import os
import threading

from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.dispatcher import FSMContext

from handlers.user.utils import decode_img, create_dict, create_table_pvz, create_table_with_images
from keyboards.default.markups import *
from loader import dp, db, bot
from filters import IsUser
from states import BuyoutMenuState
from utils.connect_tg_with_browser.aggregator import agg
from utils.db_get_info.get_set_info_db import get_browser_bid, get_buyouts_ready_to_get_all, get_buyouts_in_delivery_all


@dp.message_handler(IsUser(), text=delivery_markup, state=BuyoutMenuState.start)
async def process_delivery_markup(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(buyouts_in_delivery, buyouts_ready_to_get)
    markup.add(get_code_getting, back_message)
    await message.answer('Выберите интересующий вас раздел', reply_markup=markup)


@dp.message_handler(IsUser(), text=buyouts_in_delivery, state=BuyoutMenuState.start)
async def process_my_buyouts_in_delivery(message: Message, state: FSMContext):
    #res = await get_buyouts_in_delivery(message.from_user.id)
    res = get_buyouts_in_delivery_all()
    if res:

        await message.answer(f'В пути находится {len(res)} выкупов')
        table_name = create_table_with_images(res)
        await message.answer_document(open(table_name, 'rb'))
        os.remove(table_name)
    else:
        await message.answer('На данный момент у вас нет выкупов')


@dp.message_handler(IsUser(), text=buyouts_ready_to_get, state=BuyoutMenuState.start)
async def process_my_buyouts_ready_to_get(message: Message, state: FSMContext):
    #res = await get_buyouts_ready_to_get(message.from_user.id)
    res = get_buyouts_ready_to_get_all()
    if res:
        await message.answer(f'Готовы к выдаче {len(res)} выкупов')
        table_name = create_table_pvz(res)
        result = create_dict(res)
        img_names = []
        for i in result:
            sended_qr = []
            media = []
            meida2 = []
            await message.answer(result[i][0][5])
            #print(result[i])
            for j in result[i]:
                try:
                    if j[9] not in sended_qr and j[9] not in [2, '2']:
                        sended_qr.append(j[9])
                        bid, phone, _, _, male, name, qr = await get_browser_bid(j[9])
                        try:
                            img_name = decode_img(qr)
                            if len(media) == 8:
                                await message.answer_media_group(media)
                                media = []
                            media.append(InputMediaPhoto(open(img_name, "rb"), caption=f'bid: {j[9]}, phone: +7{phone}, name: {name.split(":")[1]} {name.split(":")[0]}'))
                            img_names.append(img_name)
                        except Exception as e:
                            print(j[9], e)
                except Exception as e:
                    print(e)
            try:
                await message.answer_media_group(media)
            except:
                pass
        for i in img_names:
            try:
                os.remove(i)
            except:
                pass
        await message.answer_document(open(table_name, 'rb'))
        os.remove(table_name)
    else:
        await message.answer('На данный момент у вас нет выкупов готовых к выдаче')


@dp.message_handler(IsUser(), text=get_code_getting, state=BuyoutMenuState.start)
async def process_my_buyouts_get_code_getting(message: Message, state: FSMContext):
    await message.answer('Обновление статусов заказов и qr кодов запущено')
    th = threading.Thread(target=agg.update_order_status_not_async, args=(message.from_user.id,))
    th.start()