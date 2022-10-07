import time

from utils.connect_tg_with_browser.aggregator import agg
from utils.db_get_info.get_set_info_db import create_message, get_bid_, create_browser
from utils.onlinesim.onlinesim import get_number, get_code
from utils.proxy_configurator.proxy_configurator import change_proxy_ip
from utils.registration.get_name import get_name_lastname_agent
from utils.registration.registration_class import Registration


def script_reg_account(cid, m, w):

    create_message(cid, 'Сейчас начнется регистрация')
    st_time = time.time()
    if m > 0:
        for i in range(m):

            name, lastname, user_agent = get_name_lastname_agent('man')
            pid, proxy = agg.get_free_proxy(user_agent)
            while proxy == 0:
                pid, proxy = agg.get_free_proxy(user_agent)
            try:
                start_reg(cid, proxy, 'man', name, lastname, user_agent)
            except:
                print('error with add new acc Man')
            agg.set_free_proxy(pid)
    if w > 0:
        for i in range(w):
            name, lastname, user_agent = get_name_lastname_agent('woman')
            pid, proxy = agg.get_free_proxy(user_agent)
            while proxy == 0:
                pid, proxy = agg.get_free_proxy(user_agent)

            try:
                start_reg(cid, proxy, 'woman', name, lastname, user_agent)
            except:
                print('error with add new acc Woman')
            agg.set_free_proxy(pid)
    print(time.time() - st_time)


def start_reg(cid, proxy, male, name, lastname, user_agent):
    try:
        st_time = time.time()
        tzid = get_number()
        phone = tzid['number'].replace('+7', '')
        reg = Registration(phone)
        reg.set_browser(proxy, user_agent)
        print('start reg')
        reg.start_registration()
        print('wait code')
        code = get_code(tzid)
        print('end reg')
        res = end_reg(reg, code, cid, phone, proxy, user_agent, male, name, lastname)
        if not res:
            print('code error')
            time.sleep(60)
            reg.resend_code()
            time.sleep(10)
            code = get_code(tzid)
            res2 = end_reg(reg, code, cid, phone, proxy, user_agent, male, name, lastname)
            if not res2:
                reg.close()
            else:
                print('set name')
                reg.set_name(male, name, lastname)
                reg.close()
        else:
            print('set name')
            reg.set_name(male, name, lastname)
            reg.close()
        #change_proxy_ip(proxy, user_agent)
        print(time.time() - st_time)
    except Exception as e:
        print(e)
        try:
            reg.close()
        except:
            pass


def end_reg(reg_, code, cid, phone, proxy, user_agent, male, name, lastname):
    print(code, cid, phone, proxy, user_agent, male, name, lastname)
    reg_.set_code(code)
    reg_.enter_code()
    time.sleep(10)
    res = reg_.check_code()
    if res == 'True':
        print('enter ok')
        time.sleep(5)
        reg_.save_cookie()
        bid = get_bid_()[-1] + 1
        print('create browser')
        print(bid, phone, proxy, user_agent, male, f'{name}:{lastname}')
        create_browser(bid, phone, proxy, user_agent, male, f'{name}:{lastname}', 0)
        #create_message(cid, 'Вход успешен')
        return True
    elif res == 'Code error':
        return False
    else:
        create_message(cid, 'Не удалось войти')
        reg_.close()
        return True


