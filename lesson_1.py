import time
import json
import requests as rq

def get_url(url, params):
    while True:
        try:
            resp: rq.Response = rq.get(url, params)
            if resp.status_code != 200:
                raise Exception
            time.sleep(0.1)
            return resp
        except Exception:
            time.sleep(0.25)

def parse(start_url, params):
    url = start_url
    params = params
    data_list = []
    while url:
        resp = get_url(url, params)
        data = resp.json()
        data_list.extend(data.get("results"))
        url = data.get('next')
        if params:
            params = {}
    return data_list


category_url = 'https://5ka.ru/api/v2/categories/'
url = 'https://5ka.ru/api/v2/special_offers/?store=&records_per_page=12&page=1&categories=&ordering=&price_promo__gte=&price_promo__lte=&search='

categories = rq.get(category_url).json()

for cat in categories:
    with open(f'categories/category {cat["parent_group_code"]}.json', 'w', encoding='UTF-8') as file:
        params = {'records_per_page': 20, 'categories': cat.get('parent_group_code')}
        data = parse(url, params)
        cat['products'] = data
        json.dump(cat, file, ensure_ascii=False)