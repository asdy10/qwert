import time
from datetime import datetime

from selenium.webdriver.common.by import By


def start_registration(driver, phone):
    try:
        driver.get('https://www.wildberries.ru/security/login')
        time.sleep(10)
        text = driver.find_element(By.CLASS_NAME, 'input-item')

        for i in str(phone):
            text.send_keys(i)
            time.sleep(0.1)

        time.sleep(5)
        el = driver.find_element(By.CLASS_NAME, 'login__btn')
        el.click()
    except Exception as e:
        print(e)
        return False
    return driver


def enter_code(driver, code):
    try:
        text = driver.find_element(By.CLASS_NAME, 'j-input-confirm-code')
        text.clear()
        time.sleep(0.5)
        for i in str(code):
            text.send_keys(i)
            time.sleep(0.15)
        time.sleep(5)
    except Exception as e:
        print(e)
        return False
    return driver


def check_code(driver):
    find = 'False'
    for i in driver.find_elements(By.CLASS_NAME, 'navbar-pc__link'):
        try:
            if i.get_attribute('href') == 'https://www.wildberries.ru/lk':
                find = 'True'
        except:
            pass
    if find == 'True':
        return find
    else:
        for i in driver.find_elements(By.CLASS_NAME, 'form-block__message'):
            try:
                if i.text == 'Неверный код':
                    find = 'Code error'
            except:
                pass
        if find == 'False':
            driver.get_screenshot_as_file(f'error{datetime.today().strftime("%H%M%S")}.png')
        return find


def resend_code(driver):
    btn = driver.find_element(By.ID, 'requestCode')
    btn.click()


def set_name_account(driver, male, name, lastname):
    driver.get('https://www.wildberries.ru/lk/details')
    time.sleep(5)
    driver.find_element(By.CLASS_NAME, 'personal-data__edit--name').click()
    time.sleep(5)

    text = driver.find_element(By.ID, 'Item.FirstName')
    text.clear()
    time.sleep(0.5)
    for i in str(name):
        text.send_keys(i)
        time.sleep(0.1)
    time.sleep(1)
    try:
        text = driver.find_element(By.ID, 'Item.LastName')
        text.clear()
        time.sleep(0.5)
        for i in str(lastname):
            text.send_keys(i)
            time.sleep(0.1)
        time.sleep(1)
    except:
        pass
    driver.find_element(By.CLASS_NAME, 'btn-main').click()
    time.sleep(3)
    male_name = 'Male' if male == 'man' else 'Female'
    btns1 = driver.find_elements(By.CLASS_NAME, 'personal-data__radio')
    for j in btns1:
        btns = j.find_elements(By.TAG_NAME, 'input')
        for i in btns:
            if i.get_attribute('value') == male_name:
                j.find_element(By.CLASS_NAME, 'radio-with-text__decor').click()
    time.sleep(3)

