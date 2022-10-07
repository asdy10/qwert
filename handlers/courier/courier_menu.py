
import os
import threading
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputMediaPhoto, InputFile

from handlers.user.utils import create_table_pvz, create_dict, decode_img
from keyboards.default.markups import courier_menu_markup, get_code_getting, buyouts_ready_to_get
from loader import dp, db, bot
from filters import IsCourier
from utils.connect_tg_with_browser.aggregator import agg
from utils.db_get_info.get_set_info_db import get_buyouts_ready_to_get_all, get_browser_bid, get_qr


@dp.message_handler(IsCourier(), text=get_code_getting)
async def process_my_buyouts_get_code_getting(message: Message, state: FSMContext):
    await message.answer('Обновление статусов заказов и qr кодов запущено')
    th = threading.Thread(target=agg.update_order_status_not_async, args=(message.from_user.id,))
    th.start()


@dp.message_handler(IsCourier(), text=buyouts_ready_to_get)
async def process_my_buyouts_ready_to_get(message: Message, state: FSMContext):
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

            for j in result[i]:
                print(j)
                try:
                    if j[9] not in sended_qr and j[9] not in [2, '2']:
                        sended_qr.append(j[9])
                        bid, phone, _, _, male, name, qr = await get_browser_bid(j[9])
                        try:
                            img_name = decode_img(qr)
                            if len(media) == 8:
                                await message.answer_media_group(media)
                                media = []
                            media.append(InputMediaPhoto(open(img_name, "rb"),
                                                         caption=f'bid: {j[9]}, phone: +7{phone}, name: {name.split(":")[1]} {name.split(":")[0]}'))
                            img_names.append(img_name)
                        except Exception as e:
                            print(e)
                except Exception as e:
                    print(e)
            await message.answer_media_group(media)
        for i in img_names:
            try:
                os.remove(i)
            except:
                pass
        await message.answer_document(open(table_name, 'rb'))
        os.remove(table_name)
    else:
        await message.answer('На данный момент у вас нет выкупов готовых к выдаче')


