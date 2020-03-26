# -*- coding: utf-8 -*-
'''
Created on 2020年3月5日

@author: tony
'''
import json
import os

import MySQLdb
import chardet
import scrapy
from scrapy.loader import ItemLoader

from scrapy_demo.items import QianlimaScrapyItem


class QianlimaSpider(scrapy.Spider):
  name = "qianlima"
  allowed_domains = ["qianlima.com"]

  def start_requests(self):
    return [scrapy.FormRequest(url = 'http://center.qianlima.com/login_post.jsp',
                               formdata = {'username':'xxx',
                                           'password':'yyy',
                                           'rem_login':'1'},
                               callback = self.after_login)]

  def after_login(self, response):
    yield scrapy.FormRequest(url = 'http://center.qianlima.com/zb_db_library_post.jsp',
                             formdata = {'q':'超声',
                                         'userName':'xxx',
                                         'dengji':'20',
                                         'areaId':'0',
                                         'yearId':'2018',
                                         'monthId':'0',
                                         'p':'0'},
                             callback = self.paging)

  def paging(self, response):
    jsonBody = response.body
    bodyDict = json.loads(jsonBody.decode('gb2312').encode('utf-8').decode('utf-8'))
    total = bodyDict['data'][0]['totPage']
    for i in range(total):
      yield scrapy.FormRequest(url = 'http://center.qianlima.com/zb_db_library_post.jsp',
                               formdata = {'q':'超声',
                                           'userName':'xxx',
                                           'dengji':'20',
                                           'areaId':'0',
                                           'yearId':'2018',
                                           'monthId':'0',
                                           'p':'%d' % (i + 1)},
                               callback = self.parse_list_page)

  def parse_list_page(self, response):
    jsonBody = response.body
    bodyDict = json.loads(jsonBody.decode('gb2312').encode('utf-8').decode('utf-8'))
    for it in bodyDict['data']:
      if it['zhuangtai'] == '中标':
        yield scrapy.Request(it['url'], callback = self.parse_detail_page_v2)

  def parse_detail_page_v2(self, response):
    filename = response.url.split('/')[-1]
    contentid = filename.split('_')[-1].replace('.html', '')
    yield scrapy.Request('http://www.qianlima.com/common/zb_exportDoc.jsp?contentid=%s' % contentid,
                         callback = self.export_detail,
                         meta = {'contentid':contentid})

  def export_detail(self, response):
    filename = '%s.doc' % response.meta['contentid']
    if not os.path.exists('exports'):
      os.makedirs('exports')
    with open('exports/%s' % filename, 'wb') as f:
      f.write(response.body)

  def parse_detail_page(self, response):
    il = ItemLoader(item = QianlimaScrapyItem(), response = response)
    il.add_value('type', 'dr')
    filename = response.url.split("/")[-1]
    il.add_value('filename', filename)
#     if not os.path.exists('logs'):
#       os.makedirs('logs')
#     with open('logs/%s' % filename, 'wb') as f:
#       f.write(response.body.decode('gb2312').encode('utf-8'))
    il.add_value('body', response.body.decode('gb2312').encode('utf-8'))
    table = response.selector.xpath('//table[@class="table_content"]')
    trs = table.xpath('tr')
    for tr in trs:
      tds = tr.xpath('td')
      for i in range(len(tds)):
        if tds[i].xpath('span/text()').extract_first() == '招标单位:':
          il.add_value('owner', tds[i + 1].xpath('span/a/text()').extract_first())
        if tds[i].xpath('span/text()').extract_first() == '代理机构:':
          il.add_value('org', tds[i + 1].xpath('span/a/text()').extract_first())
        if tds[i].xpath('span/text()').extract_first() == '更新时间:':
          il.add_value('update_time', tds[i + 1].xpath('table/tr/td/span/text()').extract_first())
    self.persistent(il.load_item())

  def persistent(self, qianlimaItem):
    t = qianlimaItem.get('type')[0]
    filename = None
    owner = None
    org = None
    update_time = None
    body = None
    if qianlimaItem.get('filename'):
      filename = qianlimaItem.get('filename')[0]
    if qianlimaItem.get('owner'):
      owner = qianlimaItem.get('owner')[0]
    if qianlimaItem.get('org'):
      org = qianlimaItem.get('org')[0]
    if qianlimaItem.get('update_time'):
      update_time = qianlimaItem.get('update_time')[0]
    if qianlimaItem.get('body'):
      body = qianlimaItem.get('body')[0]
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = 'root', db = 'crawl', charset = 'utf8mb4')
    try:
      cur = conn.cursor()
      sql = 'insert into crawl.qianlima (type, filename, owner, org, update_time, body) values (%s, %s, %s, %s, %s, %s)'
      cur.execute(sql, (t, filename, owner, org, update_time, body))
      cur.close()
      conn.commit()
    except BaseException as e:
      print(e)
      conn.rollback()
    finally:
      conn.close()
