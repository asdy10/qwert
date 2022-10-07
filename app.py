import asyncio
import base64
import concurrent
import os
import random
import threading
import time

from selenium.webdriver.common.by import By

import handlers
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from browser.cookies_browser import get_open_browser, set_cookies
from data import config
from filters import IsUser, IsAdmin, IsCourier
from filters.is_not_allowed import IsNotAllowedUser
from handlers.admin.admin_menu import run_queue_buyout_make_task, run_queue_review_make_task, check_and_send_notice, \
    run_update_order_status, run_add_after_error_in_queue, run_add_buyout_from_graph_in_queue, \
    run_update_order_status_not_async
from keyboards.default.markups import buyout, reviews, info, balance,  admin_menu_markup, courier_menu_markup
from loader import dp, db, bot
from utils.android.android_connector import run_update_adb
from utils.db_get_info.get_set_info_db import *
import filters
import logging

from utils.notices.send_messages import check_new_messages

filters.setup(dp)

WEBAPP_HOST = "127.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))


@dp.message_handler(IsUser(), commands='start')
async def cmd_start_user(message: types.Message):

    print(message.text, message.from_user.id)
    if not await is_user_exist(message.from_user.id):
        # try:
        #     ref = message.text.split()[1]
        # except:
        #     ref = 0
        #b, r = await get_b_r_price_default()
        await create_user(message.from_user.id, message.from_user.username, 20, 0, 0, 0, 1, 1, 5, 0)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(buyout, reviews)
    markup.add(balance, info)
    await message.answer('Выберите пункт главного меню, который вас интересует👇', reply_markup=markup)


@dp.message_handler(IsAdmin(), commands='start')
async def cmd_start_admin(message: types.Message):
    print(message.text)
    await message.answer('🤖 Я бот. Режим админа', reply_markup=admin_menu_markup())


@dp.message_handler(IsCourier(), commands='start')
async def cmd_start_admin(message: types.Message):
    await message.answer('🤖 Я бот. Режим курьера', reply_markup=courier_menu_markup())


@dp.message_handler(IsNotAllowedUser(), commands='start')
async def cmd_start_admin(message: types.Message):
    print(message.text)
    await message.answer('🤖 Я бот. Но у вас нет доступа')


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)#, filename='logs.txt'
    db.create_tables()
    logging.info('#####START#####')
    await bot.delete_webhook()
    await bot.set_webhook(config.WEBHOOK_URL)
    asyncio.create_task(check_new_messages())
    count_thread = 1
    from utils.connect_tg_with_browser.aggregator import agg
    await agg.set_bids()
    await agg.set_proxy()

    for i in range(count_thread):
        asyncio.create_task(run_queue_buyout_make_task())
        asyncio.create_task(run_queue_review_make_task())
    # th = threading.Thread(target=run_add_buyout_from_graph_in_queue_not_async)
    # th.start()
    # th = threading.Thread(target=run_update_order_status_not_async)
    # th.start()
    th = threading.Thread(target=run_update_adb)
    th.start()
    th = threading.Thread(target=run_update_order_status_not_async)
    th.start()

    #asyncio.create_task(check_and_send_notice())
    #asyncio.create_task(run_update_order_status())
    asyncio.create_task(run_add_after_error_in_queue())
    asyncio.create_task(run_add_buyout_from_graph_in_queue())

    print('run completed')


async def on_shutdown():
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


if __name__ == '__main__':
    if "HEROKU" in list(os.environ.keys()):

        executor.start_webhook(
            dispatcher=dp,
            webhook_path=config.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )

    else:

        executor.start_polling(dp, on_startup=on_startup, skip_updates=False)

