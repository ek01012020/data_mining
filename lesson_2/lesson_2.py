import time
import datetime
import locale
import requests as req
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pymongo as pm

class MagnitParser:

    def __init__(self,start_url):
        self.start_url = start_url
        mongo_client = pm.MongoClient('mongodb+srv://Helen:helen911@cluster0.lb92d.mongodb.net/')
        self.db = mongo_client['magnit']

    def _get(self,url):
        while True:
            try:
                resp = req.get(url)
                if resp.status_code != 200:
                    raise Exception
                time.sleep(0.1)
                return BeautifulSoup(resp.text, 'lxml')
            except Exception:
                time.sleep(0.25)

    def create_price(self, product, attr_class: str):
        price = product.find(class_=attr_class).text.split('\n')
        price = [el for el in price if el.isdigit()]
        return float('.'.join(price))

    def sale_date(self, arg):
        sale_date = arg.find('div', class_='card-sale__date').text.split('\n')
        return [el for el in sale_date if el != '']

    def create_date(self, arg):
        date_str = arg.split()
        date_str[0] = str(datetime.date.today().year)
        date_str[2] = date_str[2][0:3]
        date_str = ','.join(date_str)
        date_fmt = '%Y,%d,%b'
        return datetime.datetime.strptime(date_str, date_fmt)

    def parse(self, soup) -> dict:
        catalog = soup.find('div', class_='сatalogue__main')

        for product in catalog.findChildren('a'):
            try:
                pr_data = {
                    'url': urljoin(self.start_url, product.get('href')),
                    'promo_name': product.find(class_='card-sale__header').text,
                    'product_name': product.find(class_='card-sale__title').text,
                    'old_price': self.create_price(product,'label__price_old'),
                    'new_price': self.create_price(product,'label__price_new'),
                    'image_url': urljoin(self.start_url, product.find('img').get('data-src')),
                    'date_from': self.create_date(self.sale_date(product).pop(0)),
                    'date_to': self.create_date(self.sale_date(product).pop()),
                }
                yield pr_data
            except AttributeError:
                continue

    def run(self):
        soup = self._get(self.start_url)
        for product in self.parse(soup):
            self.save(product)

    def save(self, data: dict):
        collection = self.db['magnit']
        collection.insert_one(data)


if __name__ == '__main__':
    url = 'https://magnit.ru/promo/?geo=moskva'
    locale.setlocale(locale.LC_ALL, "ru")
    parser = MagnitParser(url)
    parser.run()