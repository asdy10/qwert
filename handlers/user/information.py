from aiogram.types import Message, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from keyboards.default.markups import info
from loader import dp
from filters import IsUser


@dp.message_handler(IsUser(), text=info)
async def process_info(message: Message, state: FSMContext):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Наш канал', url='https://t.me/wb_bot_info/16')
    btn2 = InlineKeyboardButton('Чат WB bot', url='https://t.me/wb_bot_info/16')
    btn3 = InlineKeyboardButton('Техподдержка', url='https://t.me/wb_bot_info/16')
    markup.add(btn1, btn2)
    markup.add(btn3)
    await message.answer('[1. Что такое WB bot?](https://t.me/wb_bot_info/5)\n'
                         '[2. Что умеет WB bot?](https://t.me/wb_bot_info/6)\n'
                         '[3. Что такое выкупы и для чего они нужны?](https://t.me/wb_bot_info/7)\n'
                         '[4. Прайс на услуги WB bot](https://t.me/wb_bot_info/8)\n'
                         '[5. Как пополнить баланс и оплатить услуги WB bot?](https://t.me/wb_bot_info/9)\n'
                         '[6. Сколько выкупов нужно для продвижения товара?](https://t.me/wb_bot_info/10)\n'
                         '[7. Что такое шаблоны выкупов?](https://t.me/wb_bot_info/11)\n'
                         '[8. Что такое график выкупов?](https://t.me/wb_bot_info/12)\n'
                         '[9. Как написать отзыв?](https://t.me/wb_bot_info/13)\n'
                         '[10. Когда нужно оставлять отзыв?](https://t.me/wb_bot_info/14)\n'
                         '[11. Как делать выкуп через WB bot?](https://t.me/wb_bot_info/15)\n'
                         '[12. Почему бот отказывается делать выкуп?](https://t.me/wb_bot_info/17)\n'  
                         '[13. Связаться с администратором](https://t.me/wbbot_admin)\n'
                         '[14. Заказ инфографики | SEO оптимизации](https://t.me/wb_bot_info/21)\n'
                         , parse_mode=ParseMode.MARKDOWN, reply_markup=markup, disable_web_page_preview=True)
