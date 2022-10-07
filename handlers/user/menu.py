from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove

from keyboards.default.markups import buyout, reviews, info, admin_status, admin_stat, admin_change_discount, \
    admin_change_payment, admin_set_user_discount, admin_set_default_b_r_price, \
    admin_set_user_b_r_price, admin_set_status_buyout, admin_get_buyout_idx, admin_get_user, admin_set_ref_bonus
from loader import dp, bot
from filters import IsAdmin, IsUser

catalog = '🛍️ Каталог'

cart = '🛒 Корзина'
delivery_status = '🚚 Статус заказа'
sos = '❓ sos'
balance = '💰 Баланс'
settings = '⚙️ Настройка каталога'
orders = '🚚 Заказы'
questions = '❓ Вопросы'
set_orders_status = '⚙️Настройка заказа'


@dp.message_handler(IsUser(), commands='menu')
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(buyout, reviews)
    markup.add(balance, info)
    await message.answer('Меню', reply_markup=markup)
