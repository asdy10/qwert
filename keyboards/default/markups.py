from aiogram.types import ReplyKeyboardMarkup

from utils.db_get_info.get_set_info_db import get_b_r_price, get_addresses, get_b_r_price_default

back_message = '👈 Назад'
confirm_message = '✅ Подтвердить'
all_right_message = '✅ Все верно'
cancel_message = '🚫 Отменить'
change_message = '✍️  Изменить'
ready_message = '✅  Готово'

balance = '💰 Баланс'
add_balance = 'Пополнить баланс'
make_payment = '💳 Оплатить'
link_for_payment = '🔗 Ссылка на оплату'


buyout = '📦 Выкуп'
my_buyouts = '📔 Мои выкупы'
make_buyout_btn = '✅ Сделать выкуп'
add_more_address = '📌 Да, добавить еще один адрес'
confirm_payment = 'Оплачено'
buyouts_in_delivery = '🚛 Выкупы в пути'
buyouts_ready_to_get = '✅ Готовы к выдаче'
delivery_markup = 'Доставки'
buyouts_error = '❌ Незавершенные'
archive_buyouts = '🔺 Завершенные выкупы'
cancel_buyouts = 'Отменить выкупы в очереди'
process_buyouts = 'Выкупы в процессе'
paid_buyouts = 'Оплаченные'
get_code_getting = 'Обновить статус заказов и qr коды'
send_buyout_in_template = 'Занести выкуп в шаблон'
make_timetable_buyout = 'Составить календарь выкупов'
check_delivery = 'Отследить путь выкупа'
buy_buyouts = 'Купить выкупы'
check_link_payment = 'Проверить ссылку для оплаты'
get_link_payment = 'Получить ссылку на оплату'

reviews = '⭐️ Отзывы'
my_reviews = '🗂 Мои отзывы'
make_review = '✍️ Оставить отзыв'
buy_reviews = 'Купить отзывы'

templates = '📂 Шаблоны'
my_templates = '🗂Мои шаблоны'
make_template = '✅  Создать шаблон'

timetable_buyouts = '📆 Графики выкупов'
my_timetable = '🗓 Мои графики'
make_timetable = '✅ Создать график'

info = '📚 Информация'
user_stat = '📊 Статистика рефералов'
receipts = 'Чеки'

admin_stat = 'Статистика'
admin_status = 'Статус бота'
admin_change_discount = 'Установить СПП'
admin_set_user_discount = 'Установить СПП юзеру'
admin_change_payment = 'Изменить способ оплаты'
admin_set_user_b_r_price = 'Установить BR цену юзеру'
admin_set_ref_bonus = 'Установить реферальный бонус'
admin_set_default_b_r_price = 'Установить BR цену'
admin_set_status_buyout = 'Установить статус выкупа'
admin_get_buyout_idx = 'Получить выкуп idx'
admin_get_user = 'Статистика пользователя'
add_account = 'Добавить аккаунт'
man_acc = 'Мужской'
woman_acc = 'Женский'
admin_add_proxy = 'Добавить прокси'
admin_table = 'Таблица выкупов'



def confirm_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(confirm_message)
    markup.add(back_message)

    return markup


def back_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)

    return markup


def cancel_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(cancel_message)

    return markup


def check_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, all_right_message)

    return markup


def submit_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(cancel_message, all_right_message)

    return markup


def payment_markup():
    pay100_ = '🟢 100р'
    pay200_ = '🟢 200р'
    pay500_ = '🟢 500р'
    pay1000_ = '🟢 1000р'
    pay2000_ = '🟢 2000р'
    pay5000_ = '🟢 5000р'
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(pay100_, pay200_, pay500_)
    markup.add(pay1000_, pay2000_, pay5000_)
    markup.add(back_message)
    return markup


async def buyout_markup(cid):
    b, r = await get_b_r_price(cid)
    if b == 0 or r == 0:
        b, r = await get_b_r_price_default()
    b, r = int(b), int(r)
    pay10_ = f'🟢 {10 * b}р, 10 шт'
    pay20_ = f'🟢 {20 * b}р, 20 шт'
    pay50_ = f'🟢 {50 * b}р, 50 шт'
    pay100_ = f'🟢 {100 * b}р, 100 шт'
    pay200_ = f'🟢 {200 * b}р, 200 шт'
    pay500_ = f'🟢 {500 * b}р, 500 шт'
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(pay10_, pay20_, pay50_)
    markup.add(pay100_, pay200_, pay500_)
    markup.add(back_message)
    return markup


async def review_markup(cid):
    b, r = await get_b_r_price(cid)
    b, r = int(b), int(r)
    pay10_ = f'🟢 {10 * r}р, 10 шт'
    pay20_ = f'🟢 {20 * r}р, 20 шт'
    pay50_ = f'🟢 {50 * r}р, 50 шт'
    pay100_ = f'🟢 {100 * r}р, 100 шт'
    pay200_ = f'🟢 {200 * r}р, 200 шт'
    pay500_ = f'🟢 {500 * r}р, 500 шт'
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(pay10_, pay20_, pay50_)
    markup.add(pay100_, pay200_, pay500_)
    markup.add(back_message)
    return markup


def admin_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(admin_status, admin_table)
    markup.add(add_account, admin_add_proxy)
    markup.add(admin_set_default_b_r_price, admin_set_user_b_r_price)
    markup.add(admin_change_payment, admin_set_status_buyout, admin_get_buyout_idx)
    #markup.add(admin_get_user, admin_set_ref_bonus)#, '/run_bot'
    return markup


def courier_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(get_code_getting, buyouts_ready_to_get)
    return markup


def addresses_markup():
    adrs = get_addresses()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in adrs:
        markup.add(i)
    return markup
