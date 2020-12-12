from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from .items import HhVacancyItem, HhCompanyItem
from .items import InstagramHashtagItem, InstagramHashtagMediaItem


def company_url(text):
    return urljoin('https://hh.ru', text)

class HhVacancyLoader(ItemLoader):
    default_item_class = HhVacancyItem
    vacancy_url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = Join()
    description_out = Join()
    company_url_in = MapCompose(company_url)
    company_url_out = TakeFirst()

class HhCompanyLoader(ItemLoader):
    default_item_class = HhCompanyItem
    company_url_out = TakeFirst()
    company_name_out = TakeFirst()
    company_site_out = TakeFirst()
    company_description_out = Join()

class InstagramHashtagLoader(ItemLoader):
    default_item_class = InstagramHashtagItem
    default_output_processor = TakeFirst()

class InstagramHashtagMediaLoader(ItemLoader):
    default_item_class = InstagramHashtagMediaItem
    default_output_processor = TakeFirst()