import asyncio
import time
from threading import Thread

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove

from browser.registration_browser import resend_code
from filters import IsAdmin
from keyboards.default.markups import *
from loader import dp, bot
import concurrent.futures

from states.admin_state import AddAccountState
from utils.db_get_info.get_set_info_db import create_message, get_all_browsers, set_login_status, get_login_status, \
    delete_message_, update_login_status, create_browser, get_bid_
from utils.registration.auto_reg_account import script_reg_account
from utils.registration.registration_class import reg


@dp.message_handler(IsAdmin(), text=add_account)
async def process_accs_add(message: Message, state: FSMContext):
    await AddAccountState.count_mw.set()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/menu')
    await message.answer('Введите количество М:Ж аккаунтов для регистрации, например 10:15', reply_markup=markup)


@dp.message_handler(IsAdmin(), lambda message: message.text not in ['/menu'], state=AddAccountState.count_mw)
async def process_accs_add_count_mw(message: Message, state: FSMContext):
    m, w = await check_count_mw(message.text)

    if m > 0 or w > 0:
        th = Thread(target=script_reg_account, args=(message.from_user.id, m, w))
        th.start()
        await state.finish()
    else:
        await message.answer('Некорректные данные, повторите ввод')


async def check_count_mw(count):
    try:
        m, w = count.split(':')
        return int(m), int(w)
    except:
        return 0, 0


@dp.message_handler(IsAdmin(), text='/menu', state=AddAccountState.count_mw)
async def process_accs_add_cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Меню', reply_markup=admin_menu_markup())



# @dp.message_handler(IsAdmin(), lambda message: message.text not in [back_message], state=AddAccountState.proxy)
# async def process_accs_add_proxy(message: Message, state: FSMContext):
#     proxy = message.text
#     if check_proxy(proxy):
#         async with state.proxy() as data:
#             data['proxy'] = proxy
#         await message.answer('Введите user_agent', reply_markup=back_markup())
#         await AddAccountState.next()
#
#     else:
#         await message.answer('Некорректная прокси, попробуйте еще раз', reply_markup=back_markup())
#
#
# def check_proxy(proxy):
#     return True
#
#
# @dp.message_handler(IsAdmin(), text=back_message, state=AddAccountState.proxy)
# async def process_accs_add_proxy_cancel(message: Message, state: FSMContext):
#     await process_accs_add(message, state)
#
#
# @dp.message_handler(IsAdmin(), lambda message: message.text not in [back_message], state=AddAccountState.user_agent)
# async def process_accs_add_user_agent(message: Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_agent'] = message.text
#         phone = data['phone']
#         proxy = data['proxy']
#         user_agent = message.text
#     await AddAccountState.next()
#     reg.new_reg(phone)
#     reg_ = reg.get_reg(phone)
#
#     th = Thread(target=start_reg, args=(reg_, message.from_user.id, proxy, user_agent))
#     th.start()
#     th2 = Thread(target=run_wait, args=(reg_,))
#     th2.start()
#
#     await message.answer('Сейчас произойдет авторизация, ожидайте код')
#
#
# @dp.message_handler(IsAdmin(), text=back_message, state=AddAccountState.user_agent)
# async def process_accs_add_user_agent_back_message(message: Message, state: FSMContext):
#     await process_accs_add(message, state)
#
#
# def start_reg(reg_, cid, proxy, user_agent):
#     if not reg_.set_browser(proxy, user_agent):
#         create_message(cid, 'Браузер не смог открыться, попробуйте еще раз')
#         return
#     if not reg_.start_registration():
#         create_message(cid, 'Браузер не смог начать авторизацию, попробуйте еще раз')
#         return
#     create_message(cid, 'Код отправлен')
#
#
# def run_wait(reg_):
#     reg_.wait_commands()
#
#
# @dp.message_handler(IsAdmin(), text=cancel_message, state=AddAccountState.phone)
# async def process_accs_add_phone_back(message: Message, state: FSMContext):
#     await state.finish()
#     await message.answer('Отменено', reply_markup=admin_menu_markup())
#
#
# @dp.message_handler(IsAdmin(), lambda message: message.text not in [cancel_message], state=AddAccountState.code_check)
# async def process_accs_add_code_check(message: Message, state: FSMContext):
#     async with state.proxy() as data:
#         phone = data['phone']
#         proxy = data['proxy']
#         user_agent = data['user_agent']
#     reg_ = reg.get_reg(phone)
#     #loop = asyncio.get_event_loop()
#     # with concurrent.futures.ProcessPoolExecutor() as pool:
#     #     result = await loop.run_in_executor(pool, end_reg, phone, message.text, message.from_user.id)
#     # print(result)
#     #loop = asyncio.get_event_loop()
#     set_login_status(phone, 'False')
#     th = Thread(target=end_reg, args=(reg_, message.text, message.from_user.id, phone, proxy, user_agent))
#     th.start()
#     check = 0
#     status = get_login_status(phone)
#     while check < 30 and status == 'False':
#         check += 1
#         await asyncio.sleep(2)
#         status = get_login_status(phone)
#     status = get_login_status(phone)
#     if status == 'Code error':
#         markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#         markup.add(resend_code, cancel_message)
#         await AddAccountState.next()
#         await message.answer('Код неверен', reply_markup=markup)
#         delete_message_(f'login{phone}')
#     elif status == 'True':
#         delete_message_(f'login{phone}')
#         await message.answer('Аккаунт сохранен')
#         await state.finish()
#     else:
#         await message.answer('Какая-то другая ошибка', reply_markup=admin_menu_markup())
#         delete_message_(f'login{phone}')
#         await state.finish()
#
#
# def end_reg(reg_, code, cid, phone, proxy, user_agent):
#     reg_.set_code(code)
#     reg_.enter_code()
#     time.sleep(3)
#     res = reg_.check_code()
#     if res == 'True':
#         time.sleep(5)
#         reg_.save_cookie()
#         bid = get_bid_()[-1] + 1
#         create_browser(bid, phone, proxy, user_agent)
#         update_login_status(phone, 'True')
#         create_message(cid, 'Вход успешен')
#         reg_.close()
#     elif res == 'Code error':
#         update_login_status(phone, 'Code error')
#     else:
#         create_message(cid, 'Не удалось войти')
#         reg_.close()
#
# #    loop.run_until_complete(send_text_message(cid, f'{res}'))
#     #loop.close()
#     # with concurrent.futures.ProcessPoolExecutor() as pool:
#     #
#     #     result = loop.run_in_executor(pool, send_text_message, cid, f'{res}')
#     #return res
#
#
# @dp.message_handler(IsAdmin(), lambda message: message.text not in [cancel_message], state=AddAccountState.resend_code)
# async def process_accs_add_code_resend(message: Message, state: FSMContext):
#     async with state.proxy() as data:
#         phone = data['phone']
#     await message.answer('Код отправится через 1 минуту', reply_markup=cancel_markup())
#     await asyncio.sleep(50)
#     reg_ = reg.get_reg(phone)
#     reg_.resend_code()
#     await message.answer('Код отправлен')
#     await AddAccountState.code_check.set()
#
#
# @dp.message_handler(IsAdmin(), text=cancel_message, state=AddAccountState.resend_code)
# async def process_accs_add_code_resend_cancel(message: Message, state: FSMContext):
#     async with state.proxy() as data:
#         phone = data['phone']
#     reg_ = reg.get_reg(phone)
#     reg_.close()
#     await state.finish()
#     await message.answer('Отменено', reply_markup=admin_menu_markup())
#
#
# @dp.message_handler(IsAdmin(), text=cancel_message, state=AddAccountState.code_check)
# async def process_code_check_back(message: Message, state: FSMContext):
#     await state.finish()
#     await message.answer('Отменено', reply_markup=admin_menu_markup())
#
