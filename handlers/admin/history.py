import time

import pandas as pd
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from keyboards.default.markups import  admin_table
from loader import dp, db, bot
from filters import IsAdmin
from utils.db_get_info.get_set_info_db import get_all_buyouts


@dp.message_handler(IsAdmin(), text=admin_table)
async def process_change_discount(message: Message, state: FSMContext):
    res = await get_all_buyouts()

    receipt_arr = []
    for i in res:
        if i[11] not in [0, None, '0']:
            receipt_arr.append([i[11].split(";")[0], i[11].split(";")[1]])
        else:
            receipt_arr.append([0, 0])
    df = pd.DataFrame({'idx': [i[1] for i in res],
                       'link': [i[2] for i in res],
                       'keyword': [i[3] for i in res],
                       'count': [i[4] for i in res],
                       'address': [i[5] for i in res],
                       'date': [i[6] for i in res],
                       'status': [i[7] for i in res],
                       'review': [i[8] for i in res],
                       'bid': [i[9] for i in res],
                       'price': [i[10] for i in res],
                       'rid': [i[0] for i in receipt_arr],
                       'receipt': [i[1] for i in receipt_arr]
                       })
    table_name = f'tables/all_{round(time.time())}.xlsx'
    df.to_excel(table_name, sheet_name='Result', index=False)
    await message.answer_document(open(table_name, 'rb'))
