import asyncio
import random
import time
from datetime import datetime
from threading import Thread

import pandas as pd

from browser.buyout import make_buyout_browser
from browser.delivery import get_status_buyout
from browser.review import make_review_browser
from handlers.user.errors import send_error_message, send_link_for_payment
from handlers.user.utils import sort_by_date
from loader import add_to_cart_status, status_buyout_complete, images_buyout
from utils.db_get_info.get_set_info_db import *
import concurrent.futures

from utils.logger.logger import write_log
from utils.proxy_configurator.proxy_configurator import change_proxy_ip
from utils.wb_api.work_wb_api import get_data_delivery_receipts


class Aggregator:
    __instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Aggregator, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.bids = [1]
        d = {'bids': [1], 'busy_buyout': [], 'busy_review': [], 'queue_buyout': [], 'queue_review': [], 'free_proxy': [], 'queue_proxy': []}
        self.__dict__ = d

    async def set_bids(self):
        self.__dict__['bids'] = await get_bid()

    async def set_proxy(self):
        proxies = get_pids_proxy()
        #print(proxies)

        self.__dict__['free_proxy'] = proxies

    async def get_bid_no_used(self, cid, male):
        used = await get_bid_buyouts_of_user()
        print('used', len(used))
        no_used = []
        for i in self.bids:
            if str(i) not in used + self.__dict__['busy_buyout']:
                no_used.append(str(i))
        if no_used == []:
            for i in self.bids:
                if str(i) not in used:
                    no_used.append(str(i))
        if no_used == []:
            no_used = self.bids
        all_browsers = await get_all_browsers()
        new_arr = []
        print('no_used', len(no_used))
        for i in all_browsers:
            if str(i[0]) in no_used and i[4] == male:
                new_arr.append(str(i[0]))
        print('result', len(new_arr))
        return new_arr[random.randint(0, len(new_arr) - 1)]

    def get_free_proxy(self, user_agent):
        if len(self.__dict__['free_proxy']) > 0:
            pid = self.__dict__['free_proxy'].pop()
            proxy, proxy_key = get_proxy_pid(pid)
            change_proxy_ip(proxy_key, user_agent)
            return [pid, proxy]
        else:
            return [0, 0]

    def set_free_proxy(self, pid):
        self.__dict__['free_proxy'].append(pid)

    async def make_buyout_task(self, bid, idx, keywords, link, address, count):
        print('add buyout task with bid =', bid)
        self.__dict__['queue_buyout'].append([bid, idx, keywords, link, address, count])

    async def make_review_task(self, idx, link, text, images, stars):
        bid = await get_bid_of_buyout(idx)
        bid = bid.replace('?', '')
        print('add review task with bid =', bid)
        self.__dict__['queue_review'].append([bid, idx, link, text, images, stars])

    async def queue_buyout_make_task(self):
        queue = self.__dict__['queue_buyout']
        if queue:

            #print(queue)
            for i in queue:
                bid, idx, keywords, link, address, count = i #count = count_paymenttype
                if bid not in self.__dict__['busy_buyout']:
                    _, phone, _, user_agent, _, _, _ = await get_browser_bid(bid)
                    pid, proxy = self.get_free_proxy(user_agent)
                    if str(proxy) != '0':
                        #print('remove queue', queue)
                        self.__dict__['queue_buyout'].remove(i)
                        #print('after remove queue', self.__dict__['queue_buyout'])
                        self.__dict__['busy_buyout'].append(bid)

                        args = {}
                        args['bid'] = bid
                        args['idx'] = idx
                        args['keywords'] = keywords
                        args['link'] = link
                        args['address'] = address
                        if '_' in str(count):
                            args['count'] = int(count.split('_')[0])
                            args['payment_type'] = int(count.split('_')[1])
                        else:
                            args['count'] = count
                            args['payment_type'] = 0
                        args['phone'] = phone
                        args['proxy'] = proxy
                        args['user_agent'] = user_agent
                        set_status_of_buyout(idx, 'process')
                        # th = Thread(target=make_buyout_browser, args=(phone, keywords, link, address, count, proxy, user_agent, idx))
                        # th.start()
                        try:
                            await self.script_make_buyout(args)
                        except Exception as e:
                            print(e)
                            write_log(e)
                        self.__dict__['free_proxy'].append(pid)
                        print('script completed')

    async def script_make_buyout(self, args_):
        bid = args_['bid']
        idx = args_['idx']
        #phone = args_['phone']

        loop = asyncio.get_event_loop()
        count = 0
        complete = False
        while not complete and count < 3:
            count += 1
            write_log(f'start {count} {datetime.today().strftime("%d.%m.%Y %H:%M:%S")} {str(args_)}')
            with concurrent.futures.ProcessPoolExecutor() as pool:
                complete, error = await loop.run_in_executor(pool, make_buyout_browser, args_)
        write_log(f'end {count} {datetime.today().strftime("%d.%m.%Y %H:%M:%S")} {complete} {error} {str(args_)}')
        if not complete:
            set_status_of_buyout(idx, f'{error} idx={idx}')
            await send_error_message(idx.split('_')[0], f'При выполнении заказа {idx.split("_")[1]} '
                                                        f'в аккаунте {bid} возникла ошибка\n{error}')
        else:
            set_status_of_buyout(idx, error)
            await send_error_message(idx.split('_')[0], f'Заказ {idx.split("_")[1]}, аккаунт {bid}\n{error}')

        self.__dict__['busy_buyout'].remove(bid)

    async def queue_review_make_task(self):
        queue = self.__dict__['queue_review']
        if queue:
            for i in queue:
                bid, idx, link, text, images, stars = i
                if bid not in self.__dict__['busy_review']:
                    _, phone, _, user_agent, _, _, _ = await get_browser_bid(bid)
                    pid, proxy = self.get_free_proxy(user_agent)
                    if str(proxy) != '0':
                        self.__dict__['queue_review'].remove(i)
                        self.__dict__['busy_review'].append(bid)

                        args = {}
                        args['bid'] = bid
                        args['phone'] = phone
                        args['phone'] = phone
                        args['proxy'] = proxy
                        args['user_agent'] = user_agent
                        args['idx'] = idx
                        args['link'] = link
                        args['text'] = text
                        args['images'] = images
                        args['stars'] = stars
                        try:
                            await self.script_make_review(args)
                        except Exception as e:
                            print(e)
                            write_log(e)
                        self.__dict__['free_proxy'].append(pid)

    async def script_make_review(self, args_):
        bid = args_['bid']
        idx = args_['idx']
        loop = asyncio.get_event_loop()
        count = 0
        complete = False
        while not complete and count < 3:
            count += 1
            write_log(f'start {count} {datetime.today().strftime("%d.%m.%Y %H:%M:%S")} {str(args_)}')
            with concurrent.futures.ProcessPoolExecutor() as pool:
                complete = await loop.run_in_executor(pool, make_review_browser, args_)
        write_log(f'end {count} {datetime.today().strftime("%d.%m.%Y %H:%M:%S")} {complete} {str(args_)}')
        if not complete:
            delete_review(idx)
            await send_error_message(idx.split('_')[0], f'При выполнении отзыва {idx.split("_")[1]} возникла ошибка, повторите попытку')
        else:
            await change_review_of_buyout_to_true(idx)
            old_rev = await get_reviews(idx.split('_')[0])
            await set_reviews(idx.split('_')[0], old_rev - 1)
            await send_error_message(idx.split('_')[0], 'Отзыв оставлен успешно')
        self.__dict__['busy_review'].remove(bid)

    # async def update_order_status(self):
    #     """set bid free"""
    #     # all_buyouts = await get_all_archive_buyouts()
    #     # for b in all_buyouts:
    #     #     date_time = datetime.strptime(b[6], '%d.%m.%Y %H:%M:%S')
    #     #     if (datetime.now() - date_time).total_seconds() > 86400 * 7 and '?' not in str(b[9]):
    #     #         await set_free_bid_of_buyout(b[1], f'{b[9]}?')
    #     user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    #     proxy_id, proxy = self.get_free_proxy(user_agent)
    #     check = 0
    #     while proxy == 0 and check < 600:
    #         proxy_id, proxy = self.get_free_proxy(user_agent)
    #         check += 2
    #         time.sleep(2)
    #     if proxy == 0:
    #         return False
    #     proxy, proxy_key = get_proxy_pid(proxy_id)
    #
    #     for i in self.bids:
    #         if len(get_all_buyouts_in_delivery_bid(i)) + len(get_buyouts_ready_to_get_bid(i)) > 0:
    #             _, phone, _, user_agent, _, _, _ = await get_browser_bid(i)
    #             change_proxy_ip(proxy_key, user_agent)
    #             check = 0
    #
    #             try:
    #                 #data = get_status_buyout(phone, proxy, user_agent)
    #                 print('start update bid', i)
    #                 data = get_data_delivery_receipts(phone, user_agent, proxy)
    #
    #                 for j in data:
    #                     if j != 'qr':
    #                         print(j, data[j])
    #                 """set order status"""
    #                 buyouts = get_all_buyouts_in_delivery()
    #                 data_buyouts = {}
    #                 for buyout in buyouts:
    #                     print(buyout)
    #                     if int(str(buyout[9]).replace('?', '')) == int(i):
    #                         pid = buyout[2].split('catalog/')[1].split('/')[0]
    #                         idx = buyout[1]
    #                         data_buyouts[pid] = idx
    #                 buyouts = get_buyouts_ready_to_get_bid(i)
    #                 for buyout in buyouts:
    #
    #                     if int(str(buyout[9]).replace('?', '')) == int(i):
    #                         pid = buyout[2].split('catalog/')[1].split('/')[0]
    #                         idx = buyout[1]
    #                         data_buyouts[pid] = idx
    #                 print(data_buyouts)
    #                 for sku in data:
    #                     try:
    #                         #print(sku)
    #                         if sku != 'qr':
    #                             set_status_of_buyout(data_buyouts[str(sku)], data[sku])
    #                     except:
    #                         pass
    #                 try:
    #                     set_qr(i, data['qr'])
    #                 except:
    #                     pass
    #
    #
    #             except Exception as e:
    #                 print('ERROR CHECK STATUS ORDER IN bid', i, e)
    #
    #     self.set_free_proxy(proxy_id)
    #     return True

    def update_order_status_not_async(self, cid=0):
        """set bid free"""
        print('start update')
        # all_buyouts = await get_all_archive_buyouts()
        # for b in all_buyouts:
        #     date_time = datetime.strptime(b[6], '%d.%m.%Y %H:%M:%S')
        #     if (datetime.now() - date_time).total_seconds() > 86400 * 7 and '?' not in str(b[9]):
        #         await set_free_bid_of_buyout(b[1], f'{b[9]}?')
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        proxy_id, proxy = self.get_free_proxy(user_agent)
        check = 0
        while proxy == 0 and check < 600:
            proxy_id, proxy = self.get_free_proxy(user_agent)
            check += 10
            time.sleep(10)
        if proxy == 0:
            if cid != 0:
                create_message(cid, 'Не нашли свободную прокси')
        proxy, proxy_key = get_proxy_pid(proxy_id)
        full_arr = []
        count = 0
        for i in self.bids:
            # count += 1
            # if count > 10:
            #     break
            #if ((len(get_all_buyouts_in_delivery_bid(i)) + len(get_buyouts_ready_to_get_bid(i)) + len(get_buyouts_paid_bid(i))) > 0) and i not in [2, '2']:
            if len(get_buyouts_paid_bid(i)) > 0 and i not in [2, '2']:
                _, phone, _, user_agent, _, _, _ = get_browser_bid_not_async(i)
                change_proxy_ip(proxy_key, user_agent)
                check = 0

                try:
                    #data = get_status_buyout(phone, proxy, user_agent)
                    print('start update bid', i)

                    data = get_data_delivery_receipts(phone, user_agent, proxy)
                    for j in data:
                        if j != 'qr':
                            print(j, data[j])
                            #94347421 {'status': 'complete', 'rid': '154030149640', 'price': 1896, 'receipt': 0, 'order_date': '19.09.2022 11:54:34'}
                            full_arr.append([j, data[j]['order_date'], data[j]['price'], data[j]['rid']])
                    """set order status"""

                    buyouts = get_buyouts_paid_bid(i)
                    data_buyouts = {}
                    for buyout in buyouts:
                        if int(str(buyout[9]).replace('?', '')) == int(i):
                            pid = buyout[2].split('catalog/')[1].split('/')[0]
                            idx = buyout[1]
                            data_buyouts[pid] = idx
                    # buyouts = get_all_buyouts_in_delivery()
                    # data_buyouts = {}
                    # for buyout in buyouts:
                    #     if int(str(buyout[9]).replace('?', '')) == int(i):
                    #         pid = buyout[2].split('catalog/')[1].split('/')[0]
                    #         idx = buyout[1]
                    #         data_buyouts[pid] = idx
                    # buyouts = get_buyouts_ready_to_get_bid(i)
                    # for buyout in buyouts:
                    #
                    #     if int(str(buyout[9]).replace('?', '')) == int(i):
                    #         pid = buyout[2].split('catalog/')[1].split('/')[0]
                    #         idx = buyout[1]
                    #         data_buyouts[pid] = idx
                    # buyouts = get_buyouts_paid_bid(i)
                    # for buyout in buyouts:
                    #
                    #     if int(str(buyout[9]).replace('?', '')) == int(i):
                    #         pid = buyout[2].split('catalog/')[1].split('/')[0]
                    #         idx = buyout[1]
                    #         data_buyouts[pid] = idx
                    # print(data_buyouts)
                    for sku in data:
                        try:
                            #print(sku)
                            if sku != 'qr':
                                print(data_buyouts[str(sku)], data[sku])
                                set_status_of_buyout(data_buyouts[str(sku)], data[sku])
                        except Exception as e:
                            print(e)
                    try:
                        set_qr(i, data['qr'])
                    except:
                        pass


                except Exception as e:
                    print('ERROR CHECK STATUS ORDER IN bid', i, e)
        #j, j['order_date'], j['price'], j['rid']

        full_arr.sort(key=self.sort_by_date2)
        try:
            df = pd.DataFrame({'SKU': [i[0] for i in full_arr],
                               'order_date': [i[1] for i in full_arr],
                               'price': [i[2] for i in full_arr],
                               'rid': [i[3] for i in full_arr]})
            table_name = f'tables/wtf_{round(time.time())}.xlsx'
            df.to_excel(table_name, sheet_name='Result', index=False)
        except Exception as e:
            print(e)
        self.set_free_proxy(proxy_id)
        if cid != 0:
            create_message(cid, 'Обновление статусов заказов и qr кодов завершено')

    def sort_by_date2(self, a):
        date_time = datetime.strptime(a[1], "%d.%m.%Y %H:%M:%S")
        return date_time.timestamp()

    async def add_after_error_in_queue(self):
        buyouts = await get_all_buyouts_after_error()
        for b in buyouts:
            cid, idx, link, keywords, count, address, date_buyouts, status, review, bid, _, _ = b
            await self.make_buyout_task(bid, idx, keywords, link, address, count)
            set_status_of_buyout(idx, 'new')

    async def add_buyout_from_graph_in_queue(self):
        graphs = await get_all_graphs()
        for i in graphs:
            dates = i[4].split(':')[:-2]
            times = ':'.join(i[4].split(':')[-2:])
            for date in dates:
                date_time = datetime.strptime(f'{date}:{times}', '%Y-%m-%d:%H:%M')
                if date_time < datetime.now():
                    """add buyout"""
                    temp = await get_template(i[1])
                    male = i[5]
                    cid = i[0]
                    keywords = temp[3]
                    link = temp[2]
                    address = temp[5]
                    count = i[3]
                    bid = await self.get_bid_no_used(cid, male)

                    idx = f'{cid}_{get_last_num_buyout_user(cid) + 1}'
                    await create_buyout(cid, idx, link, keywords, count, address,
                                        datetime.today().strftime("%d.%m.%Y %H:%M:%S"), 'new', False, bid)
                    await self.make_buyout_task(bid, idx, keywords, link, address, count)
                    """delete time form db"""
                    new_dates = dates.copy()
                    new_dates.remove(date)
                    if new_dates:
                        new_date_time = ':'.join(new_dates) + ':' + times
                        await update_date_graph(i[2], new_date_time)
                    else:
                        await delete_graph_gid(i[2])

    async def get_status(self):
        all_browsers = await get_all_browsers()
        man, woman = 0, 0
        for i in all_browsers:
            if i[4] == 'man':
                man += 1
            else:
                woman += 1
        return f'Всего аккаунтов: {len(self.__dict__["bids"])}\n' \
               f'Мужских: {man}\n'\
               f'Женских: {woman}\n' \
               f'Занято выкупами: {len(self.__dict__["busy_buyout"])}\n' \
               f'Занято отзывами: {len(self.__dict__["busy_review"])}\nВ очереди на выкуп: {len(self.__dict__["queue_buyout"])}\n' \
               f'В очереди на отзыв: {len(self.__dict__["queue_review"])}\n' \
               f'Свободные прокси: {len(self.__dict__["free_proxy"])}'


agg = Aggregator()
