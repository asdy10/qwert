import asyncio

# from handlers.user.templates_wb import save_new_template
from datetime import datetime

from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from browser.requests_wildberries import check_link, get_real_price
from handlers.user.buyout_menu import process_buyout
from handlers.user.timetable_buyouts import process_timetable_buyouts
from keyboards.default.markups import *
from loader import dp, db, bot, images_buyout
from filters import IsUser
from states import BuyoutMenuState
from utils.connect_tg_with_browser.aggregator import agg
from utils.db_get_info.get_set_info_db import get_discount, get_count_of_buyouts_user, create_buyout, \
    create_buyout_template, get_number_of_last_template, get_buyouts, set_buyouts, get_browser_bid, get_discount_cid, \
    is_user_exist, get_balance, set_balance, get_user_cid, get_discount_browser, get_ref_percent_cid, get_ref_bonus_cid, \
    set_ref_bonus_cid, create_referal, get_referer, get_last_num_buyout_user
from utils.payments.ya_payment import create_link_for_payment, check_payment
from utils.yamaps.ya_maps import get_address_and_photo, get_coor_wb_vpz, get_address_and_photo_not_async


@dp.message_handler(IsUser(), text=make_buyout_btn, state=BuyoutMenuState.start)
async def process_make_buyout(message: Message, state: FSMContext):
    if await get_buyouts(message.from_user.id) > 0:
        await BuyoutMenuState.make_buyout_link.set()
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_message)
        await message.answer('Пришлите ссылку или артикул товара, который нужно выкупить', reply_markup=markup)
    else:
        await message.answer('Для того чтобы заказать выкуп, необходимо купить "Выкуп" в разделе баланса')


@dp.message_handler(IsUser(), text=back_message, state=BuyoutMenuState.make_buyout_link)
async def process_make_buyout_back(message: Message, state: FSMContext):
    await process_buyout(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [back_message], state=BuyoutMenuState.make_buyout_link)
async def process_make_buyout_link(message: Message, state: FSMContext):
    link = message.text
    if len(link) > 15:
        if await check_link(link):
            pid = link.split('/')[4]
            link = f'https://www.wildberries.ru/catalog/{pid}/detail.aspx?targetUrl=EX'
            async with state.proxy() as data:
                data['link'] = link
            await message.answer('Введите ключевой запрос', reply_markup=cancel_markup())
            await BuyoutMenuState.next()
        else:
            await message.answer('Неверная ссылка')
    else:
        url = f'https://www.wildberries.ru/catalog/{link}/detail.aspx?targetUrl=EX'
        if await check_link(url):
            async with state.proxy() as data:
                data['link'] = url
            await message.answer('Введите ключевой запрос', reply_markup=cancel_markup())
            await BuyoutMenuState.next()
        else:
            await message.answer('Артикул не найден')


@dp.message_handler(IsUser(), text=back_message, state=BuyoutMenuState.make_buyout_link)
async def process_make_buyout_link_back(message: Message, state: FSMContext):
    await process_buyout(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message], state=BuyoutMenuState.make_buyout_keywords)
async def process_make_buyout_keywords(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['keywords'] = message.text
    await message.answer('Сколько единиц товара выкупить?', reply_markup=cancel_markup())
    await BuyoutMenuState.next()


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.make_buyout_keywords)
async def process_make_buyout_keywords_cancel_message(message: Message, state: FSMContext):
    await process_buyout(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message], state=BuyoutMenuState.make_buyout_count)
async def process_make_buyout_count(message: Message, state: FSMContext):
    count = await make_buyout_check_count(message.text)
    if count > 0:
        async with state.proxy() as data:
            data['count'] = count
        await message.answer('Введите адрес пункта выдачи', reply_markup=addresses_markup())
        await BuyoutMenuState.next()
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(cancel_message)
        await message.answer('Неверное количество. Введите еще раз', reply_markup=markup)


async def make_buyout_check_count(count):
    try:
        return int(count)
    except:
        return 0


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.make_buyout_count)
async def process_make_buyout_count_cancel(message: Message, state: FSMContext):
    await process_make_buyout(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message],
                    state=BuyoutMenuState.make_buyout_address)
async def process_make_buyout_address(message: Message, state: FSMContext):
    user_address = message.text
    await message.answer('Подождите, адрес проверяется...')
    address, image, y, x = get_address_and_photo_not_async(user_address)

    coor_arr = get_coor_wb_vpz()
    find = False
    if [round(float(x), 2), round(float(y), 2)] in coor_arr:
        find = True
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if find:
        async with state.proxy() as data:
            data['address'] = address
        markup.add(confirm_message, change_message)
        markup.add(cancel_message)
        await message.answer_photo(photo=image,
                                   caption=f'Мы нашли ПВЗ по адресу: <b>"{address}".</b> Это верный адрес ПВЗ?',
                                   reply_markup=markup)
        await BuyoutMenuState.next()
    else:
        if address != '':
            markup.add(cancel_message)
            await message.answer_photo(photo=image, caption=f'По адресу <b>"{address}"</b> нет ПВЗ. '
                                       f'Проверьте правильность написания адреса и оправьте его еще раз',
                                       reply_markup=markup)
        else:
            markup.add(cancel_message)
            await message.answer('Этот адрес не найден. Проверьте '
                                 'правильность написания адреса и оправьте его еще раз', reply_markup=markup)


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.make_buyout_address)
async def process_make_buyout_address_cancel(message: Message, state: FSMContext):
    await process_make_buyout(message, state)


@dp.message_handler(IsUser(), text=confirm_message, state=BuyoutMenuState.make_buyout_address_confirm)
async def process_make_buyout_address_confirm(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(man_acc, woman_acc)
    markup.add(cancel_message)
    await BuyoutMenuState.next()
    await message.answer('Мужской или женский аккаунт использовать для выкупа?', reply_markup=markup)


@dp.message_handler(IsUser(), text=change_message, state=BuyoutMenuState.make_buyout_address_confirm)
async def process_make_buyout_address_change(message: Message, state: FSMContext):
    await BuyoutMenuState.make_buyout_address.set()
    await message.answer('Введите адрес ПВЗ еще раз', reply_markup=addresses_markup())


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.make_buyout_address_confirm)
async def process_make_buyout_address_back(message: Message, state: FSMContext):
    await process_make_buyout(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message], state=BuyoutMenuState.make_buyout_male)
async def process_make_buyout_male(message: Message, state: FSMContext):
    if message.text in [man_acc, woman_acc]:
        male = 'man' if message.text == man_acc else 'woman'
        async with state.proxy() as data:
            address = data['address']
            data['male'] = male
            link = data['link']
            keywords = data['keywords']
            count = data['count']
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(confirm_message, change_message)
        await BuyoutMenuState.next()
        await message.answer(f'Отлично, подтвердите его правильность заказа:\n'
                             f'Ссылка на товар: {link}\nПоисковая фраза: {keywords}\n'
                             f'Количество: {count}\nВыкупает {message.text} аккаунт\nАдрес ПВЗ: {address}',
                             reply_markup=markup)
    else:
        await message.answer('Такого варианта нет')


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.make_buyout_male)
async def process_make_buyout_male_cancel(message: Message, state: FSMContext):
    await process_make_buyout(message, state)


@dp.message_handler(IsUser(), text=confirm_message, state=BuyoutMenuState.make_buyout_confirm)
async def process_make_buyout_confirm(message: Message, state: FSMContext):

    await BuyoutMenuState.next()
    cid = message.from_user.id
    async with state.proxy() as data:
        link = data['link']
        keywords = data['keywords']
        address = data['address']
        count = int(data['count'])
        male = data['male']
    for i in range(count):
        bid = await agg.get_bid_no_used(cid, male)
        idx = f'{cid}_{int(get_last_num_buyout_user(cid)) + 1}'
        await create_buyout(cid, idx, link, keywords, 1, address, datetime.today().strftime("%d.%m.%Y %H:%M:%S"), 'new', 0, bid)
        await agg.make_buyout_task(bid, idx, keywords, link, address, 1)
        old_x = await get_buyouts(cid)
        await set_buyouts(cid, old_x - 1)
    #ref_id = await get_referer(cid)
    # if ref_id:
    #     b, _ = await get_b_r_price(cid)
    #     b = int(b)
    #     ref_percent = float(await get_ref_percent_cid(ref_id))
    #     ref_bonus = round(b * ref_percent / 100)
    #     ref_balance = round(float(await get_ref_bonus_cid(ref_id)))
    #     await set_ref_bonus_cid(ref_id, ref_bonus + ref_balance)
    #     await create_referal(ref_id, idx, ref_bonus, datetime.today().strftime("%d.%m.%Y %H:%M:%S"))
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(send_buyout_in_template, timetable_buyouts)
    markup.add(back_message)
    await message.answer('Выкуп отправлен в работу. Происходит поиск товара по ключевому слову, '
                         'через время придет qr код на оплату. Время ожидания 7-20 минут(зависит от занимаемой позиции) '
                         '\nВы можете продолжить делать выкупы.', reply_markup=markup)


@dp.message_handler(IsUser(), text=change_message, state=BuyoutMenuState.make_buyout_confirm)
async def process_make_buyout_change(message: Message, state: FSMContext):
    await process_make_buyout(message, state)


@dp.message_handler(IsUser(), text=send_buyout_in_template, state=BuyoutMenuState.make_buyout_after_payment)
async def process_make_buyout_after_payment_send_buyout_in_template(message: Message, state: FSMContext):
    async with state.proxy() as data:
        link = data['link']
        keywords = data['keywords']
        count_products = data['count']
        address = data['address']
    cid = message.from_user.id
    idt = f'{cid}_{int(await get_number_of_last_template(cid)) + 1}'
    await create_buyout_template(cid, idt, link, keywords, count_products, address, datetime.today().strftime("%d.%m.%Y %H:%M:%S"))
    await message.answer('Выкуп добавлен в шаблоны!')
    await state.finish()


@dp.message_handler(IsUser(), text=timetable_buyouts, state=BuyoutMenuState.make_buyout_after_payment)
async def process_make_buyout_after_payment_make_timetable_buyout(message: Message, state: FSMContext):
    await process_timetable_buyouts(message, state)


@dp.message_handler(IsUser(), text=back_message, state=BuyoutMenuState.make_buyout_after_payment)
async def process_make_buyout_after_payment_check_delivery(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(buyout, reviews)
    markup.add(balance, info)
    await message.answer('Выберите пункт главного меню, который вас интересует👇', reply_markup=markup)
    await state.finish()

