# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import requests
import time
import json
import sys
import pickle


def get_cookies():
    opts = Options()
    opts.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(chrome_options=opts)
    driver.get('https://www.wildberries.ru/security/login?returnUrl=https%3A%2F%2Fwww.wildberries.ru%2F')

    s = input()

    time.sleep(1)
    pickle.dump(driver.get_cookies(), open('cookies_myacc', 'wb'))

    time.sleep(5)
    driver.close()


def set_cookies():
    opts = Options()
    opts.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(chrome_options=opts)
    driver.get('https://www.wildberries.ru/')
    time.sleep(3)
    for cookie in pickle.load(open('cookies_myacc', 'rb')):
        driver.add_cookie(cookie)

    time.sleep(3)
    driver.refresh()
    time.sleep(10)
    driver.close()


# set_cookies()
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    set_cookies()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
