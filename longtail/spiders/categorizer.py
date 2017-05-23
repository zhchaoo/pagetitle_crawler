# -*- coding: utf-8 -*-
import scrapy
import codecs
import csv

from urlparse import urlparse
from longtail.items import TailItem

# key : priority
KEY_MAPS = {
    "色情": {
        "激情": 2,
        "福利": 2,
        "A片": 2,
        "黄色": 2,
        "草榴": 2,
        "三级": 1,
        "av": 1,
        "AV": 1,
        "伦理": 1,
        "撸": 1,
        "淫": 1,
        "啪啪啪": 1,
        "18禁止": 1,
        "Sex": 1,
        "sex": 1,
        "色": 1,
        "成人": 1,
        "人体": 1,
    },
    "博彩": {
        "博彩": 4,
        "彩票": 4,
        "六合彩": 3,
        "开奖": 2,
        "双色球": 2,
        "中彩": 1,
        "彩": 1,
    },
    "小说": {
        "小说": 3,
        "书": 1,
        "阅读": 1,
        "文学": 2,
        "章节": 2,
    },
    "下载": {
        "下载": 1,
        "软件": 1,
    },
    "直播": {
        "直播": 1,
    },
    "购物": {
        "特卖": 2,
        "热卖": 2,
        "正品": 1,
        "货到": 1,
        "淘": 1,
    },
    "漫画": {
        "漫画": 3,
    }
}


class CategorizerSpider(scrapy.Spider):
    name = "categorizer"
    start_urls = []

    def __init__(self, max_pages=None, database_dir='./data', *args, **kwargs):
        super(CategorizerSpider, self).__init__(*args, **kwargs)
        url_file = codecs.open(kwargs['file'], "rb", "utf-16")
        url_reader = csv.reader(url_file)
        head_line = True
        for line in url_reader:
            if head_line:
                head_line = False
                continue
            else:
                self.start_urls.append("http://" + line[1])
                # self.start_urls.append(line[0])

    @staticmethod
    def _parse_category(text):
        category_map = {}
        category = ""
        for cat, maps in KEY_MAPS.items():
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
