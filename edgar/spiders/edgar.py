#!/usr/bin/python3

import scrapy

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.selector import Selector
from urllib.parse import urlencode

DOMAIN = 'https://www.sec.gov'
EDGAR_URL = DOMAIN + '/cgi-bin/browse-edgar'

class EdgarSpider(scrapy.Spider):
    name = 'edgar'
    def __init__(self, cik='0001166559', *args, **kwargs):
        super(EdgarSpider, self).__init__(*args, **kwargs)
        query_str = urlencode({
            'CIK': cik,
            'action': 'getcompany',
            'owner': 'exclude',
            'type': '13F-HR'
        }, doseq=True)

        self.cik = cik
        self.start_urls = [EDGAR_URL + '?' + query_str]

    def parse(self, response):
        document_path = response.xpath('//table[@class=\'tableFile2\']//a/@href').get()
        if document_path:
            yield response.follow(DOMAIN + document_path, self.parse_documents)
        else:
            raise Exception('No holdings found from', response.url)

    def parse_documents(self, response):
        table = response.xpath('//table[@class=\'tableFile\']//tr')
        table_header = table[0].xpath('//th//text()').getall()
        col_index = {}

        for index, header in enumerate(table_header):
            header = header.lower()
            if header in ['document', 'type']:
                col_index[header] = index

        for row in table:
            row_data = row.xpath('td')
            if row_data:
                type = row_data[col_index['type']].xpath('text()').get()
                document = row_data[col_index['document']].xpath('./a')
                document_text = document.xpath('text()').get() if document else ''
                if type.lower() == 'information table' and 'xml' in document_text:
                    report_path = document.xpath('@href').get()
                    yield response.follow(DOMAIN + report_path, self.parse_report)

    def parse_report(self, response):
        report = Selector(text=response.text)
        for item in report.xpath('//infotable'):
            yield {
                'name': item.xpath('./nameofissuer/text()').get(),
                'value': item.xpath('./value/text()').get()
            }
