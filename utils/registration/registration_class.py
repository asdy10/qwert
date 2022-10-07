import asyncio
import threading
import time

from browser.cookies_browser import get_open_browser, save_cookies
from browser.registration_browser import start_registration, enter_code, check_code, resend_code, set_name_account


class Registration:
    def __init__(self, phone):
        phone = phone.replace('+7', '')
        self.phone = phone
        self.code = None
        self.driver = None

    # async def wait_commands(self):
    #     while True:
    #         await asyncio.sleep(10)

    def wait_commands(self):
        while True:
            time.sleep(10)

    def set_phone(self, phone):
        self.phone = phone

    def get_phone(self):
        return self.phone

    def set_code(self, code):
        self.code = code

    def get_code(self):
        return self.code

    def set_browser(self, proxy, user_agent):
        self.driver = get_open_browser(proxy, user_agent)
        if self.driver == False:
            return False
        else:
            return True

    def start_registration(self):
        self.driver = start_registration(self.driver, self.phone)
        if self.driver == False:
            return False
        else:
            return True

    def enter_code(self):
        self.driver = enter_code(self.driver, self.code)
        if self.driver == False:
            return False
        else:
            return True

    def set_name(self, male, name, lastname):
        set_name_account(self.driver, male, name, lastname)

    def check_code(self):
        return check_code(self.driver)

    def resend_code(self):
        resend_code(self.driver)

    def save_cookie(self):
        save_cookies(self.driver, self.phone)

    def close(self):
        self.driver.close()


class RegistrationThreading:

    def new_reg(self, phone):
        self.__dict__[phone] = Registration(phone)
        # print('set', self.__dict__)

    def get_reg(self, phone):
        # print('get', self.__dict__)
        return self.__dict__[phone]


reg = RegistrationThreading()
