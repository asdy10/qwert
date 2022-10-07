import requests


def change_proxy_ip(proxy_key, user_agent):
    url = f'https://mobileproxy.space/reload.html?proxy_key={proxy_key}&format=json'
    if len(user_agent) < 10:
        user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'
    headers = {'User-Agent': user_agent}
    r = requests.get(url, headers=headers).json()
    if r['status'] == 'OK':
        print('proxy changed!')
