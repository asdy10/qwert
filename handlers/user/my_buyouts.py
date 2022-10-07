import os
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, InputMediaPhoto
from aiogram.dispatcher import FSMContext

from handlers.user.buyout_menu import process_buyout
from handlers.user.utils import decode_img, create_table_pvz, create_dict, create_table_with_images, save_image
from keyboards.default.markups import *
from loader import dp, db, bot
from filters import IsUser
from states import BuyoutMenuState, ReviewsState, ErrorState
from utils.connect_tg_with_browser.aggregator import agg
from utils.db_get_info.get_set_info_db import *
from aiogram.utils.callback_data import CallbackData

from utils.wb_api.work_wb_api import get_image_url_product


@dp.message_handler(IsUser(), text=my_buyouts, state=BuyoutMenuState.start)
async def process_my_buyouts(message: Message, state: FSMContext):
    await BuyoutMenuState.my_buyouts.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(paid_buyouts, archive_buyouts)
    markup.add(process_buyouts, cancel_buyouts)
    markup.add(buyouts_error, back_message)
    await message.answer('Выберите интересующий вас пункт', reply_markup=markup)


review_cb = CallbackData('somearg', 'idx', 'action')


@dp.message_handler(IsUser(), text=archive_buyouts, state=BuyoutMenuState.my_buyouts)
async def process_my_buyouts_archive_buyouts(message: Message, state: FSMContext):
    #res = await get_archive_buyouts(message.from_user.id)
    res = await get_all_archive_buyouts()
    if res:

        await message.answer(f'Завершенные {len(res)} выкупов')
        table_name = create_table_with_images(res)
        await message.answer_document(open(table_name, 'rb'))
        os.remove(table_name)
    else:
        await message.answer('На данный момент у вас нет выкупов')


@dp.message_handler(IsUser(), text=paid_buyouts, state=BuyoutMenuState.my_buyouts)
async def process_my_buyouts_paid_buyouts(message: Message, state: FSMContext):
    res = get_buyouts_paid_all()

    if res:
        await message.answer(f'Оплаченные {len(res)} выкупов')
        table_name = create_table_with_images(res)
        await message.answer_document(open(table_name, 'rb'))
        os.remove(table_name)
    else:
        await message.answer('На данный момент у вас нет выкупов')


error_cb = CallbackData('somearg', 'idx', 'action')
error_buyouts_cb = CallbackData('somearg', 'idx', 'action')


@dp.message_handler(IsUser(), text=buyouts_error, state=BuyoutMenuState.my_buyouts)
async def process_my_buyouts_error(message: Message, state: FSMContext):
    #res = await get_buyouts_error(message.from_user.id)
    res = get_buyouts_error_all()
    if res:
        for i in res:
            try:
                if i[7] == 'error Dont delete this':
                    continue
                markup = InlineKeyboardMarkup()
                btn = InlineKeyboardButton('Перезапустить', callback_data=error_buyouts_cb.new(idx=i[1], action='restart'))
                btn1 = InlineKeyboardButton('Удалить', callback_data=error_buyouts_cb.new(idx=i[1], action='delete'))
                markup.add(btn, btn1)
                img = f"product_images\\{i[2].split('/')[-2]}.png"
                try:
                    open(img, 'r')
                except:

                    url = get_image_url_product(i[2].split('/')[-2])
                    save_image(url)
                await message.answer_photo(open(img, 'rb'), caption=f'<b>Заказ №{i[1].split("_")[1]}</b>'
                                     f'<b>Ссылка на товар:</b>\n{i[2]}\n'
                                     f'<b>Количество:</b> {i[4]}\n'
                                     f'<b>Ключевая фраза:</b>\n{i[3]}\n'
                                     f'<b>Пункт выдачи:</b>\n{i[5]}\n<b>Дата создания выкупа:</b> {i[6]}\n<b>Статус:</b> {i[7][:100]}', reply_markup=markup)
            except Exception as e:
                print(e)

        await message.answer(f'Незавершенные {len(res)} выкупов')
        table_name = create_table_with_images(res)
        await message.answer_document(open(table_name, 'rb'))
        os.remove(table_name)
    else:
        await message.answer('На данный момент у вас нет выкупов с ошибками')


@dp.message_handler(IsUser(), text=back_message, state=BuyoutMenuState.my_buyouts)
async def process_my_buyouts_back(message: Message, state: FSMContext):
    await process_buyout(message, state)


@dp.callback_query_handler(IsUser(), error_buyouts_cb.filter(action='restart'), state=BuyoutMenuState.my_buyouts)
async def process_my_buyouts_restart(query: CallbackQuery, callback_data: dict, state: FSMContext):
    set_status_of_buyout(callback_data['idx'], 'after error')
    await query.message.delete()
    await query.message.answer('Выкуп перезапущен')


@dp.callback_query_handler(IsUser(), error_buyouts_cb.filter(action='delete'), state=BuyoutMenuState.my_buyouts)
async def process_my_buyouts_delete(query: CallbackQuery, callback_data: dict, state: FSMContext):
    delete_buyout(callback_data['idx'])
    await query.message.delete()
    await query.message.answer('Выкуп удален')


# @dp.callback_query_handler(IsUser(), review_cb.filter(action='make_review'), state=BuyoutMenuState.my_buyouts)
# async def process_my_buyouts_archive_buyouts_make_review(query: CallbackQuery, callback_data: dict, state: FSMContext):
#     async with state.proxy() as data:
#         idx = callback_data['idx']
#     await state.finish()
#     await ReviewsState.review_check_buyout.set()
#     async with state.proxy() as data:
#         data['idx'] = idx
#     await process_make_review_check_buyout(query.message, state)


@dp.message_handler(IsUser(), text=process_buyouts, state=BuyoutMenuState.my_buyouts)
async def process_my_buyouts_process_buyouts(message: Message, state: FSMContext):
    #buyouts = get_buyouts_process_cid(message.from_user.id)
    buyouts = get_buyouts_process_all()
    if buyouts:
        # for i in buyouts:
        #     await message.answer(f'<b>Заказ №{i[1].split("_")[1]}</b>\n'
        #                          f'<b>Ссылка на товар:</b>\n{i[2]}\n'
        #                          f'<b>Количество:</b> {i[4]}\n'
        #                          f'<b>Ключевая фраза:</b>\n{i[3]}\n'
        #                          f'<b>Пункт выдачи:</b>\n{i[5]}\n'
        #                          f'<b>Статус:</b> {i[7]}')


        links = {}
        for i in buyouts:
            try:
                links[i[2]] = links[i[2]] + 1
            except:
                links[i[2]] = 1
        s = ''
        for i in links:
            s += f'{links[i]} {i}\n'
        table_name = create_table_with_images(buyouts)
        await message.answer(f'В процессе {len(buyouts)} выкупов\n{s}')
        await message.answer_document(open(table_name, 'rb'))
        os.remove(table_name)
    else:
        await message.answer('На данный момент у вас нет выкупов в процессе')


@dp.message_handler(IsUser(), text=cancel_buyouts, state=BuyoutMenuState.my_buyouts)
async def process_my_buyouts_cancel_buyouts(message: Message, state: FSMContext):
    buyouts = agg.__dict__['queue_buyout'].copy()
    agg.__dict__['queue_buyout'].clear()
    for i in buyouts:
        bid, idx, keywords, link, address, count = i
        delete_buyout(idx)
    await message.answer('Выкупы удалены из очереди')

