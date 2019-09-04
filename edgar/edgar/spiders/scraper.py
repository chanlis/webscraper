#!/usr/bin/python3

import scrapy
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib.parse import urlencode

DOMAIN = 'https://www.sec.gov'
EDGAR_URL = DOMAIN + '/cgi-bin/browse-edgar'

RESULTS = 'results'
DOCUMENTS = 'documents'
REPORT = 'report'

class Scraper(scrapy.Spider):
    name = 'edgar'
    # start_urls = ['https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001166559&owner=exclude']
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
                report_path = row_data[col_index['document']]
                report_path = report_path.css('a::attr(href)').get()
                report_path = report_path if report_path else ''
                print('################', type, report_path)

                if type.lower() == 'information table' and report_path.find('xml'):
                    self.state = REPORT
                    yield response.follow(DOMAIN + report_path, self.parse)

    def parse_report(self, response):
        pass

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
