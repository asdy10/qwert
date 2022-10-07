import time

import pyperclip
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By

from browser.cookies_browser import get_open_browser, set_cookies, save_cookies


def open_purchase(driver):
    driver.get('https://www.wildberries.ru/lk/myorders/archive')
    time.sleep(10)
    # for i in driver.find_elements(By.CLASS_NAME, 'navbar-pc__link'):
    #     try:
    #         if i.get_attribute('href') == 'https://www.wildberries.ru/lk':
    #             actions = ActionChains(driver)
    #             actions.move_to_element(i).perform()
    #             time.sleep(1)
    #             for j in driver.find_elements(By.CLASS_NAME, 'profile-menu__link'):
    #                 try:
    #                     if j.get_attribute('href') == 'https://www.wildberries.ru/lk/myorders/archive':
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


def make_review_browser(args):
    try:
        images = args['images']
        link = args['link']
        proxy = args['proxy']
        user_agent = args['user_agent']
        phone = args['phone']
        stars = args['stars']
        text = args['text']
        if images != '0':
            images = images.split(';')
        product_id = link.split('catalog/')[1].split('/')[0]
        print('review get_open_browser')
        driver = get_open_browser(proxy, user_agent)
        print('review set_cookies')
        driver = set_cookies(driver, phone)
        time.sleep(3)
        print('review open_purchase')
        driver = open_purchase(driver)
        time.sleep(5)
        complete = False
        try:
            actions = ActionChains(driver)
            print(driver.find_elements(By.CLASS_NAME, 'archive-item__content'))
            for i in driver.find_elements(By.CLASS_NAME, 'archive-item__content'):
                if i.find_element(By.CLASS_NAME, 'archive-item__img-wrap').get_attribute('data-popup-nm-id') == product_id:
                    print('find id')
                    actions.move_to_element(i).perform()
                    time.sleep(1)
                    i.find_element(By.CLASS_NAME, 'archive-item__btn').click()
                    time.sleep(10)
                    """stars"""
                    stars_el = driver.find_elements(By.CLASS_NAME, 'rate-star__item')
                    print('stars')
                    stars_el[5-stars].click()
                    time.sleep(1)
                    """comment"""
                    print('text')
                    review_text = driver.find_element(By.ID, 'NewComment')
                    review_text.clear()
                    review_text.click()
                    JS_ADD_TEXT_TO_INPUT = """
                      var elm = arguments[0], txt = arguments[1];
                      elm.value += txt;
                      elm.dispatchEvent(new Event('change'));
                      """

                    #browser = webdriver.Chrome('C:\\Python37\\chromedriver.exe')
                    #browser.get("https://google.com/")
                    #elem = browser.find_element_by_name('q')
                    #driver.execute_script(JS_ADD_TEXT_TO_INPUT, review_text, text)
                    pyperclip.copy(text)
                    act = ActionChains(driver)
                    print('enter text')
                    act.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                    # for i1 in text:
                    #     review_text.send_keys(i1)
                    #     time.sleep(0.15)
                    time.sleep(2)
                    """image"""
                    print('image', images)
                    if images != '0':

                        for i2 in range(5):
                            try:
                                uploadElement = driver.find_element(By.ID, "img-load")
                                uploadElement.send_keys(images[i2])
                                time.sleep(3)
                                driver.find_element(By.CLASS_NAME, 'btn-main').click()
                                time.sleep(2)
                            except:
                                pass

                    print('ready')
                    j = driver.find_element(By.CLASS_NAME, 'popup__btn-main')
                    actions.move_to_element(j).perform()
                    j.click()
                    time.sleep(3)
                    complete = True
            time.sleep(5)
            save_cookies(driver, phone)
            driver.close()
            return complete
        except Exception as e:
            print(e)
            try:
                save_cookies(driver, phone)
                driver.close()
            except:
                pass
            return False
    except Exception as e:
        print(e)
        try:
            save_cookies(driver, phone)
            driver.close()
        except:
            pass
        return False
