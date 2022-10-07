import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from browser.cookies_browser import get_open_browser, set_cookies


def get_code_delivery(phone, proxy, user_agent):
    #product_id = link.split('catalog/')[1].split('/')[0]

    try:
        driver = get_open_browser(proxy, user_agent)
        driver = set_cookies(driver, phone)
        driver.get('https://www.wildberries.ru/lk/myorders/delivery')
        time.sleep(5)
        code = driver.find_element(By.CLASS_NAME, 'delivery-code__value').text
        driver.close()
        return code
    except:
        return 0


def get_status_buyout(phone, proxy, user_agent):
    driver = get_open_browser(proxy, user_agent)
    driver = set_cookies(driver, phone)
    # time.sleep(3)
    # for i in driver.find_elements(By.CLASS_NAME, 'navbar-pc__link'):
    #     try:
    #         if i.get_attribute('href') == 'https://www.wildberries.ru/lk':
    #             actions = ActionChains(driver)
    #             actions.move_to_element(i).perform()
    #     except:
    #         pass
    # time.sleep(2)
    # discount = driver.find_element(By.CLASS_NAME, 'profile-menu__sale').text
    # discount = discount.split('%')[0]
    driver.get('https://www.wildberries.ru/lk/myorders/delivery')
    time.sleep(10)
    data = {}
    for i in driver.find_elements(By.CLASS_NAME, 'goods-list-delivery__info'):
        el = i.find_element(By.TAG_NAME, 'img')
        product_id = el.get_attribute('src').split('/images')[0].split('/')[-1]
        text = i.find_element(By.CLASS_NAME, 'goods-list-delivery__price-status').text
        data[product_id] = text
    el = driver.find_elements(By.CLASS_NAME, 'delivery-qr__code')
    for i in el:
        try:
            res = i.get_attribute('src')
            data['qr'] = res.split(',')[1]
        except:
            pass
    driver.close()
    return data
