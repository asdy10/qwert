import time

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By


def find_and_click_by_class_name(driver, class_name):
    driver.execute_script("document.body.style.zoom='0.67'")
    actions = ActionChains(driver)
    m = driver.find_element(By.CLASS_NAME, class_name)
    actions.move_to_element(m).perform()
    time.sleep(1)
    m.click()
    time.sleep(2)
    return driver


def go_to_cart(driver):
    driver.get('https://www.wildberries.ru/lk/basket')
    time.sleep(5)
    driver.execute_script("document.body.style.zoom='0.67'")
    # for i in driver.find_elements(By.CLASS_NAME, 'navbar-pc__link'):
    #     try:
    #         if i.get_attribute('href') == 'https://www.wildberries.ru/lk/basket':
    #             actions = ActionChains(driver)
    #             actions.move_to_element(i).perform()
    #             time.sleep(1)
    #             i.click()
    #     except:
    #         pass
    # time.sleep(5)
    return driver


def clear_cart(driver):
    actions = ActionChains(driver)
    driver.execute_script("document.body.style.zoom='0.67'")
    k = driver.find_elements(By.CLASS_NAME, 'accordion__list-item')
    for i in k:
        actions.move_to_element(i).perform()
        time.sleep(1)
        clear = driver.find_element(By.CLASS_NAME, 'btn__del')
        actions.move_to_element(clear).perform()
        time.sleep(1)
        clear.click()
        time.sleep(2)
    return driver


def change_count_in_cart(driver, count):
    actions = ActionChains(driver)
    driver.execute_script("document.body.style.zoom='0.67'")
    k = driver.find_element(By.CLASS_NAME, 'accordion__list-item')
    actions.move_to_element(k).perform()
    time.sleep(1)
    plus = driver.find_element(By.CLASS_NAME, 'count__plus')
    actions.move_to_element(plus).perform()
    time.sleep(1)
    if count > 1:
        for i in range(count - 1):
            plus.click()
            time.sleep(1)
    return driver


def change_address_ship(driver, address):
    check = 0
    driver.execute_script("document.body.style.zoom='0.67'")
    while check < 3:
        try:
            check += 1
            try:
                find_and_click_by_class_name(driver, 'basket-delivery__choose-address')
                time.sleep(3)
                find_and_click_by_class_name(driver, 'popup__btn-main')
            except:
                find_and_click_by_class_name(driver, 'btn-edit')
                time.sleep(3)
                delete_all_address_ship(driver)
                time.sleep(3)
                find_and_click_by_class_name(driver, 'popup__btn-main')
            time.sleep(15)
            find_and_click_by_class_name(driver, 'ymaps-2-1-79-searchbox-input__input')
            maps_search = driver.find_element(By.CLASS_NAME, 'ymaps-2-1-79-searchbox-input__input')
            maps_search.clear()
            for i in address:
                maps_search.send_keys(i)
                time.sleep(0.10)
            maps_search.send_keys(Keys.ENTER)

            time.sleep(5)
            try:
                find_and_click_by_class_name(driver, 'ymaps-2-1-79-islets_serp-item__title')
                time.sleep(5)
            except:
                pass
            for i in range(3):
                find_and_click_by_class_name(driver, 'ymaps-2-1-79-zoom__plus')
                time.sleep(1)
            time.sleep(1)
            find_and_click_by_class_name(driver, 'address-item')
                #ymaps-2-1-79-zoom__minus
                # for i in range(4):
                #     try:
                #         driver.find_element(By.CLASS_NAME, 'ymaps-2-1-79-zoom__minus').click()
                #         time.sleep(3)
                #         find_and_click_by_class_name(driver, 'address-item')
                #         break
                #     except:
                #         pass
            time.sleep(2)
            find_and_click_by_class_name(driver, 'j-btn-select-poo')
            time.sleep(2)
            find_and_click_by_class_name(driver, 'popup__btn-main')
            time.sleep(10)
            check = 3
            return driver, True
        except Exception as e:
            print('ERROR MAPS', e)
            driver.refresh()
            time.sleep(10)
            driver.execute_script("document.body.style.zoom='0.67'")
    return driver, False


def delete_all_address_ship(driver):
    driver.execute_script("document.body.style.zoom='0.67'")
    for i in range(len(driver.find_elements(By.CLASS_NAME, 'history__menu'))):
        find_and_click_by_class_name(driver, 'history__menu')
        find_and_click_by_class_name(driver, 'address-delete')
    return driver


def set_payment_method(driver):
    try:
        driver.execute_script("document.body.style.zoom='0.67'")
        find_and_click_by_class_name(driver, 'j-btn-choose-pay')
        time.sleep(3)
        els = driver.find_elements(By.CLASS_NAME, 'methods-pay__text')
        for i in els:
            if 'Оплата по QR-коду' in i.text:
                i.click()
        time.sleep(2)
        find_and_click_by_class_name(driver, 'popup__btn-main')
        time.sleep(3)
    except:
        pass


def get_price(driver):
    try:
        driver.execute_script("document.body.style.zoom='0.67'")
        el = driver.find_elements(By.CLASS_NAME, 'b-top__total')
        for i in el:
            try:
                print(i.text)
                price = i.text#2 859 ₽
                nums = [str(j) for j in range(10)]
                real_price = ''
                for j in price:
                    if j in nums:
                        real_price += j
                return real_price
            except:
                pass
        return 0
    except Exception as e:
        print(e)
        return 0


def check_is_product_in_cart(driver, id):
    try:
        driver.execute_script("document.body.style.zoom='0.67'")
        el = driver.find_elements(By.CLASS_NAME, 'list-item__good')
        for i in el:
            try:
                j = i.find_element(By.TAG_NAME, 'a')
                if str(id) in j.get_attribute('href'):
                    return True
            except:
                pass
        return False
    except:
        return False