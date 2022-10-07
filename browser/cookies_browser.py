import asyncio
import os
import pickle
import time

# from selenium import webdriver
# from seleniumwire import webdriver
import seleniumwire.undetected_chromedriver as webdriver
#from webdriver_manager.chrome import ChromeDriverManager
import logging
#import undetected_chromedriver as uc


def get_cookies(phone, driver):
    driver.get('https://www.wildberries.ru/security/login?returnUrl=https%3A%2F%2Fwww.wildberries.ru%2F')
    s = input()
    time.sleep(1)
    pickle.dump(driver.get_cookies(), open(f'cookies_{phone}', 'wb'))
    time.sleep(5)
    driver.close()


def save_cookies(driver, phone):
    time.sleep(1)
    dir_ = os.path.abspath(os.curdir)
    pickle.dump(driver.get_cookies(), open(f'{dir_}\\browser\\cookies\\cookies_{phone}', 'wb'))
    time.sleep(1)


def set_cookies(driver, phone):
    driver.get('https://www.wildberries.ru/')
    time.sleep(3)
    dir_ = os.path.abspath(os.curdir)
    for cookie in pickle.load(open(f'{dir_}\\browser\\cookies\\cookies_{phone}', 'rb')):
        driver.add_cookie(cookie)
    time.sleep(3)
    driver.refresh()
    time.sleep(10)
    return driver


def get_open_browser(proxy, user_agent):
    logging.getLogger('WDM').setLevel(logging.NOTSET)
    if len(user_agent) < 10:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    if len(proxy) > 10:
        part1, part2 = proxy.split('@')
        username, password = part1.split(':')
        ip, port = part2.split(':')

        proxy = f'{username}:{password}@{ip}:{port}'
        options = {
            'proxy': {
                'https': f'https://{proxy}',
            },
            "backend": "mitmproxy",
            "disable_capture": True,
            "verify_ssl": False,
            "connection_keep_alive": False,
            "max_threads": 3,
            "connection_timeout": None,
            '--user-agent': user_agent,
            'mitm_http2': False
        }
    else:
        options = {
            'disable_capture': True,
            '--user-agent': user_agent,
            'mitm_http2': False
        }
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(seleniumwire_options=options)
    #driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options, seleniumwire_options=options)
    driver.maximize_window()
    driver.get('https://google.com')
    time.sleep(1)
    return driver
