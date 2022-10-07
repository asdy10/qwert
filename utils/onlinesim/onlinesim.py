import time

from onlinesimru import Driver

from data.config import ONLINE_SIM_TOKEN


def get_number():
    driver = Driver(ONLINE_SIM_TOKEN).numbers()
    tzid = driver.get(service='Wildberries', number=True)
    print(tzid, tzid['number'])
    return tzid


def get_code(tzid):
    driver = Driver(ONLINE_SIM_TOKEN).numbers()
    code = driver.wait_code(tzid['tzid'])
    print(code)
    if len(code) > 4:
        return code[-4:]
        code = driver.wait_code(tzid['tzid'])
    # time.sleep(5)
    # print(code)
    return code
