import asyncio
from datetime import datetime

from keyboards.default.markups import *
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from filters import IsUser
from states import BalanceState
from utils.db_get_info.get_set_info_db import get_balance, set_balance, get_buyouts, get_reviews, set_buyouts, \
    set_reviews, get_payment_default, get_token_default
from utils.payments.ya_payment import create_link_for_payment, check_payment


@dp.message_handler(IsUser(), text=balance)
async def process_balance(message: Message, state: FSMContext):
    await BalanceState.start.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(buy_buyouts, buy_reviews)
    markup.add(add_balance, back_message)
    cid = message.from_user.id
    balance_ = await get_balance(cid)
    available_buyouts = await get_buyouts(cid)
    available_reviews = await get_reviews(cid)
    await message.answer(f'💰Баланс: {balance_}\nДоступные выкупы: {available_buyouts}\n'
                         f'Доступные отзывы: {available_reviews}\n____________\n'
                         'Приглашайте друзей и получайте 5% с каждой их покупки!\n'
                         '🔗Ваша уникальная инвайт-ссылка на WB bot: '
                         f'https://t.me/wbforsellersbot?start={cid}', reply_markup=markup, disable_web_page_preview=True)


@dp.message_handler(IsUser(), text=back_message, state=BalanceState.start)
async def process_balance_back(message: Message, state: FSMContext):
    await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(buyout, reviews)
    markup.add(balance, info)
    await message.answer('Меню', reply_markup=markup)


@dp.message_handler(IsUser(), text=buy_buyouts, state=BalanceState.start)
async def process_balance_buy_buyouts(message: Message, state: FSMContext):
    await BalanceState.balance_buyout_count.set()
    await message.answer('Выберите сколько купить выкупов', reply_markup=await buyout_markup(message.from_user.id))


@dp.message_handler(IsUser(), text=buy_reviews, state=BalanceState.start)
async def process_balance_buy_reviews(message: Message, state: FSMContext):
    await BalanceState.balance_reviews_count.set()
    await message.answer('Выберите сколько купить отзывов', reply_markup=await review_markup(message.from_user.id))


@dp.message_handler(IsUser(), text=add_balance, state=BalanceState.start)
async def process_add_balance(message: Message, state: FSMContext):
    await BalanceState.add_balance_count.set()
    await message.answer('Выберите на сколько пополнить баланс', reply_markup=payment_markup())


@dp.message_handler(IsUser(), lambda message: message.text not in [back_message], state=BalanceState.balance_buyout_count)
async def process_balance_buyout_count(message: Message, state: FSMContext):
    count = message.text
    async with state.proxy() as data:
        data['count'] = count
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(make_payment, back_message)
    await message.answer(f'Ваш выбор:\n{count}', reply_markup=markup)
    await BalanceState.next()


@dp.message_handler(IsUser(), text=back_message, state=BalanceState.balance_buyout_count)
async def process_balance_buyout_count_back(message: Message, state: FSMContext):
    await process_balance_back(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [back_message], state=BalanceState.balance_reviews_count)
async def process_balance_reviews_count(message: Message, state: FSMContext):
    count = message.text
    async with state.proxy() as data:
        data['count'] = count
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(make_payment, back_message)
    await message.answer(f'Ваш выбор:\n{count}', reply_markup=markup)
    await BalanceState.next()


@dp.message_handler(IsUser(), text=back_message, state=BalanceState.balance_reviews_count)
async def process_balance_reviews_count_back(message: Message, state: FSMContext):
    await process_balance_back(message, state)


@dp.message_handler(IsUser(), lambda message: message.text not in [back_message], state=BalanceState.add_balance_count)
async def process_add_balance_count(message: Message, state: FSMContext):
    count = message.text
    async with state.proxy() as data:
        data['count'] = count.split()[1].split('р')[0]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(make_payment, back_message)
    await message.answer(f'Ваш выбор:\n{count}', reply_markup=markup)
    await BalanceState.next()


@dp.message_handler(IsUser(), text=back_message, state=BalanceState.add_balance_count)
async def process_add_balance_count_back(message: Message, state: FSMContext):
    await process_balance_back(message, state)


@dp.message_handler(IsUser(), text=make_payment, state=BalanceState.balance_buyout_count_confirm)
async def process_balance_buyout_count_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        count = data['count']
    if await check_is_have_enough_balance(message.from_user.id, count):
        await change_balance(message.from_user.id, count, 'buyout')
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(buyout)
        await message.answer('Оплата прошла успешно', reply_markup=markup)
        await state.finish()
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(buy_buyouts, buy_reviews)
        markup.add(add_balance, back_message)
        await message.answer('❌ На вашем балансе недостаточно средств, пополните баланс', reply_markup=markup)
        await BalanceState.start.set()


@dp.message_handler(IsUser(), text=back_message, state=BalanceState.balance_buyout_count_confirm)
async def process_balance_buyout_count_confirm_back(message: Message, state: FSMContext):
    await process_balance_buy_buyouts(message, state)


@dp.message_handler(IsUser(), text=make_payment, state=BalanceState.balance_reviews_count_confirm)
async def process_balance_reviews_count_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        count = data['count']
    if await check_is_have_enough_balance(message.from_user.id, count):
        await change_balance(message.from_user.id, count, 'reviews')
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(reviews)
        await message.answer('Оплата прошла успешно', reply_markup=markup)
        await state.finish()
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(buy_buyouts, buy_reviews)
        markup.add(add_balance, back_message)
        await message.answer('❌ На вашем балансе недостаточно средств, пополните баланс', reply_markup=markup)
        await BalanceState.start.set()


async def check_is_have_enough_balance(user_id, count_):
    # '🟢 100р, 10 шт'
    balance_ = int(await get_balance(user_id))
    return int(count_.split(' ')[1].split('р')[0]) < balance_


async def change_balance(user_id_, count_, typ):
    # '🟢 100р, 10 шт'
    count_rub = int(count_.split(' ')[1].split('р')[0])
    count_x = int(count_.split(' ')[2])
    balance_ = await get_balance(user_id_)
    await set_balance(user_id_, balance_ - count_rub)
    if typ == 'buyout':
        x = await get_buyouts(user_id_)
        await set_buyouts(user_id_, x + count_x)
    else:
        x = await get_reviews(user_id_)
        await set_reviews(user_id_, x + count_x)


@dp.message_handler(IsUser(), text=back_message, state=BalanceState.balance_reviews_count_confirm)
async def process_balance_reviews_count_confirm_back(message: Message, state: FSMContext):
    await process_balance_buy_reviews(message, state)


@dp.message_handler(IsUser(), text=make_payment, state=BalanceState.add_balance_count_confirm)
async def process_add_balance_count_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        count = data['count']
        label = f'{message.from_user.id}_{datetime.today().strftime("%d%m%Y%H%M%S")}'
        data['label'] = label
        token = await get_token_default()
        data['token'] = token
    receiver = await get_payment_default()
    link = await create_link_for_payment(receiver, label, count)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(confirm_payment, cancel_message)
    await BalanceState.next()
    await message.answer(f'Для пополнения необходимо перейти по ссылке и оплатить:\n{link}', reply_markup=markup)


@dp.message_handler(IsUser(), text=back_message, state=BalanceState.add_balance_count_confirm)
async def process_add_balance_count_confirm_back(message: Message, state: FSMContext):
    await process_add_balance(message, state)


@dp.message_handler(IsUser(), text=confirm_payment, state=BalanceState.add_balance_check_payment)
async def process_add_balance_check_payment(message: Message, state: FSMContext):
    async with state.proxy() as data:
        label = data['label']
        count = data['count']
        token = data['token']
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(buy_buyouts, buy_reviews)
    markup.add(add_balance, back_message)
    await message.answer('Оплата проверяется')
    if await add_balance_check_payment(label, token, count):
        await add_balance_to_user(message.from_user.id, count)
        await message.answer('Оплата произведена успешно, спасибо за покупку!', reply_markup=markup)
        await BalanceState.start.set()
    else:
        await message.answer('Оплата не поступила. Если вы оплачивали, обратитесь к менеджеру для уточнения', reply_markup=markup)
        await BalanceState.start.set()


async def add_balance_check_payment(label, token, count):
    check = 0
    while check < 90:
        if await check_payment(label, token, count):
            return True
        else:
            await asyncio.sleep(10)
            check += 1
    return False


async def add_balance_to_user(user, count):
    old = int(await get_balance(user))
    count = int(count)
    await set_balance(user, old+count)


@dp.message_handler(IsUser(), text=cancel_message, state=BalanceState.add_balance_check_payment)
async def process_add_balance_check_payment_cancel(message: Message, state: FSMContext):
    await process_balance_back(message, state)