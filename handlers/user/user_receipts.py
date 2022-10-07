import os
import time

from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from keyboards.default.markups import receipts
from loader import dp, db, bot
from filters import IsUser
from states import BuyoutMenuState
from utils.db_get_info.get_set_info_db import get_all_buyouts_of_user
import pandas as pd


@dp.message_handler(IsUser(), text=receipts, state=BuyoutMenuState.start)
async def process_receipts(message: Message, state: FSMContext):
    buyouts = await get_all_buyouts_of_user(message.from_user.id)
    new_arr = []
    for i in buyouts:
        if i[11] not in [None, '0']:
            new_arr.append(i)
    df = pd.DataFrame({'rid': [i[11].split(';')[0] for i in new_arr],
                       'receipt': [i[11].split(';')[1] for i in new_arr],
                       'price': [i[10] for i in new_arr],
                       'date': [i[6] for i in new_arr],
                       'idx': [i[1] for i in new_arr],
                       'link': [i[2] for i in new_arr],
                       'keywords': [i[3] for i in new_arr],
                       'count': [i[4] for i in new_arr],
                       'address': [i[5] for i in new_arr],
                       'review': [i[8] for i in new_arr],
                       'bid': [i[9] for i in new_arr],
                       })

    table_name = f'tables/receipts_{round(time.time())}.xlsx'
    df.to_excel(table_name, sheet_name='Result', index=False)
    await message.answer_document(open(table_name, 'rb'))
    os.remove(table_name)
