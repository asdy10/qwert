from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from keyboards.default.markups import user_stat
from loader import dp, db, bot
from filters import IsUser
from states import BuyoutMenuState
from utils.db_get_info.get_set_info_db import get_referals_cid


@dp.message_handler(IsUser(), text=user_stat, state=BuyoutMenuState.start)
async def process_user_stat(message: Message, state: FSMContext):
    s = ''
    for i in await get_referals_cid(message.from_user.id):
        s += f'Номер заказа: {i[1]}, ваш бонус: {i[2]}р, дата: {i[3]}\n'
    if s:
        await message.answer(s)
    else:
        await message.answer('Ваши рефералы еще не делали заказы')
