import requests

from data.config import YAMAPS_KEY


async def get_address_and_photo(address):
    apikey = YAMAPS_KEY
    base_url = "https://geocode-maps.yandex.ru/1.x/"
    try:
        response = requests.get(base_url, params={
            "apikey": apikey,
            "geocode": address,
            "format": "json",
        })
        #response.raise_for_status()
        address = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        r = requests.get(f'https://static-maps.yandex.ru/1.x/?l=map&pt={lon},{lat},pm2vvm&z=16')
        return address, r.content, lon, lat
    except:
        return '', '', '0', '0'


def get_coor_wb_vpz():
    url = 'https://www.wildberries.ru/webapi/spa/modules/pickups'
    cookies = """cookie: BasketUID=62cf91b6-c80d-4fee-ac6e-e44c89c434d6; _gcl_au=1.1.2035184656.1654951773; _wbauid=3717703611654951772; _ga=GA1.2.937760077.1654951773; route=1654951774.007.6749.762287|bc5b49a034e8c65a5a36b6c2a453bfa0; __wba_s=1; ___wbu=b511796f-c526-4617-89c6-769b1bf009a0.1654951780; ___wbu=5ea8e470-400c-4aa4-bb76-6d3b534cc520.1656610871; __bsa=basket-ru-42; WILDAUTHNEW_V3=DD00407934B970F1B869FD8F066DA9D299D73F851E093E83ED729300402B70D2904FAA4F10D00E4D0941BC4BF3C32C3ECCDDA58E7531C7BD1D21803DA748EB4F371FFE391C08A611A409906AEA989AA35C22E6164E4B44E33C474C721F4C88F692C0A1522B8D3657143D08B7458285A579C9ECC5C16941466DAE141B4CD4CC65AB8911A1C6CD7F728A0F516654739F4CF2FEF3AAA6D93D2B086C5483DD668AAC28C5A68412F417F7616956C3B3F284B23DC5DF73EEEB1627F7E3143760F6D3E2758BF98CA5C40ADA44A0AA1FF74CC855B737FC77FBFF13A8F654AA2B05CD817D37C68333B8E225E73A814B5F9C7557C3AA8B9C6DE1A75FD93207C34050D87DD93A654528720E7D2F57530CAA5F5AB022C1D44204E4AA7D8D27CD324BC1EC74025796D50358BDD7285B50B63122C55448E5C350851EFE2C2BC48BBBE584FF1B3F39364F2BD97FADFABCDEC15B40F52757F4E4091B; _wbSes=CfDJ8GWigffatjpAmgU4Ds4%2BnhvTeRrv9OOB29bMQ%2B26lJnXf0WZP291XMBQbctY%2F%2B%2F0NaIf2mbbr5nvvOlzROJU%2B%2B1SaJnmJrOdfouL2mRqUmGLEm7J%2BGzYgyvxc2b39xGcpCxsvvnWRL%2BOQ2AyYSeyJglbCKqBRzY8wydDwdoNW7VF; __bsa=basket-ru-42; __wbl=cityId%3D0%26regionId%3D0%26city%3D%D1%81%20%D0%9D%D0%B0%D0%B3%D0%B0%D0%B5%D0%B2%D0%BE%2C%20%D0%9D%D0%BE%D0%B2%D0%B0%D1%8F%20%D0%A3%D0%BB%D0%B8%D1%86%D0%B0%201%26phone%3D84957755505%26latitude%3D54%2C625223%26longitude%3D56%2C104452%26src%3D1; __store=117673_122258_122259_117986_1733_117501_507_3158_120762_204939_159402_2737_130744_686_1193_124731_121709; __region=64_83_4_38_80_33_70_82_86_30_69_22_66_31_40_1_48; __pricemargin=1.0--; __cpns=2_12_7_3_6_18_21; __sppfix=; __dst=-1075831_-77677_-398551_12358502; ncache=117673_122258_122259_117986_1733_117501_507_3158_120762_204939_159402_2737_130744_686_1193_124731_121709%3B64_83_4_38_80_33_70_82_86_30_69_22_66_31_40_1_48%3B1.0--%3B2_12_7_3_6_18_21%3B%3B-1075831_-77677_-398551_12358502; um=uid%3Dw7TDssOkw7PCu8K5wrfCsMK5wrTCsMKzwrA%253d%3Aproc%3D100%3Aehash%3D8249bb93d039be873a02732ef40a8424; _gid=GA1.2.1944336370.1660751634; __tm=1660822478; _dc_gtm_UA-2093267-1=1; ___wbs=089e40a2-dd96-47b7-935f-8fc00a59a851.1660811679"""
    headers = """accept: */*
accept-encoding: gzip, deflate, br
accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
referer: https://www.wildberries.ru/services/besplatnaya-dostavka?desktop=1
sec-ch-ua: "Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36
x-requested-with: XMLHttpRequest
x-spa-version: 9.3.22"""
    arr_headers = {i.split(': ')[0]: i.split(': ')[1] for i in headers.split('\n')}
    arr_cook = {i.split('=')[0]: i.split('=')[1] for i in cookies.split('; ')}
    res = requests.get(url=url, headers=arr_headers, cookies=arr_cook)
    res = res.json()['value']['pickups']
    coor_arr = []
    for i in res:
        x, y = i['coordinates']
        coor_arr.append([round(float(x), 2), round(float(y), 2)])
    return coor_arr


def get_address_and_photo_not_async(address):
    apikey = YAMAPS_KEY
    base_url = "https://geocode-maps.yandex.ru/1.x/"
    try:
        response = requests.get(base_url, params={
            "apikey": apikey,
            "geocode": address,
            "format": "json",
        })
        #response.raise_for_status()
        address = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        r = requests.get(f'https://static-maps.yandex.ru/1.x/?l=map&pt={lon},{lat},pm2vvm&z=16')
        return address, r.content, lon, lat
    except:
        return '', '', '', ''


#get_coor_wb_vpz()