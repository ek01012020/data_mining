import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse import settings
from gb_parse.spiders.autoyoula import AutoyoulaSpider
from gb_parse.spiders.hh import HhSpider
from gb_parse.spiders.instagram import InstagramSpider
from gb_parse.spiders.instagram_users import InstagramUsersSpider

if __name__ == '__main__':
    dotenv.load_dotenv('../.env')
    users = ['lenochka_kuznecova_', 'olgaagranovskaya']
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    #crawl_proc.crawl(AutoyoulaSpider)
    #crawl_proc.crawl(HhSpider)
    crawl_proc.crawl(InstagramSpider,
                      list_users=users,
                      login=os.getenv('INST_LOGIN'),
                      password=os.getenv('INST_PSWD'))
    crawl_proc.start()