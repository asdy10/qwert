import requests


async def get_real_price(link, browser_discount):
    try:
        product_id = link.split('catalog/')[1].split('/')[0]
        browser_discount = int(browser_discount)
        url = f'https://card.wb.ru/cards/detail?spp={browser_discount}&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,48,1,40,71&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,3,18,15,21&dest=-1029256,-102269,-1320234,-1299031&nm={product_id}'

        r = requests.get(url).json()
        # brand
        try:
            price_u = r['data']['products'][0]['extended']['basicPriceU'] / 100
        except:
            price_u = r['data']['products'][0]['priceU'] / 100
        try:
            price_client = r['data']['products'][0]['extended']['clientPriceU'] / 100
            max_discount = r['data']['products'][0]['extended']['clientSale']
        except:
            price_client = price_u
            max_discount = 0
        return price_u, price_client, max_discount
    except Exception as e:
        print(e)


def get_brand_of_product(link):
    try:
        product_id = link.split('catalog/')[1].split('/')[0]
        url = f'https://card.wb.ru/cards/detail?spp=16&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,48,1,40,71&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,3,18,15,21&dest=-1029256,-102269,-1320234,-1299031&nm={product_id}'

        r = requests.get(url).json()
        return r['data']['products'][0]['brand']
    except:
        return 0


async def check_link(link):
    test_link = ['https://www.wildberries.ru/catalog/', 'https://wildberries.ru/catalog/']
    try:
        if requests.get(link).status_code == 200 and (test_link[0] in link or test_link[1] in link):
            return True
        else:
            return False
    except:
        return False
