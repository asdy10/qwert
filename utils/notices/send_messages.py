import asyncio

from loader import bot
from utils.db_get_info.get_set_info_db import get_new_message, delete_message


async def check_new_messages():
    await asyncio.sleep(5)
    while True:
        try:
            new_messages = await get_new_message()
            for i in new_messages:
                try:
                    int(i[0])
                    try:
                        await bot.send_message(i[0], f'{i[1]}', parse_mode='markdown')
                        await delete_message(i[0])
                    except Exception as e:
                        print(e)
                except:
                    pass

        except Exception as e:
            print(e)
        await asyncio.sleep(5)