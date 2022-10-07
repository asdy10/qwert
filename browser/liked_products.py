import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By


def open_liked(driver):
    driver.get('https://www.wildberries.ru/lk/favorites')
    # for i in driver.find_elements(By.CLASS_NAME, 'navbar-pc__link'):
    #     try:
    #         if i.get_attribute('href') == 'https://www.wildberries.ru/lk':
    #             actions = ActionChains(driver)
    #             actions.move_to_element(i).perform()
    #             time.sleep(1)
    #             for j in driver.find_elements(By.CLASS_NAME, 'profile-menu__link'):
    #                 try:
    #                     if j.get_attribute('href') == 'https://www.wildberries.ru/lk/favorites':
    #                         actions = ActionChains(driver)
    #                         actions.move_to_element(j).perform()
    #                         time.sleep(1)
    #                         j.click()
    #                 except:
    #                     pass
    #             time.sleep(5)
    #     except:
    #         pass
    return driver


def delete_from_liked(driver, product_id):

    actions = ActionChains(driver)

    for j in range(len(driver.find_elements(By.CLASS_NAME, 'favorites-goods__item'))):
        try:
            elements = driver.find_elements(By.CLASS_NAME, 'favorites-goods__item')
            #print(elements[0].get_attribute('id'))
            if len(elements) > 1:
                el = elements[0] if str(product_id) not in elements[0].get_attribute('id') else elements[1]
                actions.move_to_element(el).perform()
                time.sleep(2)
                #if el.get_attribute('class') == 'favorites-goods__item goods-card goods-card--favorites j-favorite-good-item':
                close = el.find_element(By.CLASS_NAME, 'goods-card__remove')
                actions.move_to_element(close).perform()
                time.sleep(1)
                close.click()
                time.sleep(5)
        except Exception as e:
            print(e)
    return driver


def add_to_cart(driver, product_id):
    actions = ActionChains(driver)
    find = False
    for i in driver.find_elements(By.CLASS_NAME, 'favorites-goods__item'):
        try:
            if i.get_attribute('class') == 'favorites-goods__item goods-card goods-card--favorites j-favorite-good-item' \
                    and product_id in i.get_attribute('id'):
                actions.move_to_element(i).perform()
                time.sleep(0.5)
                add_to_cart_btn = i.find_elements(By.CLASS_NAME, 'goods-card__add-basket')
                actions.move_to_element(add_to_cart_btn[0]).perform()
                time.sleep(1)
                add_to_cart_btn[0].click()
                time.sleep(2)
                find = True
        except:
            pass
    return driver, find
