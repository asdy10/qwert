import asyncio
from datetime import datetime

from loader import bot
from utils.db_get_info.get_set_info_db import get_all_graphs, get_template, update_date_graph, delete_graph_gid


async def get_graph_notice():
    graphs = await get_all_graphs()
    data = {}
    for i in graphs:
        dates = i[4].split(':')[:-2]
        times = ':'.join(i[4].split(':')[-2:])
        for date in dates:
            date_time = datetime.strptime(f'{date}:{times}', '%Y-%m-%d:%H:%M')
            if date_time < datetime.now():
                """send notice"""
                temp = await get_template(i[1])
                data[i[0]] = f'Время для выкупа\n<b>Шаблон №{temp[1].split("_")[1]}</b>\n' \
                             f'<b>Ссылка на товар:</b>\n{temp[2]}\n<b>Ключевая фраза:</b>\n' \
                             f'{temp[3]}\n<b>Пункт выдачи:</b>\n{temp[5]}'

                """delete time form db"""
                new_dates = dates.copy()
                new_dates.remove(date)
                if new_dates:
                    new_date_time = ':'.join(new_dates) + ':' + times
                    await update_date_graph(i[2], new_date_time)
                else:
                    await delete_graph_gid(i[2])
                break
    return data

