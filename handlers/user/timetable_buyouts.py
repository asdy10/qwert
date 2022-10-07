import asyncio
from datetime import datetime

from aiogram.utils.callback_data import CallbackData
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from aiogram.dispatcher import FSMContext

from browser.requests_wildberries import get_brand_of_product, get_real_price
from handlers.user.buyout_menu import process_buyout
from keyboards.default.markups import *
from loader import dp, db, bot
from filters import IsUser
from states import BuyoutMenuState
from utils.db_get_info.get_set_info_db import get_graph_cid, get_template, get_all_templates_of_user, \
    get_number_of_last_graph, get_discount, create_graph
from utils.payments.ya_payment import create_link_for_payment, check_payment


@dp.message_handler(IsUser(), text=timetable_buyouts, state=BuyoutMenuState.start)
async def process_timetable_buyouts(message: Message, state: FSMContext):
    await BuyoutMenuState.timetable_buyouts.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(my_timetable, make_timetable)
    markup.add(back_message)
    await message.answer('Вы хотите создать график выкупов или посмотреть уже созданные графики?'
                         'С помощью графиков вы можете планировать выкупы в автоматическом режиме,'
                         'для этого вам нужно создать шаблон, а далее оплатить заказы', reply_markup=markup)


@dp.message_handler(IsUser(), text=back_message, state=BuyoutMenuState.timetable_buyouts)
async def process_timetable_buyouts_back(message: Message, state: FSMContext):
    await process_buyout(message, state)


@dp.message_handler(IsUser(), text=my_timetable, state=BuyoutMenuState.timetable_buyouts)
async def process_timetable_buyouts_my_timetable(message: Message, state: FSMContext):
    res = await get_graph_cid(message.from_user.id)
    if res:
        for i in res:
            temp = await get_template(i[1])
            dates = '\n'.join(i[4].split(':')[:-2])
            time_ = ':'.join(i[4].split(':')[-2:])
            await message.answer(f'<b>График №{i[2].split("_")[1]}\nДаты:</b>\n{dates}\n<b>Время: {time_}\n'
                                 f'Ссылка на товар:</b>\n{temp[2]}\n<b>Ключевая фраза:</b>\n{temp[3]}\n'
                                 f'<b>Товара в каждом заказе: {i[3]}\nПункт выдачи:</b>\n{temp[5]}')
    else:
        await message.answer('У вас пока нет созданных графиков выкупов')


@dp.message_handler(IsUser(), text=make_timetable, state=BuyoutMenuState.timetable_buyouts)
async def process_timetable_buyouts_make_timetable(message: Message, state: FSMContext):
    cid = message.from_user.id
    if await get_all_templates_of_user(cid):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(ready_message, cancel_message)
        await BuyoutMenuState.next()
        await message.answer('В конце нажмите на кнопку "Готово"')
        await message.answer('Выберите даты, в которые будут сделаны заказы')
        calendar, step = DetailedTelegramCalendar().build()
        if LSTEP[step] == 'year':
            step_ = 'год'
        elif LSTEP[step] == 'month':
            step_ = 'месяц'
        else:
            step_ = 'день'
        await bot.send_message(cid, f"Выберите {step_}", reply_markup=calendar)
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(make_template, back_message)
        await BuyoutMenuState.templates.set()
        await message.answer('У вас пока нет шаблонов.', reply_markup=markup)


@dp.callback_query_handler(IsUser(), DetailedTelegramCalendar.func(), state=BuyoutMenuState.timetable_buyouts_dates)
async def cal(c, state: FSMContext):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        if LSTEP[step] == 'year':
            step_ = 'год'
        elif LSTEP[step] == 'month':
            step_ = 'месяц'
        else:
            step_ = 'день'
        await bot.edit_message_text(f"Выберите {step_}",
                                    c.message.chat.id,
                                    c.message.message_id,
                                    reply_markup=key)
    elif result:
        async with state.proxy() as data:
            d = datetime.strptime(datetime.strftime(datetime.today(), '%Y-%m-%d'), '%Y-%m-%d')
            #print((datetime.strptime(result, '%Y-%m-%d') - d).total_seconds() > 86399)
            if (datetime.strptime(str(result), '%Y-%m-%d') - d).total_seconds() > 86399:
                try:
                    if str(result) not in data['dates']:
                        data['dates'] = f'{data["dates"]}:{result}'
                except:
                    data['dates'] = str(result)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(ready_message, cancel_message)
        await bot.send_message(c.message.chat.id, f"Вы выбрали {result}", reply_markup=markup)


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.timetable_buyouts_dates)
async def process_timetable_buyouts_dates_cancel(message: Message, state: FSMContext):
    await process_buyout(message, state)


@dp.message_handler(IsUser(), text=ready_message, state=BuyoutMenuState.timetable_buyouts_dates)
async def process_timetable_buyouts_dates_ready(message: Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            dates = data['dates']
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(back_message)
            await message.answer('Введите время по мск в формате 08:00', reply_markup=markup)
            await BuyoutMenuState.next()
        except:
            await message.answer('Выберите корректную дату, не раньше завтра')


@dp.message_handler(IsUser(), text=back_message, state=BuyoutMenuState.timetable_buyouts_time)
async def process_timetable_buyouts_time_back(message: Message, state: FSMContext):
    await BuyoutMenuState.timetable_buyouts.set()
    await process_timetable_buyouts_make_timetable(message, state)


graph_cb = CallbackData('somearg', 'idt', 'action')


@dp.message_handler(IsUser(), lambda message: message.text not in [back_message],state=BuyoutMenuState.timetable_buyouts_time)
async def process_timetable_buyouts_time(message: Message, state: FSMContext):
    date_text = message.text
    if await check_correct_time(date_text):
        async with state.proxy() as data:
            data['time'] = date_text
        markup1 = ReplyKeyboardMarkup(resize_keyboard=True)
        markup1.add(back_message)
        res = await get_all_templates_of_user(message.from_user.id)
        await message.answer('Выберите один из шаблонов ниже, по которому будет происходить заказ', reply_markup=markup1)
        for i in res:
            markup = InlineKeyboardMarkup()
            btn = InlineKeyboardButton('Выбрать шаблон', callback_data=graph_cb.new(idt=i[1], action='order'))
            markup.add(btn)
            await message.answer(f'<b>Шаблон №{i[1].split("_")[1]}</b>\n<b>Ссылка на товар:</b>\n'
                                 f'{i[2]}\n<b>Ключевая фраза:</b>\n{i[3]}\n<b>Пункт выдачи:</b>\n{i[5]}',
                                 reply_markup=markup)
        await BuyoutMenuState.next()
    else:
        await message.answer('Некорректный формат времени, введите еще раз в формате 08:00')


async def check_correct_time(date_text):
    try:
        datetime.strptime(date_text, '%H:%M')
        return True
    except:
        return False


@dp.message_handler(IsUser(), text=back_message, state=BuyoutMenuState.timetable_buyouts_dates_choice_template)
async def process_timetable_buyouts_dates_choice_template(message: Message, state: FSMContext):
    await BuyoutMenuState.timetable_buyouts.set()
    await process_timetable_buyouts_make_timetable(message, state)


@dp.callback_query_handler(IsUser(), graph_cb.filter(action='order'), state=BuyoutMenuState.timetable_buyouts_dates_choice_template)
async def process_timetable_buyouts_choice_template(query: CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        idt = callback_data['idt']
        data['idt'] = idt
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)
    await BuyoutMenuState.next()
    await query.message.answer('Сколько единиц товара выкупить?', reply_markup=markup)


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message], state=BuyoutMenuState.timetable_buyouts_count)
async def process_timetable_buyouts_count(message: Message, state: FSMContext):
    count = check_count(message.text)
    if count > 0:
        print(count)
        async with state.proxy() as data:
            data['count'] = count
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(man_acc, woman_acc)
        markup.add(cancel_message)
        await BuyoutMenuState.next()
        await message.answer('Мужской или женский аккаунт использовать для выкупа?', reply_markup=markup)

    else:
        await message.answer('Неверное количество. Введите еще раз', reply_markup=cancel_markup())


def check_count(m):
    try:
        return int(m)
    except:
        return 0


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.timetable_buyouts_count)
async def process_timetable_buyouts_count_cancel(message: Message, state: FSMContext):
    await BuyoutMenuState.timetable_buyouts.set()
    await process_timetable_buyouts_make_timetable(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [cancel_message], state=BuyoutMenuState.timetable_buyouts_male)
async def process_timetable_buyouts_male(message: Message, state: FSMContext):
    if message.text in [man_acc, woman_acc]:
        male = 'man' if message.text == man_acc else 'woman'
        async with state.proxy() as data:
            data['male'] = male
            count = data['count']
            idt = data['idt']
            dates = data['dates']
            dates = dates.replace(':', '\n')
            date_time = data['time']
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(ready_message, cancel_message)
        temp = await get_template(idt)
        await BuyoutMenuState.next()
        await message.answer(f'Проверьте правильность данных:\n<b>Даты:</b> {dates}\n<b>Время: {date_time}\n'
                             f'Шаблон №{temp[1].split("_")[1]}</b>\n'
                             f'<b>Ключевая фраза:</b> {temp[3]}\n'
                             f'<b>Количество:</b> {count}\n'
                             f'<b>Выкупает: {message.text} аккаунт</b>\n'
                             f'\n<b>Ссылка на товар:</b>\n'
                             f'{temp[2]}\n\n<b>Пункт выдачи:</b>\n{temp[5]}',
                             reply_markup=markup)
    else:
        await message.answer('Такого варианта нет')


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.timetable_buyouts_male)
async def process_timetable_buyouts_male_cancel(message: Message, state: FSMContext):
    await BuyoutMenuState.timetable_buyouts.set()
    await process_timetable_buyouts_make_timetable(message, state)


@dp.message_handler(IsUser(), text=ready_message, state=BuyoutMenuState.timetable_buyouts_dates_confirm)
async def process_timetable_buyouts_dates_confirm_ready(message: Message, state: FSMContext):
    cid = message.from_user.id
    async with state.proxy() as data:
        idt = data['idt']
        dates = data['dates']
        t = data['time']
        male = data['male']
        count = data['count']
    gid = int(await get_number_of_last_graph(cid)) + 1
    await create_graph(message.from_user.id, idt, f'{cid}_{gid}', count, f'{dates}:{t}', male)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/menu')
    await message.answer('График сохранен!', reply_markup=markup)
    await state.finish()


@dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.timetable_buyouts_dates_confirm)
async def process_timetable_buyouts_dates_confirm_cancel(message: Message, state: FSMContext):
    await BuyoutMenuState.timetable_buyouts.set()
    await process_timetable_buyouts_make_timetable(message, state)


# @dp.callback_query_handler(IsUser(), graph_cb.filter(action='order'), state=BuyoutMenuState.timetable_buyouts_dates_choice_template)
# async def process_timetable_buyouts_dates_choice_template(query: CallbackQuery, callback_data: dict, state: FSMContext):
#     async with state.proxy() as data:
#         data['idt'] = callback_data['idt']
#     await query.message.answer('Сколько единиц товара вы бы хотели выкупить в этом заказе?', reply_markup=ReplyKeyboardRemove())
#     await BuyoutMenuState.next()
#
#
# @dp.message_handler(IsUser(), state=BuyoutMenuState.timetable_buyouts_dates_count)
# async def process_timetable_buyouts_dates_count(message: Message, state: FSMContext):
#     count = await timetable_buyouts_dates_check_count(message.text)
#     if count > 0:
#         async with state.proxy() as data:
#             data['count'] = count
#             dates = data['dates']
#             dates = dates.replace(':', '\n')
#             date_time = data['time']
#             idt = data['idt']
#         markup = ReplyKeyboardMarkup(resize_keyboard=True)
#         markup.add(ready_message, cancel_message)
#         temp = await get_template(idt)
#         await message.answer(f'Проверьте правильность данных:\n<b>Даты:</b> {dates}\n<b>Время: {date_time}\n'
#                              f'Шаблон №{temp[1].split("_")[1]}</b>\n<b>Количество товара в каждом заказе: {count}</b>'
#                              f'\n<b>Ссылка на товар:</b>\n'
#                              f'{temp[2]}\n<b>Ключевая фраза:</b>\n{temp[3]}\n<b>Пункт выдачи:</b>\n{temp[5]}', reply_markup=markup)
#         await BuyoutMenuState.next()
#     else:
#         await message.answer('Некорректное количество. Введите еще раз')
#
#
# async def timetable_buyouts_dates_check_count(count_):
#     try:
#         return int(count_)
#     except:
#         return 0
#
#
# @dp.message_handler(IsUser(), text=ready_message, state=BuyoutMenuState.timetable_buyouts_dates_confirm)
# async def process_timetable_buyouts_dates_confirm_ready(message: Message, state: FSMContext):
#     await message.answer('Идет обработка заказа, сейчас будет сформирована ссылка для быстрой оплаты...')
#     cid = message.from_user.id
#     async with state.proxy() as data:
#         idt = data['idt']
#         link = (await get_template(idt))[2]
#         s = data['dates']
#         date_count = len(s.split(':'))
#         count = int(data['count']) * date_count
#         price = float((await get_real_price(link)) * count)
#         discount = float(await get_discount())
#         new_price = round(price * (100 - discount) / 100, 2)
#         data['price'] = await get_real_price(link)
#         receiver = await get_payment()
#         gid = await get_number_of_last_graph(cid) + 1
#         label = f'{cid}_{idt}_{gid}'
#         data['gid'] = f'{cid}_{gid}'
#         data['label'] = label
#
#     payment_link = await create_link_for_payment(receiver, label, new_price)
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.add(confirm_payment, cancel_message)
#     await message.answer(f'Сумма заказа: {price} рублей.\n<b>С нашей скидкой сумма: {new_price} рублей</b>'
#                          f'\nСсылка для оплаты:\n{payment_link}', reply_markup=markup)
#     await BuyoutMenuState.next()
#
#
# @dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.timetable_buyouts_dates_confirm)
# async def process_timetable_buyouts_dates_confirm_cancel(message: Message, state: FSMContext):
#     await process_buyout(message, state)
#
#
# @dp.message_handler(IsUser(), text=confirm_payment, state=BuyoutMenuState.timetable_buyouts_dates_payment)
# async def process_timetable_buyouts_dates_payment_confirm(message: Message, state: FSMContext):
#     async with state.proxy() as data:
#         label = data['label']
#         idt = data['idt']
#         dates = data['dates']
#         t = data['time']
#         count = data['count']
#         price = data['price']
#         gid = data['gid']
#     if await timetable_buyouts_check_payment(label):
#         markup = ReplyKeyboardMarkup(resize_keyboard=True)
#         markup.add('/menu')
#         await create_graph(message.from_user.id, idt, gid, count, f'{dates}:{t}', price, completed=False)
#         await message.answer('Оплата произведена успешно. Ваш заказ был принят к исполнению', reply_markup=markup)
#     else:
#         await message.answer('Заказ отменен, оплата не поступила. Если вы оплачивали, обратитесь к менеджеру')
#     await state.finish()
#
#
# async def timetable_buyouts_check_payment(label):
#     check = 0
#     while check < 60:
#         # if await check_payment(label):
#         is_pay = True
#         if is_pay:
#             return True
#         else:
#             await asyncio.sleep(60)
#             check += 1
#     return False
#
#
# @dp.message_handler(IsUser(), text=cancel_message, state=BuyoutMenuState.timetable_buyouts_dates_payment)
# async def process_timetable_buyouts_dates_payment_cancel(message: Message, state: FSMContext):
#     await process_timetable_buyouts(message, state)