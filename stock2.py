#coding=utf-8
import re
import urllib2 as web
import xlwt
from bs4 import BeautifulSoup
from time import sleep
#lrb，zcfzb，xjllb 利润，资产负债表，现金流量
count = 1
for count in range(600500,600502):
    url = 'http://quotes.money.163.com/service/xjllb_'+str(count)+'.html'
    while True:
        try:
            content = web.urlopen(url,timeout=2).read()
            #print(content)
            a_utf_8 = content.decode('gb2312').encode('utf-8')
            with open(str(count)+'xjllb.txt','wb') as f:
                f.write(a_utf_8)
                f.close()
            print(count)
            sleep(1)
            break
        except Exception as e:
            if str(e) =='HTTP Error 404: Not Found':
                break
            else:
                print(e)
                continue