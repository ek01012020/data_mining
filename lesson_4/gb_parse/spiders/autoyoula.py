import scrapy
import pymongo
from urllib.parse import urljoin

class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    css_query = {
        'brands': '.ColumnItemList_column__5gjdt a.blackLink'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = pymongo.MongoClient('mongodb+srv://Helen:helen911@cluster0.lb92d.mongodb.net/')['parser_auto'][self.name]

    def parse(self, response):
        for link in response.css(self.css_query['brands']):
            yield response.follow(link.attrib['href'], callback=self.brand_page_parse)

    def brand_page_parse(self, response):
        for page in response.css('.Paginator_block__2XAPy a.Paginator_button__u1e7D'):
            yield response.follow(page.attrib['href'], callback=self.brand_page_parse)

        for item_link in response.css('article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'):
            yield response.follow(item_link.attrib['href'], callback=self.ads_parse)

    def ads_parse(self,response):
        title = response.css('.AdvertCard_advertTitle__1S1Ak::text').get()
        images = [image.attrib['src'] for image in response.css('figure.PhotoGallery_photo__36e_r img')]
        description = response.css('.AdvertCard_description__2bVlR .AdvertCard_descriptionInner__KnuRi::text').get()
        price = float(response.css('.AdvertCard_price__3dDCr::text').get().replace('\u2009', ''))
        charact = {sel.css('::text').getall()[0]: sel.css('::text').getall()[1] for sel in response.css('.AdvertSpecs_row__ljPcX')}
        seller_id = ''
        for script_text in response.css('script').getall():
            if script_text.find('avatar') > 0:
                seller_id = 'user/' + script_text[script_text.rfind('youlaId%22%2C%22') + 16:script_text.find('%22%2C%22avatar')]
                seller_id = urljoin('https://youla.ru/', seller_id)
                break
            if script_text.find('sellerLink') > 0:
                seller_id = script_text[script_text.rfind('sellerLink%22%2C%22') + 19:script_text.find('%22%2C%22type')].replace('%2F','/')
                seller_id = urljoin('https://auto.youla.ru/', seller_id)

        self.db.insert_one({
            'title': title,
            'images': images,
            'description': description,
            'url': response.url,
            'price': price,
            'charact': charact,
            'seller_id': seller_id
        })