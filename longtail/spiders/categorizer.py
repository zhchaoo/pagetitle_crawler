# -*- coding: utf-8 -*-
import scrapy
import logging
import csv

from urlparse import urlparse
from longtail.items import TailItem
from longtail.keymaps import KeyMaps


class CategorizerSpider(scrapy.Spider):
    name = "categorizer"
    start_urls = []

    def __init__(self, max_pages=None, database_dir='./data', *args, **kwargs):
        super(CategorizerSpider, self).__init__(*args, **kwargs)
        # url_file = codecs.open(kwargs['file'], "rb", "utf-16")
        url_file = open(kwargs['file'], "rb")
        url_reader = csv.reader(url_file)
        url_index = -1
        head_line = True
        for line in url_reader:
            if head_line:
                for i in range(len(line)):
                    if "url" in line[i]:
                        url_index = i
                head_line = False
                continue
            else:
                if url_index < 0:
                    logging.error("no url founded in file")
                    exit()
                self.start_urls.append("http://" + line[url_index])
                # self.start_urls.append(line[0])

    @staticmethod
    def _parse_category(text):
        category_map = {}
        category = ""
        for cat, maps in KeyMaps.items():
            score = 0
            for key, priority in maps.items():
                score += text.count(key) * priority
            category_map[cat] = score

        max_score = 0
        for cat, score in category_map.items():
            if score > max_score:
                category = cat
                max_score = score
        return category, max_score

    def parse(self, response):
        title = response.xpath('//title/text()').extract()[0].encode('utf-8')
        category, score = self._parse_category(title)

        tail_item = TailItem()
        tail_item["url"] = response.url
        parsed_uri = urlparse(response.url)
        tail_item["domain"] = parsed_uri.hostname
        tail_item["title"] = title
        tail_item["score"] = score
        tail_item["category"] = category
        yield tail_item
