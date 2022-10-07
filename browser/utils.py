import asyncio
import time

import qrcode
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By

from browser.cart_products import delete_all_address_ship
import cv2
import numpy as np


async def check_address(driver, address):
    try:
        await find_and_click_by_class_name(driver, 'basket-delivery__choose-address')
        await asyncio.sleep(3)
        await find_and_click_by_class_name(driver, 'popup__btn-main')
    except:
        await find_and_click_by_class_name(driver, 'btn-edit')
        await asyncio.sleep(3)
        await delete_all_address_ship(driver)
        await asyncio.sleep(3)
        await find_and_click_by_class_name(driver, 'popup__btn-main')
    await asyncio.sleep(8)
    await find_and_click_by_class_name(driver, 'ymaps-2-1-79-searchbox-input__input')
    maps_search = driver.find_element(By.CLASS_NAME, 'ymaps-2-1-79-searchbox-input__input')
    maps_search.clear()
    for i in address:
        maps_search.send_keys(i)
        await asyncio.sleep(0.10)
    maps_search.send_keys(Keys.ENTER)
    title, description = '', ''
    await asyncio.sleep(5)
    try:
        await find_and_click_by_class_name(driver, 'ymaps-2-1-79-searchbox-list-button')
        title = driver.find_element(By.CLASS_NAME, 'ymaps-2-1-79-islets_serp-item__title').text
        description = driver.find_element(By.CLASS_NAME, 'ymaps-2-1-79-islets_card__description').text
    except:
        print('no address')
    if title and description:
        return driver, f'{description}, {title}'


def find_and_click_by_class_name(driver, class_name):
    actions = ActionChains(driver)
    m = driver.find_element(By.CLASS_NAME, class_name)
    actions.move_to_element(m).perform()
    time.sleep(1)
    m.click()
    time.sleep(2)
    return driver


def qr_decode(image):
    inputImage = cv2.imread(image)
    qrDecoder = cv2.QRCodeDetector()
    data, _, rectifiedImage = qrDecoder.detectAndDecode(inputImage)
    #rectifiedImage = np.uint8(rectifiedImage)
    #cv2.imwrite("Rectified QRCode.png", rectifiedImage)
    return data


def qr_code(data, imgname):
    img = qrcode.make(data)
    img.save(imgname)


