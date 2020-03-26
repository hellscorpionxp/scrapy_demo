'''
Created on 2020年3月20日

@author: tony
'''
from scrapy import cmdline

if __name__ == '__main__':
  cmdline.execute(argv = ['scrapy', 'crawl', 'qianlima'])
