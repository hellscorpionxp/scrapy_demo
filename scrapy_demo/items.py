# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class QianlimaScrapyItem(scrapy.Item):
  # define the fields for your item here like:
  # name = scrapy.Field()
  type = scrapy.Field()
  filename = scrapy.Field()
  owner = scrapy.Field()
  winner = scrapy.Field()
  org = scrapy.Field()
  update_time = scrapy.Field()
  body = scrapy.Field()
