import pickle
from datetime import datetime, timedelta

import requests
from requests.auth import HTTPProxyAuth
from bs4 import BeautifulSoup

from utils.db_get_info.get_set_info_db import get_all_receipts


def get_delivery_req(phone, user_agent='', proxy=''):
    proxies = {}
    if len(proxy) > 10:
        part1, part2 = proxy.split('@')
        username, password = part1.split(':')
        ip, port = part2.split(':')
        proxies = {"http": f"{ip}:{port}"}
        auth = HTTPProxyAuth(username, password)
    url = 'https://www.wildberries.ru/webapi/lk/myorders/delivery/active'
    if user_agent == '':
        user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'
    headers = f"""accept: */*
accept-encoding: gzip, deflate, br
accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
content-length: 0
content-type: application/x-www-form-urlencoded; charset=UTF-8
origin: https://www.wildberries.ru
referer: https://www.wildberries.ru/lk/myorders/delivery
sec-ch-ua: "Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"
sec-ch-ua-mobile: ?1
sec-ch-ua-platform: "Android"
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: {user_agent}
x-client-id: 0
x-client-time: 2022-08-26T21:02:20.942
x-requested-with: XMLHttpRequest
x-spa-version: 9.3.28.2"""
    arr_cook = {}
    for cookie in pickle.load(open(f'browser\\cookies\\cookies_{phone}', 'rb')):
        arr_cook[cookie['name']] = cookie['value']
    arr = {i.split(':')[0]: i.split(': ')[1] for i in headers.split('\n')}
    if proxies != {}:
        res1 = requests.post(url=url, headers=arr, cookies=arr_cook, proxies=proxies, auth=auth)
        try:
            res = res1.json()['value']
        except:
            print(res1.text)
    else:
        res1 = requests.post(url=url, headers=arr, cookies=arr_cook)
        try:
            res = res1.json()['value']
        except:
            print(res1.text)
    #print(res)
    positions = res['positions']
    data = {}
    for i in positions:
        print(1, i['code1S'], i['trackingStatus'], i['rId'], i['price'], get_normal_time(i['orderDate']))
        try:
            t = data[f"1_{i['code1S']}"]
            data[f"2_{i['code1S']}"] = {'status': i['trackingStatus'], 'rid': i['rId'], 'price': i['price'],
                                        'receipt': 0, 'order_date': get_normal_time(i['orderDate'])}

        except:
            try:
                t = data[i['code1S']]
                data[f"1_{i['code1S']}"] = {'status': i['trackingStatus'], 'rid': i['rId'], 'price': i['price'],
                                            'receipt': 0, 'order_date': get_normal_time(i['orderDate'])}
            except:
                data[i['code1S']] = {'status': i['trackingStatus'], 'rid': i['rId'], 'price': i['price'], 'receipt': 0, 'order_date': get_normal_time(i['orderDate'])}
    try:
        data['qr'] = res['qrCode']
    except:
        pass
    url = 'https://www.wildberries.ru/webapi/lk/myorders/delivery/closed'
    try:
        if proxies != {}:
            res = requests.post(url=url, headers=arr, cookies=arr_cook, proxies=proxies, auth=auth).json()['value']
        else:
            res = requests.post(url=url, headers=arr, cookies=arr_cook).json()['value']

        for i in res:
            for j in i['products']:
                print(2, j['code1S'], j['rId'], j['price'], get_normal_time(j['orderDate']))
                try:
                    t = data[f"1_{i['code1S']}"]
                    data[f"2_{i['code1S']}"] = {'status': 'complete', 'rid': j['rId'], 'price': j['price'], 'receipt': 0, 'order_date': get_normal_time(j['orderDate'])}

                except:
                    try:
                        t = data[i['code1S']]
                        data[f"1_{i['code1S']}"] = {'status': 'complete', 'rid': j['rId'], 'price': j['price'], 'receipt': 0, 'order_date': get_normal_time(j['orderDate'])}
                    except:
                        data[i['code1S']] = {'status': 'complete', 'rid': j['rId'], 'price': j['price'], 'receipt': 0, 'order_date': get_normal_time(j['orderDate'])}

    except:
        pass
    url = 'https://www.wildberries.ru/webapi/lk/myorders/archive/get'
    try:
        if proxies != {}:
            res = requests.post(url=url, headers=arr, cookies=arr_cook, proxies=proxies, auth=auth).json()['value']
        else:
            res = requests.post(url=url, headers=arr, cookies=arr_cook).json()['value']

        for i in res['archive']:
            print(3, i['code1S'], i['rId'], i['price'], get_normal_time(i['orderDate']))
            try:
                t = data[f"1_{i['code1S']}"]
                data[f"2_{i['code1S']}"] = data[i['code1S']] = {'status': 'complete', 'rid': i['rId'], 'price': i['price'], 'receipt': 0, 'order_date': get_normal_time(i['orderDate'])}

            except:
                try:
                    t = data[i['code1S']]
                    data[f"1_{i['code1S']}"] = data[i['code1S']] = {'status': 'complete', 'rid': i['rId'], 'price': i['price'], 'receipt': 0, 'order_date': get_normal_time(i['orderDate'])}
                except:
                    data[i['code1S']] = data[i['code1S']] = {'status': 'complete', 'rid': i['rId'], 'price': i['price'], 'receipt': 0, 'order_date': get_normal_time(i['orderDate'])}



    except:
        pass
    return data


def get_receipts_req(phone, user_agent='', proxy=''):
    url = 'https://www.wildberries.ru/webapi/lk/receipts/data?count=10'
    proxies = {}
    if len(proxy) > 10:
        part1, part2 = proxy.split('@')
        username, password = part1.split(':')
        ip, port = part2.split(':')
        proxies = {"http": f"{ip}:{port}"}
        auth = HTTPProxyAuth(username, password)
    if user_agent == '':
        user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'
    headers = f"""accept: */*
accept-encoding: gzip, deflate, br
accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
content-length: 0
origin: https://www.wildberries.ru
referer: https://www.wildberries.ru/lk/receipts/get?count=10
sec-ch-ua: "Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"
sec-ch-ua-mobile: ?1
sec-ch-ua-platform: "Android"
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: {user_agent}
x-requested-with: XMLHttpRequest
x-spa-version: 9.3.28"""
    arr_cook = {}
    for cookie in pickle.load(open(f'browser\\cookies\\cookies_{phone}', 'rb')):
        arr_cook[cookie['name']] = cookie['value']
    arr = {i.split(':')[0]: i.split(': ')[1] for i in headers.split('\n')}
    data = {}
    try:
        if proxies != {}:
            res = requests.post(url=url, headers=arr, cookies=arr_cook, proxies=proxies, auth=auth).json()['value']['data']['receipts']
        else:
            res = requests.post(url=url, headers=arr, cookies=arr_cook).json()['value']['data']['receipts']
        #print(res)
        for i in res:
            data[i['receiptId']] = {'price': i['operationSum'], 'link': i['link']}
    except:
        pass
    return data


def get_receipt_rid_by_link(link, user_agent='', proxy=''):
    proxies = {}
    if len(proxy) > 10:
        part1, part2 = proxy.split('@')
        username, password = part1.split(':')
        ip, port = part2.split(':')
        proxies = {"http": f"{ip}:{port}"}
        auth = HTTPProxyAuth(username, password)
    if user_agent == '':
        user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'

    headers = {'user-agent': user_agent}
    if proxies != {}:
        res = requests.get(link, headers=headers, proxies=proxies, auth=auth)
    else:
        res = requests.get(link, headers=headers)

    soup = BeautifulSoup(res.text, "html.parser")
    ids = soup.findAll('div', class_='products-cell products-cell_name w-100 first')
    for i in ids:
        ids1 = i.find('div', class_='products-prop-value')
        return ids1.text.split(' ')[-1]


def get_data_delivery_receipts(phone, user_agent='', proxy=''):
    if len(user_agent) < 10:
        user_agent = ''
    if len(proxy) < 10:
        proxy = ''
    data = get_delivery_req(phone, user_agent, proxy)
    receipts = get_receipts_req(phone, user_agent, proxy)
    if receipts:
        for i in receipts:
            res = get_all_receipts()
            res1 = [i.split(';')[1] for i in res]
            if receipts[i]['link'] not in res1:
                for j in data:
                    if j != 'qr':
                        if data[j]['price'] == receipts[i]['price']:
                            # find by price
                            rec_link = receipts[i]['link']
                            rid = get_receipt_rid_by_link(rec_link, user_agent, proxy)
                            if rid == data[j]['rid']:
                                receipt = f'{rid};{rec_link}'
                                data[j]['receipt'] = receipt
    return data


def get_image_url_product(id):
    for i in range(1, 10):
        url = f'https://basket-0{i}.wb.ru/vol{id[:-5]}/part{id[:-3]}/{id}/images/c246x328/1.jpg'
        res = requests.get(url)
        if res.status_code == 200:
            return url


def get_normal_time(s):
    date_, time_ = s.split('T')
    y, m, d = date_.split('-')
    time_ = time_[:-1]
    date_time = datetime.strptime(f'{d}.{m}.{y} {time_}', "%d.%m.%Y %H:%M:%S") + timedelta(hours=3)
    result = date_time.strftime("%d.%m.%Y %H:%M:%S")
    return result


def get_ip_ooo(id):
    return requests.get(f'https://wbx-content-v2.wbstatic.net/sellers/{id}.json').json()


