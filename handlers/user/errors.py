import os

from loader import dp, db, bot


async def send_error_message(cid, text):
    await bot.send_message(cid, text)


async def send_link_for_payment(cid, text):
    link, qrname = text.split(';')
    with open(qrname, 'rb') as f:
        await bot.send_photo(cid, f.read(), link)
    #await bot.send_message(cid, f'{link}, {qrname}')


async def send_fail_payment(cid, payment):
    await bot.send_message(cid, f'{payment}')


