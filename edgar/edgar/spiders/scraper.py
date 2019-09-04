#!/usr/bin/python3

import scrapy
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib.parse import urlencode

DOMAIN = 'https://www.sec.gov'
EDGAR_URL = DOMAIN + '/cgi-bin/browse-edgar'

class Scraper(scrapy.Spider):
    name = 'edgar'
    # start_urls = ['https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001166559&owner=exclude']
    def __init__(self, cik='0001166559', *args, **kwargs):
        super(Scraper, self).__init__(*args, **kwargs)
        query_str = urlencode({
            'CIK': cik,
            'action': 'getcompany',
            'owner': 'exclude'
        }, doseq=True)
        self.start_urls = [EDGAR_URL + '?' + query_str]

    def parse(self, response):
        document = response.css('table.tableFile2 a::attr(href)').get()
        print('###########################', document)
        if document:
            yield response.follow(DOMAIN + document, self.parse)

# if __name__ == '__main__':
#     if len(sys.argv) != 2:
#         print('Usage: ./webscraper [CIK]')
#
#     cik = sys.argv[1]
#     process = CrawlerProcess({
#         'FEED_FORMAT': 'json',
#         'FEED_URI': 'result.json'
#     })
#     process.crawl(Scraper, cik=cik)
#     process.start
