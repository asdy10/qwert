from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from keyboards.default.markups import *
from loader import dp, db, bot
from filters import IsUser
from states import BuyoutMenuState


@dp.message_handler(IsUser(), text=buyout)
async def process_buyout(message: Message, state: FSMContext):
    await BuyoutMenuState.start.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(my_buyouts, templates)
    markup.add(make_buyout_btn, timetable_buyouts)
    markup.add(delivery_markup, back_message)
    await message.answer('Выберите интересующий вас раздел', reply_markup=markup)


@dp.message_handler(IsUser(), text=back_message, state=BuyoutMenuState.start)
async def process_buyout_back(message: Message, state: FSMContext):
    await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(buyout, reviews)
    markup.add(balance, info)
    await message.answer('Выберите пункт главного меню, который вас интересует👇', reply_markup=markup)
