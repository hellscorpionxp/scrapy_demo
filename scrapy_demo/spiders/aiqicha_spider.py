# -*- coding: utf-8 -*-
'''
Created on 2020年3月5日

@author: tony
'''
import js2xml
from js2xml.utils.vars import get_vars
import scrapy


class AiqichaSpider(scrapy.Spider):
  name = "aiqicha"
  allowed_domains = ["aiqicha.baidu.com"]

  def start_requests(self):
    return [scrapy.FormRequest(url = 'https://aiqicha.baidu.com/company_detail_33564448292419',
                               method = 'POST',
                               callback = self.after_login)]

  def after_login(self, response):
    script = response.selector.xpath('body/script[1]/text()').extract_first()
    varDict = get_vars(js2xml.parse(script, encoding = 'utf-8', debug = False))
    dataDict = varDict.get('window.pageData')
    print(dataDict)
