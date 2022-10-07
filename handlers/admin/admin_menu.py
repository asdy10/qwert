import asyncio
import threading
import time
from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ContentType, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData
from keyboards.default.markups import admin_change_discount, admin_stat, admin_status, admin_change_payment, \
    admin_set_user_discount, admin_set_default_b_r_price, admin_set_user_b_r_price, admin_set_status_buyout, \
    admin_get_buyout_idx, admin_get_user, admin_set_ref_bonus, admin_menu_markup, admin_add_proxy, back_markup, \
    cancel_markup
from states import AdminState, AddProxyState
from aiogram.types.chat import ChatActions
from handlers.user.menu import settings
from loader import dp, db, bot
from filters import IsAdmin
from utils.connect_tg_with_browser.aggregator import agg
from utils.db_get_info.get_set_info_db import set_discount, set_payment_default, set_token_default, set_discount_cid, \
    get_all_buyouts, get_all_reviews, set_b_r_price_default, set_b_r_price, set_status_of_buyout, get_buyout_idx, \
    get_user_cid, get_all_buyouts_of_user, get_referals_cid, set_ref_percent_cid, create_proxy, get_all_buyouts_new
from utils.notices.graph_notice import get_graph_notice

"""discount"""


@dp.message_handler(IsAdmin(), commands='menu')
async def admin_menu(message: Message):
    await message.answer('Меню', reply_markup=admin_menu_markup())


@dp.message_handler(IsAdmin(), text=admin_change_discount)
async def process_change_discount(message: Message, state: FSMContext):
    await AdminState.set_discount.set()
    await message.answer('Введите скидку')


@dp.message_handler(IsAdmin(), state=AdminState.set_discount)
async def process_set_discount(message: Message, state: FSMContext):
    dis = message.text
    if await check_discount(dis) > 0:
        await set_discount(dis)
        await message.answer('Скидка изменена.')
        await state.finish()


async def check_discount(dis):
    try:
        return int(dis)
    except:
        return 0


"""status"""


@dp.message_handler(IsAdmin(), text=admin_status)
async def process_get_status(message: Message, state: FSMContext):
    await message.answer(await agg.get_status())


"""statistic"""


@dp.message_handler(IsAdmin(), text=admin_stat)
async def process_get_statistic(message: Message, state: FSMContext):
    all_buyouts = await get_all_buyouts()
    sum_day = 0
    count_day = 0
    sum_week = 0
    count_week = 0
    sum_month = 0
    count_month = 0
    now = datetime.now()
    for i in all_buyouts:
        if (now - datetime.strptime(i[7], '%d.%m.%Y %H:%M:%S')).total_seconds() < 86400:
            count_day += 1
            sum_day += i[11] - i[5]
        if (now - datetime.strptime(i[7], '%d.%m.%Y %H:%M:%S')).total_seconds() < 604800:
            count_week += 1
            sum_week += i[11] - i[5]
        if (now - datetime.strptime(i[7], '%d.%m.%Y %H:%M:%S')).total_seconds() < 2592000:
            count_month += 1
            sum_month += i[11] - i[5]
    all_reviews = await get_all_reviews()
    count_reviews_day = 0
    count_reviews_week = 0
    count_reviews_month = 0
    now = datetime.now()
    for i in all_reviews:
        if (now - datetime.strptime(i[3], '%d.%m.%Y %H:%M:%S')).total_seconds() < 86400:
            count_reviews_day += 1
        if (now - datetime.strptime(i[3], '%d.%m.%Y %H:%M:%S')).total_seconds() < 604800:
            count_reviews_week += 1
        if (now - datetime.strptime(i[3], '%d.%m.%Y %H:%M:%S')).total_seconds() < 2592000:
            count_reviews_month += 1
    s = f'Статистика\nЗа день: {count_day} выкупов с профитом {round(sum_day)}р и {count_reviews_day} отзывов\n' \
        f'За неделю: {count_week} выкупов с профитом {round(sum_week)}р и {count_reviews_week} отзывов\n' \
        f'За месяц: {count_month} выкупов с профитом {round(sum_month)}р и {count_reviews_month} отзывов\n'
    await message.answer(s)


"""payment"""


@dp.message_handler(IsAdmin(), text=admin_change_payment)
async def process_change_payment(message: Message, state: FSMContext):
    await AdminState.set_payment.set()
    await message.answer('Введите номер карты')


@dp.message_handler(IsAdmin(), text=admin_change_payment, state=AdminState.set_payment)
async def process_set_payment(message: Message, state: FSMContext):
    await AdminState.next()
    payment = message.text
    await set_payment_default(payment)
    await message.answer('Введите токен')


@dp.message_handler(IsAdmin(), text=admin_change_payment, state=AdminState.set_token)
async def process_set_token(message: Message, state: FSMContext):
    await state.finish()
    token = message.text
    await set_token_default(token)
    await message.answer('Метод оплаты изменен')


"""run bot"""


async def run_queue_buyout_make_task():
    while True:
        try:
            await agg.queue_buyout_make_task()
            await asyncio.sleep(10)
        except Exception as e:
            print(e)


async def run_queue_review_make_task():
    while True:
        try:
            await agg.queue_review_make_task()
            await asyncio.sleep(10)
        except Exception as e:
            print(e)


async def run_add_buyout_from_graph_in_queue():
    while True:
        try:
            await agg.add_buyout_from_graph_in_queue()
            await asyncio.sleep(60)
        except Exception as e:
            print(e)


def run_add_buyout_from_graph_in_queue_not_async():
    while True:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(agg.add_buyout_from_graph_in_queue())
            time.sleep(60)
        except Exception as e:
            print(3, e)


async def run_update_order_status():
    await asyncio.sleep(86400)
    while True:
        try:
            res = await agg.update_order_status()
            if res:
                await asyncio.sleep(86400)
            else:
                await asyncio.sleep(60)
        except Exception as e:
            print(e)


def get_is_work():
    t = time.strftime('%X')
    h, m, s = t.split(':')
    return h == '23' and m == '59'


def run_update_order_status_not_async():
    time.sleep(0)
    while True:
        if get_is_work():
            print('START UPDATE', time.strftime('%X'))
            try:
                agg.update_order_status_not_async()
                time.sleep(3600)
            except Exception as e:
                print(e)
                time.sleep(60)
        else:
            time.sleep(10)


async def run_add_after_error_in_queue():
    buyouts2 = await get_all_buyouts_new()
    for b in buyouts2:
        cid, idx, link, keywords, count, address, date_buyouts, status, review, bid, _, _ = b
        await agg.make_buyout_task(bid, idx, keywords, link, address, count)
        # set_status_of_buyout(idx, 'new')
    while True:
        try:
            await agg.add_after_error_in_queue()
            await asyncio.sleep(60)
        except Exception as e:
            print(e)


def run_add_after_error_in_queue_not_async():
    while True:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(agg.add_after_error_in_queue())
            time.sleep(600)
        except Exception as e:
            print(2, e)


async def check_and_send_notice():
    while True:
        try:
            data = await get_graph_notice()
            for i in data:
                await bot.send_message(i, data[i])
            await asyncio.sleep(60)
        except Exception as e:
            print(e)
            await asyncio.sleep(60)


#
# @dp.message_handler(IsAdmin(), commands='run_bot')
# async def run_bot(message: Message):
#     await message.answer('Бот запущен')
#     count_thread = 5
#     await agg.set_bids()
#
#     for i in range(count_thread):
#         asyncio.create_task(run_queue_buyout_make_task())
#         asyncio.create_task(run_queue_review_make_task())
#     asyncio.create_task(check_and_send_notice())
#     asyncio.create_task(run_update_order_status())
#     asyncio.create_task(run_add_after_error_in_queue())

        #asyncio.create_task(run_add_buyout_from_graph_in_queue(agg))


@dp.message_handler(IsAdmin(), text=admin_add_proxy)
async def process_add_proxy(message: Message, state: FSMContext):
    await message.answer('Введите прокси в формате login:pass@ip:port', reply_markup=cancel_markup())
    await AddProxyState.proxy.set()


def check_proxy(proxy: str):
    try:
        a, b = proxy.split('@')
        return a.split(':'), b.split(':')
    except:
        return 0, 0, 0, 0


@dp.message_handler(IsAdmin(), state=AddProxyState.proxy)
async def process_add_proxy_check(message: Message, state: FSMContext):
    [a, b], [c, d] = check_proxy(message.text)
    if [a, b, c, d] != [0, 0, 0, 0]:
        async with state.proxy() as data:
            data['proxy'] = message.text
        await message.answer('Введите ключ прокси')
        await AddProxyState.next()
    else:
        await message.answer('Формат не верный, операция отменена', reply_markup=admin_menu_markup())
        await state.finish()


@dp.message_handler(IsAdmin(), state=AddProxyState.proxy_key)
async def process_add_proxy_key(message: Message, state: FSMContext):
    if len(message.text) < 20:
        await message.answer('Формат не верный, операция отменена', reply_markup=admin_menu_markup())
        await state.finish()
    else:
        async with state.proxy() as data:
            proxy = data['proxy']
        create_proxy(proxy, message.text)
        await message.answer('Прокси сохранена')
        await state.finish()


"""set user discount"""


@dp.message_handler(IsAdmin(), text=admin_set_user_discount)
async def process_change_user_discount(message: Message, state: FSMContext):
    await AdminState.get_user_id.set()
    await message.answer('Введите id пользователя')


@dp.message_handler(IsAdmin(), state=AdminState.get_user_id)
async def process_get_user_id(message: Message, state: FSMContext):
    await AdminState.next()
    cid = int(message.text)
    async with state.proxy() as data:
        data['cid'] = cid
    await message.answer('Введите СПП для пользователя')


@dp.message_handler(IsAdmin(), state=AdminState.set_user_discount)
async def process_set_user_discount(message: Message, state: FSMContext):

    dis = float(message.text)
    async with state.proxy() as data:
        cid = data['cid']
    await set_discount_cid(cid, dis)
    await message.answer('СПП изменена')
    await state.finish()


"""Buyout, review price"""
#admin_set_default_b_r_price, admin_set_user_b_r_price


@dp.message_handler(IsAdmin(), text=admin_set_default_b_r_price)
async def process_set_default_b_r_price(message: Message, state: FSMContext):
    await AdminState.set_buyout_price.set()
    await message.answer('Введите стоимость выкупа')


@dp.message_handler(IsAdmin(), text=admin_set_user_b_r_price)
async def process_set_user_b_r_price(message: Message, state: FSMContext):
    await AdminState.set_b_r_price_user_id.set()
    await message.answer('Введите id пользователя')


@dp.message_handler(IsAdmin(), state=AdminState.set_b_r_price_user_id)
async def process_set_b_r_price_user_id(message: Message, state: FSMContext):
    await AdminState.next()
    cid = int(message.text)
    async with state.proxy() as data:
        data['cid'] = cid
    await message.answer('Введите стоимость выкупа')


@dp.message_handler(IsAdmin(), state=AdminState.set_buyout_price)
async def process_set_buyout_price(message: Message, state: FSMContext):
    await AdminState.next()
    async with state.proxy() as data:
        data['b_price'] = message.text
    await message.answer('Введите стоимость отзыва')


@dp.message_handler(IsAdmin(), state=AdminState.set_review_price)
async def process_set_review_price(message: Message, state: FSMContext):
    cid = 0
    async with state.proxy() as data:
        b_price = data['b_price']
        r_price = message.text
        try:
            cid = data['cid']
        except:
            pass
    if cid == 0:
        await set_b_r_price_default(b_price, r_price)
    else:
        await set_b_r_price(cid, b_price, r_price)
    await message.answer('Изменено')
    await state.finish()


"""Set status buyout"""


@dp.message_handler(IsAdmin(), text=admin_set_status_buyout)
async def process_admin_set_status_buyout(message: Message, state: FSMContext):
    await AdminState.set_status_buyout_idx.set()
    await message.answer('Введите idx заказа')


@dp.message_handler(IsAdmin(), state=AdminState.get_user_id)
async def process_get_user_id(message: Message, state: FSMContext):
    await AdminState.next()
    async with state.proxy() as data:
        data['idx'] = message.text
    await message.answer('Введите статус')


@dp.message_handler(IsAdmin(), state=AdminState.set_status_buyout_status)
async def process_set_user_discount(message: Message, state: FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
    await set_status_of_buyout(idx, message.text)
    await message.answer('Статус изменен')
    await state.finish()


"""Get status buyout idx"""


@dp.message_handler(IsAdmin(), text=admin_get_buyout_idx)
async def process_admin_get_buyout_idx(message: Message, state: FSMContext):
    await AdminState.get_buyout_idx.set()
    await message.answer('Введите idx заказа')


@dp.message_handler(IsAdmin(), state=AdminState.get_buyout_idx)
async def process_get_buyout_idx(message: Message, state: FSMContext):
    idx = message.text
    i = await get_buyout_idx(idx)
    await message.answer(f'<b>Заказ №{i[1]}</b>\n<b>Ссылка на товар:</b>\n{i[2]}\n'
                         f'<b>Количество:</b> {i[4]}\n<b>Стоимость для бота: </b>{i[5]}\n'
                         f'<b>Стоимость для пользователя: </b>{i[11]}\n<b>Ключевая фраза:</b>\n'
                         f'{i[3]}\n<b>Пункт выдачи:</b>\n{i[6]}\n<b>Дата выкупа:</b> {i[7]}\n'
                         f'<b>Статус:</b> {i[8]}\nbid={i[10]}\nОтзыв={i[9]}')
    await state.finish()


@dp.message_handler(IsAdmin(), text=admin_get_user)
async def process_admin_get_buyout_idx(message: Message, state: FSMContext):
    await AdminState.get_cid.set()
    await message.answer('Введите cid пользователя')


@dp.message_handler(IsAdmin(), state=AdminState.get_cid)
async def process_get_buyout_buyout_idx(message: Message, state: FSMContext):
    cid = message.text
    s = str(await get_user_cid(cid))
    s += '\nВЫКУПЫ\n'
    for i in await get_all_buyouts_of_user(cid):
        s += f'{i}\n'
    s += '\nРЕФЕРАЛЬНЫЙ БОНУС\n'
    for i in await get_referals_cid(cid):
        s += f'{i}\n'
    await message.answer(s)
    await state.finish()


"""Set referal bonus user cid"""


@dp.message_handler(IsAdmin(), text=admin_set_ref_bonus)
async def process_admin_set_ref_bonus(message: Message, state: FSMContext):
    await AdminState.set_ref_cid.set()
    await message.answer('Введите cid пользователя')


@dp.message_handler(IsAdmin(), state=AdminState.set_ref_cid)
async def process_set_ref_cid(message: Message, state: FSMContext):
    await AdminState.next()
    async with state.proxy() as data:
        data['cid'] = message.text
    await message.answer('Введите реферальный бонус')


@dp.message_handler(IsAdmin(), state=AdminState.set_ref_bonus)
async def process_set_ref_bonus(message: Message, state: FSMContext):
    async with state.proxy() as data:
        cid = data['cid']
    bonus = message.text
    await set_ref_percent_cid(cid, bonus)
    await message.answer('Изменено')
    await state.finish()
