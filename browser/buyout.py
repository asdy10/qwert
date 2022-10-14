import asyncio
import logging
import os
import random
import time
from datetime import datetime
from threading import Thread

from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from browser.cart_products import go_to_cart, change_count_in_cart, change_address_ship, clear_cart, set_payment_method, \
    get_price, check_is_product_in_cart
from browser.cookies_browser import get_open_browser, set_cookies, save_cookies
from browser.liked_products import delete_from_liked, open_liked, add_to_cart
from browser.requests_wildberries import get_brand_of_product
from browser.utils import find_and_click_by_class_name, check_address, qr_code, qr_decode
from handlers.user.errors import send_link_for_payment, send_fail_payment
from loader import status_buyout_complete, add_to_cart_status, images_buyout
from utils.android.android_connector import device
from utils.db_get_info.get_set_info_db import get_buyout_idx, get_referals_idx, set_status_of_buyout, set_date_buyout
from utils.logger.logger import write_log


def find_and_add_products(driver, keywords, link, is_brand=False):
    print('search')
    driver = find_by_keywords(driver, keywords)

    product_id = link.split('catalog/')[1].split('/')[0]
    actions = ActionChains(driver)
    time.sleep(15)
    print('check product on page')
    is_product_in_page = check_is_product_in_page(driver, product_id)
    print('is_product_in_page', is_product_in_page)
    count_pages = 0
    while not is_product_in_page and count_pages < 7:
        count_pages += 1
        print('page', count_pages)
        ids = get_all_product_ids_on_page(driver)
        res = like_random_products_on_page(driver, ids)
        if res == 'no items':
            time.sleep(5)
            continue
        time.sleep(5)
        try:
            next_page = driver.find_element(By.CLASS_NAME, 'pagination-next')
            actions.move_to_element(next_page).perform()
            time.sleep(2)
            next_page.click()
            time.sleep(10)
            is_product_in_page = check_is_product_in_page(driver, product_id)
        except:
            print('except next page')
            is_product_in_page = False
            return driver, False
    print('find', is_product_in_page)
    if is_product_in_page:
        print('product on page')
        ids = get_all_product_ids_on_page(driver)
        like_random_products_on_page(driver, ids, f'c{product_id}')
        # for i in range(2):
        #     try:
        #         print('get_all_product_ids_on_page after')
        #         ids = get_all_product_ids_on_page(driver)
        #         print('like_random_products_on_page after')
        #         res = like_random_products_on_page(driver, ids)
        #         if res == 'no items':
        #             time.sleep(5)
        #             continue
        #         next_page = driver.find_element(By.CLASS_NAME, 'pagination-next')
        #         actions.move_to_element(next_page).perform()
        #         time.sleep(0.5)
        #         next_page.click()
        #         time.sleep(5)
        #     except:
        #         try:
        #             for i in driver.find_elements(By.CLASS_NAME, 'pagination-item'):
        #                 try:
        #                     if 'page=1' in i.get_attribute('href'):
        #                         i.click()
        #                         time.sleep(5)
        #                 except:
        #                     pass
        #         except:
        #             pass
    else:
        return driver, False
    time.sleep(10)
    return driver, True


def add_products_last(driver, keywords):
    driver = find_by_keywords(driver, keywords)
    actions = ActionChains(driver)
    for i in range(2):
        try:
            ids = get_all_product_ids_on_page(driver)
            res = like_random_products_on_page(driver, ids)
            if res == 'no items':
                time.sleep(5)
                continue
            next_page = driver.find_element(By.CLASS_NAME, 'pagination-next')
            actions.move_to_element(next_page).perform()
            time.sleep(0.5)
            next_page.click()
            time.sleep(5)
        except:
            for j in driver.find_elements(By.CLASS_NAME, 'pagination-item'):
                try:
                    if 'page=1' in j.get_attribute('href'):
                        j.click()
                        time.sleep(5)
                except:
                    pass
    return driver


def find_by_keywords(driver, keywords):
    try:
        search = driver.find_element(By.ID, 'searchInput') #By.CLASS_NAME, 'search-catalog__block'
        if not search.is_displayed():
            search = driver.find_element(By.CLASS_NAME, 'header__nav-icons').find_element(By.CLASS_NAME,
                'j-search-catalog__input')
        time.sleep(1)
        search.click()
        time.sleep(2)
        search = driver.find_element(By.ID, 'searchInput')
    except:
        search = driver.find_element(By.CLASS_NAME, 'nav-element__search')

        time.sleep(1)
        search.click()
        time.sleep(2)
        search = driver.find_element(By.ID, 'mobileSearchInput')
    search.clear()
    for i in keywords:
        search.send_keys(i)
        time.sleep(0.15)
    search.send_keys(Keys.ENTER)
    time.sleep(3)
    return driver


def check_is_product_in_page(driver, product_id):
    try:
        driver.find_element(By.ID, f'c{product_id}')
        return True
    except:
        return False


def get_all_product_ids_on_page(driver):
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    ids = [tag['id'] for tag in soup.findAll('div', class_='product-card')]
    return ids


def click_like_btn(driver):
    actions = ActionChains(driver)
    # check = 0
    # while driver.find_elements(By.CLASS_NAME, 'btn-heart-black') == [] and check < 5:
    #     time.sleep(5)
    #     check += 1
    #     print('sleep', driver.find_elements(By.CLASS_NAME, 'btn-heart-black') )
    time.sleep(20)
    print(1)
    el3 = driver.find_elements(By.CLASS_NAME, 'popup__btn')
    for el4 in el3:
        try:
            el4.find_element(By.CLASS_NAME, 'popup__btn-main').click()
            # print('click 18+')
            time.sleep(5)
        except:
            pass
    print(2)
    for i in driver.find_elements(By.CLASS_NAME, 'j-size'):
        try:
            if i.get_attribute('class') != 'j-size disabled':
                actions.move_to_element(i).perform()
                time.sleep(1)
                i.click()
                time.sleep(2)
                break
        except:
            pass
    print(3)
    for i in driver.find_elements(By.CLASS_NAME, 'btn-heart-black'):
        print(i.text)
        try:
            if 'active' not in i.get_attribute('class'):
                try:
                    i.click()
                    print('click like')
                except:
                    pass
        except:
            pass
    time.sleep(7)
    return driver


def like_random_products_on_page(driver, ids, id_product=''):
    actions = ActionChains(driver)
    count_add_products = 0 # random.randint(2, 4)
    ids_add = []
    print('len', len(ids))
    try:
        for i in range(count_add_products):
            ids_add.append(ids[random.randint(0, len(ids) - 1)])
    except Exception as e:
        print(e)
        return 'no items'
    if id_product != '':
        if id_product not in ids_add:
            ids_add.append(id_product)
    current_scroll_position, new_height = 500, 1000
    for i in ids:
        try:
            el = driver.find_element(By.ID, i)
            el2 = el.find_element(By.CLASS_NAME, 'goods-name')
            speed = 10
            new_height = el2.location['y'] - 500
            while current_scroll_position <= new_height:
                current_scroll_position += speed
                driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            time.sleep(0.2)
            if ids_add:
                if i in ids_add:
                    actions.move_to_element(el2).perform()
                    time.sleep(5)
                    el2.click()
                    time.sleep(5)
                    el3 = driver.find_elements(By.CLASS_NAME, 'popup__btn')
                    for el4 in el3:
                        try:
                            el4.find_element(By.CLASS_NAME, 'popup__btn-main').click()
                            #print('click 18+')
                            time.sleep(5)
                        except:
                            pass
                    try:
                        time.sleep(5)
                        print('start clikc like')
                        click_like_btn(driver)
                    except:
                        pass
                    time.sleep(5)
                    driver.back()
                    time.sleep(7)
        except:
            time.sleep(7)
    time.sleep(8)
    return 'good'


def get_qr_for_pay(driver, idx, payment_type=0):
    #driver = go_to_cart(driver)
    driver.execute_script("document.body.style.zoom='0.67'")
    actions = ActionChains(driver)
    #time.sleep(5)
    el2 = driver.find_element(By.CLASS_NAME, 'basket-order__b-oferta-access')
    actions.move_to_element(el2).perform()
    time.sleep(2)
    driver = find_and_click_by_class_name(driver, 'b-btn-do-order')
    time.sleep(10)
    imgname = f'{idx}{datetime.today().strftime("%H%M%S")}'
    driver.get_screenshot_as_file(f'data/qr_images/{imgname}.png')
    link = qr_decode(f'data/qr_images/{imgname}.png')
    dir = os.path.abspath(os.curdir)
    qrname = f'{dir}\\data\\decoded_qr_images\\{imgname}.png'
    qr_code(link, qrname)
    #images_buyout[idx] = {'link': link, 'qrname': qrname}
    if payment_type == 1:
        pin = '1320'
        device.add_queue(link, pin)
        th = Thread(target=device.try_pay)
        th.start()
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_link_for_payment(idx.split('_')[0], f"{link};{qrname}"))
    return driver
    # await save_cookies(driver, phone)


def check_payment_browser(driver, idx=0):
    try:
        el = driver.find_element(By.CLASS_NAME, 'popup__header').text
        check = 0
        if el:
            while el == 'QR-код для оплаты' and check < 600:
                try:
                    el = driver.find_element(By.CLASS_NAME, 'popup__header').text
                except:
                    time.sleep(10)
                    check += 10
                    try:

                        el2 = driver.find_element(By.CLASS_NAME, 'order-fail').text
                        print(el2)
                        el = driver.find_element(By.CLASS_NAME, 'order-fail__text').text
                    except:
                        el = 'Good sale'
                time.sleep(10)
                check += 10
            if check < 600:
                page = driver.page_source
                soup = BeautifulSoup(page, "html.parser")
                # with open('test.txt', 'w', encoding='utf-8') as f:
                #     f.write(page)
                tit = ''
                for tag in soup.findAll('div', class_='order-fail'):
                    tit = tag.find('h1', class_='order-fail__title').text
                if tit == 'К сожалению, Ваш платёж не удался!':
                    payment = 'Платеж не удался, заказ отменен'
                else:
                    payment = 'Оплата успешна'
                #loop = asyncio.get_event_loop()
                #loop.run_until_complete(send_fail_payment(idx.split('_')[0], payment))
                return driver, payment
            else:
                return driver, 'error check payment'
        else:
            return driver, 'error no name'
    except:
        return driver, 'error check payment'


def make_buyout_browser(args_):
    st_time = time.time()
    bid = args_['bid']
    idx = args_['idx']
    keywords = args_['keywords']
    link = args_['link']
    address = args_['address']
    count = args_['count']
    phone = args_['phone']
    proxy = args_['proxy']
    user_agent = args_['user_agent']
    payment_type = args_['payment_type']

    product_id = link.split('catalog/')[1].split('/')[0]
    print(f'{idx}; get_open_browser')

    # driver.get_screenshot_as_file(f'data/qr_images/{name}.png')
    try:
        driver = get_open_browser(proxy, user_agent)
        driver = set_cookies(driver, phone)

        name = datetime.today().strftime("%H%M%S")
        time.sleep(10)
        print(f'{idx}; clear cart')
        driver = go_to_cart(driver)
        time.sleep(5)
        driver = clear_cart(driver)
        time.sleep(5)
        """add product in liked"""
        print(f'{idx}; find_and_add_products')
        driver, is_find = find_and_add_products(driver, keywords, link)
        if not is_find:
            print('NOT find')
            time.sleep(3)
            keywords = get_brand_of_product(link)
            print(f'{idx}; find_and_add_products2')
            find_and_add_products(driver, keywords, link, is_brand=True)
        """sleep after like"""
        #print(f'{idx}; sleep')
        #time.sleep(random.randint(3600, 18000))
        #time.sleep(10)
        """add more products in liked"""
        print(f'{idx}; delete_from_liked')
        driver = open_liked(driver)
        time.sleep(5)
        driver = delete_from_liked(driver, product_id)
        time.sleep(5)
        print(f'{idx}; add_to_cart')
        driver, find = add_to_cart(driver, product_id)
        if not find:
            driver.get(link)
            time.sleep(10)
            click_like_btn(driver)
            driver = open_liked(driver)
            time.sleep(5)
            driver = delete_from_liked(driver, product_id)
            time.sleep(5)
            print(f'{idx}; add_to_cart')
            driver, find = add_to_cart(driver, product_id)
        time.sleep(5)
        driver = go_to_cart(driver)
        time.sleep(5)
        find = check_is_product_in_cart(driver, product_id)
        if not find:
            driver.refresh()
            time.sleep(10)
            find = check_is_product_in_cart(driver, product_id)
            if not find:
                driver.refresh()
                time.sleep(20)
                find = check_is_product_in_cart(driver, product_id)
                if not find:
                    driver.get(link)
                    time.sleep(10)
                    click_like_btn(driver)
                    driver = open_liked(driver)
                    time.sleep(5)
                    driver = delete_from_liked(driver, product_id)
                    time.sleep(5)
                    print(f'{idx}; add_to_cart')
                    driver, find = add_to_cart(driver, product_id)
                    time.sleep(5)
                    driver = go_to_cart(driver)
                    time.sleep(10)
                    find = check_is_product_in_cart(driver, product_id)
                    if not find:
                        return False, 'error cart'
        # print(f'{idx}; change_count_in_cart')
        # driver = change_count_in_cart(driver, count)
        # time.sleep(5)
        print(f'{idx}; change_address_ship')
        driver, check = change_address_ship(driver, address)
        if not check:
            return False, f'error cant choice pvz on maps'
        time.sleep(5)
        print(f'{idx}; set_payment_method')
        #time.sleep(3)
        set_payment_method(driver)
        time.sleep(5)
        price = get_price(driver)
        status = {'status': 'process', 'price': price, 'receipt': 0, 'order_date': datetime.today().strftime("%d.%m.%Y %H:%M:%S")}
        set_status_of_buyout(idx, status)

        print(f'{idx}; order')
        driver = get_qr_for_pay(driver, idx, payment_type)
        print(f'{idx}; wait payment')
        driver, payment = check_payment_browser(driver, idx)
        write_log(f'payment {datetime.today().strftime("%d.%m.%Y %H:%M:%S")} {payment}')
        set_date_buyout(idx)
        print('FINISH', time.time() - st_time)
        if 'error' not in payment:
            return True, payment
        elif payment == 'error check payment':
            return True, payment
        else:
            return False, payment
        # status_buyout_complete[phone] = True
        # status_buyout_complete[f'{phone}error'] = 'all good'
        # add_to_cart_status[phone] = True
    except Exception as e:
        try:
            save_cookies(driver, phone)
            driver.close()
        except:
            pass
        return False, f'error {e}'
        # add_to_cart_status[phone] = True
        # status_buyout_complete[phone] = False
        # status_buyout_complete[f'{phone}error'] = e
