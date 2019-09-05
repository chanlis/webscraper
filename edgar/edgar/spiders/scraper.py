#!/usr/bin/python3

import scrapy
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.selector import Selector
from urllib.parse import urlencode

DOMAIN = 'https://www.sec.gov'
EDGAR_URL = DOMAIN + '/cgi-bin/browse-edgar'

RESULTS = 'results'
DOCUMENTS = 'documents'
REPORT = 'report'

class EdgarSpider(scrapy.Spider):
    name = 'edgar'
    def __init__(self, cik='0001166559', *args, **kwargs):
        super(Scraper, self).__init__(*args, **kwargs)
        query_str = urlencode({
            'CIK': cik,
            'action': 'getcompany',
            'owner': 'exclude',
            'type': '13F-HR'
        }, doseq=True)
        self.start_urls = [EDGAR_URL + '?' + query_str]
        self.state = RESULTS

    def parse(self, response):
        if self.state == RESULTS:
            yield from self.parse_results(response)
        elif self.state == DOCUMENTS:
            yield from self.parse_documents(response)
        elif self.state == REPORT:
            yield from self.parse_report(response)
        else:
            pass
            # TODO: THROW EXCEPTION(INVALID STATE)

    def parse_results(self, response):
        document_path = response.css('table.tableFile2 a::attr(href)').get()
        if document_path:
            self.state = DOCUMENTS
            yield response.follow(DOMAIN + document_path, self.parse)
        else:
            print('No holdings found.')

    def parse_documents(self, response):
        table = response.css('table.tableFile tr')
        if not table:
            # TODO: INVALID, TABLE NOT FOUND
            return

        table_header = table[0].xpath('th//text()').getall()
        col_index = {}
        for index, header in enumerate(table_header):
            if header.lower() in ['document', 'type']:
                col_index[header.lower()] = index

        for row in table:
            row_data = row.css('td')
            if row_data:
                type = row_data[col_index['type']].xpath('text()').get()
                document = row_data[col_index['document']].css('a')
                document_text = document.xpath('text()').get() if document else ''
                if type.lower() == 'information table' and 'xml' in document_text:
                    self.state = REPORT
                    report_path = document.xpath('@href').get()
                    yield response.follow(DOMAIN + report_path, self.parse)

    def parse_report(self, response):
        report = Selector(text=response.text)
        for item in report.xpath('//infotable'):
            yield {
                'name': item.xpath('./nameofissuer/text()').get(),
                'value': item.xpath('./value/text()').get()
            }

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
