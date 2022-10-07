from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery
from aiogram.dispatcher import FSMContext

from browser.requests_wildberries import check_link, get_real_price
from handlers.user.buyout_menu import process_buyout
from handlers.user.make_buyout import process_make_buyout_confirm
from keyboards.default.markups import *
from loader import dp, db, bot
from filters import IsUser
from states import BuyoutMenuState
from utils.db_get_info.get_set_info_db import get_all_templates_of_user, delete_template, get_template, \
    create_buyout_template, get_number_of_last_template, get_buyouts
from aiogram.utils.callback_data import CallbackData

from utils.yamaps.ya_maps import get_address_and_photo, get_coor_wb_vpz


@dp.message_handler(IsUser(), text=templates, state=BuyoutMenuState.start)
async def process_templates(message: Message, state: FSMContext):
    await BuyoutMenuState.templates.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(my_templates, make_template)
    markup.add(back_message)
    await message.answer('Вы хотите создать шаблон выкупов или посмотреть уже '
                         'созданные шаблоны? С помощью шаблонов вы '
                         'сможете делать выкупы в один клик', reply_markup=markup)


@dp.message_handler(IsUser(), text=back_message, state=BuyoutMenuState.templates)
async def process_templates_back(message: Message, state: FSMContext):
    await process_buyout(message, state)


'''my_templates start'''

template_cb = CallbackData('somearg', 'idt', 'action')


@dp.message_handler(IsUser(), text=my_templates, state=BuyoutMenuState.templates)
async def process_my_templates(message: Message, state: FSMContext):

    res = await get_all_templates_of_user(message.from_user.id)
    if res:
        for i in res:
            markup = InlineKeyboardMarkup()
            btn = InlineKeyboardButton('Заказать', callback_data=template_cb.new(idt=i[1], action='order'))
            btn2 = InlineKeyboardButton('Удалить шаблон', callback_data=template_cb.new(idt=i[1], action='delete'))
            markup.add(btn)
            markup.add(btn2)
            await message.answer(f'<b>Шаблон №{i[1].split("_")[1]}</b>\n<b>Ссылка на товар:</b>\n'
                                 f'{i[2]}\n<b>Ключевая фраза:</b>\n{i[3]}\n<b>Пункт выдачи:</b>\n{i[5]}',
                                 reply_markup=markup)

    else:
        await message.answer('У вас пока нет шаблонов')


@dp.callback_query_handler(IsUser(), template_cb.filter(action='order'), state=BuyoutMenuState.templates)
async def process_my_templates_order(query: CallbackQuery, callback_data: dict, state: FSMContext):
    if await get_buyouts(query.message.chat.id) > 0:
        async with state.proxy() as data:
            data['idt'] = callback_data['idt']
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(cancel_message)
        await query.message.answer('Сколько единиц товара вы бы хотели выкупить в этом заказе?', reply_markup=markup)
        await BuyoutMenuState.my_template_make_buyout.set()
    else:
        await query.message.answer('Для того чтобы заказать выкуп, необходимо купить "Выкуп" в разделе баланса')


@dp.callback_query_handler(IsUser(), template_cb.filter(action='delete'), state=BuyoutMenuState.templates)
async def process_my_templates_delete(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await delete_template(callback_data['idt'])
    await query.message.delete()


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message], state=BuyoutMenuState.my_template_make_buyout)
async def process_my_template_make_buyout(message: Message, state: FSMContext):
    count = await my_template_make_buyout_check_count(message.text)
    if count > 0:
        async with state.proxy() as data:
            data['count'] = count
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(man_acc, woman_acc)
        markup.add(cancel_message)
        await BuyoutMenuState.next()
        await message.answer('Мужской или женский аккаунт использовать для выкупа?', reply_markup=markup)
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(cancel_message)
        await message.answer('Неверное количество. Введите еще раз', reply_markup=markup)


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.my_template_make_buyout)
async def process_my_template_make_buyout_cancel(message: Message, state: FSMContext):
    await BuyoutMenuState.templates.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(my_templates, make_template)
    markup.add(back_message)
    await message.answer('Выберите интересующий вас пункт', reply_markup=markup)


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message], state=BuyoutMenuState.my_template_make_buyout_male)
async def process_my_template_make_buyout_male(message: Message, state: FSMContext):

    if message.text in [man_acc, woman_acc]:
        male = 'man' if message.text == man_acc else 'woman'
        async with state.proxy() as data:
            data['male'] = male
            count = data['count']
            idt = data['idt']
            temp = await get_template(idt)
            data['address'] = temp[5]
            data['link'] = temp[2]
            data['keywords'] = temp[3]

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(confirm_message, cancel_message)
        await BuyoutMenuState.next()
        await message.answer(f'Отлично, подтвердите правильность заказа:\n'
                             f'Ссылка на товар: {temp[2]}\nПоисковая фраза: {temp[3]}\n'
                             f'Количество: {count}\nВыкупает {message.text} аккаунт\nАдрес пвз: {temp[5]}',
                             reply_markup=markup)
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(cancel_message)
        await message.answer('Такого варианта нет', reply_markup=markup)


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.my_template_make_buyout_male)
async def process_my_template_make_buyout_male_cancel(message: Message, state: FSMContext):
    await BuyoutMenuState.templates.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(my_templates, make_template)
    markup.add(back_message)
    await message.answer('Выберите интересующий вас пункт', reply_markup=markup)


async def my_template_make_buyout_check_count(count):
    try:
        return int(count)
    except:
        return 0


@dp.message_handler(IsUser(), text=confirm_message, state=BuyoutMenuState.my_template_make_buyout_confirm)
async def process_my_template_make_buyout_confirm(message: Message, state: FSMContext):
    await BuyoutMenuState.make_buyout_confirm.set()
    await process_make_buyout_confirm(message, state)


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.my_template_make_buyout_confirm)
async def process_my_template_make_buyout_confirm_cancel(message: Message, state: FSMContext):
    await process_my_template_make_buyout_cancel(message, state)

'''my_templates end'''

'''make_templates start'''


@dp.message_handler(IsUser(), text=make_template, state=BuyoutMenuState.templates)
async def process_make_template(message: Message, state: FSMContext):
    await BuyoutMenuState.make_templates_link.set()
    await message.answer('Пришлите ссылку на товар', reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=BuyoutMenuState.make_templates_link)
async def process_make_template_back(message: Message, state: FSMContext):
    await process_templates(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [back_message],
                    state=BuyoutMenuState.make_templates_link)
async def process_make_template_link(message: Message, state: FSMContext):
    link = message.text
    if await check_link(link):
        async with state.proxy() as data:
            data['link'] = link
        await message.answer('Введите ключевой запрос', reply_markup=ReplyKeyboardRemove())
        await BuyoutMenuState.next()

    else:
        await message.answer('Неверная ссылка')


@dp.message_handler(IsUser(), state=BuyoutMenuState.make_templates_keywords)
async def process_make_templates_keywords(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['keywords'] = message.text
    await message.answer('Выберите адрес пункта выдачи или введите новый', reply_markup=addresses_markup())
    await BuyoutMenuState.next()


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message],
                    state=BuyoutMenuState.make_templates_address)
async def process_make_templates_address(message: Message, state: FSMContext):
    user_address = message.text
    await message.answer('Подождите, адрес проверяется...')
    address, image, y, x = await get_address_and_photo(user_address)

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
                                   caption=f'Мы нашли ПВЗ по адресу <b>"{address}".</b> Это верный адрес ПВЗ?',
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


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.make_templates_address)
async def process_make_template_address_cancel(message: Message, state: FSMContext):
    await process_make_template(message, state)


@dp.message_handler(IsUser(), text=confirm_message, state=BuyoutMenuState.make_templates_address_confirm)
async def process_make_templates_address_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        address = data['address']
        link = data['link']
        keywords = data['keywords']
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(confirm_message, change_message)
    await BuyoutMenuState.next()
    await message.answer(f'Отлично, шаблон почти готов. Подтвердите его правильность:\n'
                         f'Ссылка на товар: {link}\nПоисковая фраза: {keywords}\nАдрес пвз: {address}',
                         reply_markup=markup)


@dp.message_handler(IsUser(), text=change_message, state=BuyoutMenuState.make_templates_address_confirm)
async def process_make_templates_address_change(message: Message, state: FSMContext):
    await BuyoutMenuState.make_templates_address.set()
    await message.answer('Введите адрес ПВЗ еще раз', reply_markup=addresses_markup())


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.make_templates_address_confirm)
async def process_make_templates_address_back(message: Message, state: FSMContext):
    await process_make_template(message, state)


@dp.message_handler(IsUser(), text=confirm_message, state=BuyoutMenuState.make_templates_confirm)
async def process_make_templates_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        address = data['address']
        link = data['link']
        keywords = data['keywords']
    cid = message.from_user.id
    idt = f'{cid}_{int(await get_number_of_last_template(cid)) + 1}'
    await create_buyout_template(cid, idt, link, keywords, 1, address, 'no date')
    await message.answer('Шаблон добавлен!')
    await process_templates(message, state)


@dp.message_handler(IsUser(), text=change_message, state=BuyoutMenuState.make_templates_confirm)
async def process_make_templates_change(message: Message, state: FSMContext):
    await process_make_template(message, state)


'''make_templates end'''
