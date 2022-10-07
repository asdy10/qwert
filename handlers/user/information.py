from aiogram.types import Message, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from keyboards.default.markups import info
from loader import dp
from filters import IsUser


@dp.message_handler(IsUser(), text=info)
async def process_info(message: Message, state: FSMContext):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Наш канал', url='https://t.me/wb_totop_info')
    btn2 = InlineKeyboardButton('Чат WB ToTop bot', url='https://t.me/wb_totop_chat')
    btn3 = InlineKeyboardButton('Техподдержка', url='https://t.me/wb_totop_admin')
    markup.add(btn1, btn2)
    markup.add(btn3)
    await message.answer('[1. О сервисе](https://t.me/wb_totop_info/2)\n'
                         '[2. В чем суть?](https://t.me/wb_totop_info/3)\n'
                         '[3. Что такое WB ToTop bot?](https://t.me/wb_totop_info/4)\n'
                         '[4. Что умеет WB ToTop bot](https://t.me/wb_totop_info/5)\n'
                         '[5. Что такое выкупы и для чего они нужны?](https://t.me/wb_totop_info/6)\n'
                         '[6. Прайс на услуги WB ToTop bot](https://t.me/wb_totop_info/7)\n'
                         '[7. Как пополнить баланс и оплатить услуги WB ToTop bot?](https://t.me/wb_totop_info/8)\n'
                         '[8. Сколько выкупов нужно для продвижения товара?](https://t.me/wb_totop_info/9)\n'
                         '[9. Что такое шаблоны выкупов?](https://t.me/wb_totop_info/10)\n'
                         '[10. Что такое график выкупов?](https://t.me/wb_totop_info/11)\n'
                         '[11. Как сделать выкуп?](https://t.me/wb_totop_info/14)\n'
                         '[12. Как написать отзыв?](https://t.me/wb_totop_info/12)\n'
                         , parse_mode=ParseMode.MARKDOWN, reply_markup=markup, disable_web_page_preview=True)
