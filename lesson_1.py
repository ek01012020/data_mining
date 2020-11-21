import json
import requests as rq

category_url = 'https://5ka.ru/api/v2/categories/'
url = "https://5ka.ru/api/v2/special_offers/?categories=&ordering=&page=2&price_promo__gte=&price_promo__lte=&records_per_page=12&search=&store="

categories = rq.get(category_url).json()

for cat in categories:
    with open(f'categories/{cat["parent_group_code"]}.json', 'w', encoding='UTF-8') as file:
        params = {'records_per_page': 12, 'categories': cat.get('parent_group_code')}
        resp: rq.Response = rq.get(url, params)
        data = resp.json().get("results")
        cat['products']=data
        json.dump(cat, file, ensure_ascii=False)