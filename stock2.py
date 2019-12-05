#coding=utf-8
import re
import urllib2 as web
import csv
import json
import re
from bs4 import BeautifulSoup
import time
from config import define
import utils
#lrb，zcfzb，xjllb,zycwzb 利润，资产负债，现金流量，主要财务指标

start_stock = 600500
end_stock = 600502
table_names = ['lrb','zcfzb','xjllb']
def downloadData():
    #判断是否有更新(最新季度？)，存在，再下载
    for talbeName in table_names:
        for count in range(start_stock,end_stock):
            url = 'http://quotes.money.163.com/service/' + talbeName + '_' +str(count)+'.html'
            while True:
                try:
                    content = web.urlopen(url,timeout=2).read()
                    #print(content)
                    a_utf_8 = content.decode('gb2312').encode('utf-8')
                    with open(str(count)+ talbeName + '.csv','wb') as f:
                        f.write(a_utf_8)
                        f.close()
                    print(count)
                    time.sleep(1)
                    break
                except Exception as e:
                    if str(e) =='HTTP Error 404: Not Found':
                        break
                    else:
                        print(e)
                        continue

# def csvToJson(csvPath,jsonPath):
#     csvfile = open('600500lrb.csv', 'r')


def loadData(stock_code,table_name):
    table_name = table_name or 'lrb'
    if not stock_code:
        print('stock_code is null')
        return
    try:
        csvfile = open(stock_code + table_name + '.csv', 'r')
    except Exception as e:
        print(stock_code + ' open wrong')
        print(e)
        return
    dictionary = {}
    #print(re.sub(u"\\(\u4e07\u5143", "", u'向中央银行借款净增加额(万元'))
    for row in csvfile:
        #row.decode('utf-8').encode('gb2312')
        row = row.replace('--', '0')
        row = re.sub(u"\\(.*?\\)|\\(\u4e07\u5143| ", "", row.decode('utf-8'))
        array = row.split(',')
        key_zh = array[0]
        if len(array) <= 1:
            continue
        #print(key_zh)
        key = define.getTableByName(table_name)[key_zh]
        del array[0]
        for index in range(len(array)):
            try:
                array[index] = int(array[index])
            except ValueError as e:
                break
        dictionary[key] = array
        #print(key)
    #print(len(dictionary))
    #json_str = json.dumps(dictionary)
    #abc = json.loads(json_str)
    # fw = open('600500xjllb.json', 'w')
    # fw.write(json_str)
    # fw.close()
    return dictionary
    # for key in xjllb_name_dict:
    #     print(key)
    #     print(abc[xjllb_name_dict[key]])
def showYear(cur_year):
    if not cur_year:
        cur_year = time.strftime("%Y", time.localtime()) 
    cur_year = int(cur_year)
    # print('|' + 'hej'.ljust(20) + '|' + 'hej'.rjust(20) + '|' + 'hej'.center(20) + '|')
    # print('hej'.center(20, '+')) #一共有20个字符, 中间使用hej, 其他用+填充
    str_year = ''
    for index in range(1,6):
        str_year = str_year + str(cur_year - index).ljust(15)
    return str_year
    #print(str_year)

def analyseData(lrb_data,xjllb_data,zcfzb_data):
    if not lrb_data or not xjllb_data or not zcfzb_data:
        print('loss data')
        return
    
    local_time = time.localtime()
    cur_year = int(time.strftime("%Y", local_time))

    report_dates = lrb_data['report_date']
    max_count = 5
    indexes_for_cal = []
    for index in range(len(report_dates)):
        yyyymmdd = report_dates[index].split('-')
        if len(yyyymmdd) < 3:
            continue
        single_year = int(yyyymmdd[0])
        single_month = int(yyyymmdd[1]) 
        single_day = int(yyyymmdd[2])

        if single_year < cur_year and single_month == 12 and single_day == 31 and len(indexes_for_cal) < max_count:
            indexes_for_cal.append(index)

    #print(indexes_for_cal)
    print('资产负债比率（占总资产%：）'.ljust(50) + showYear(cur_year))
    str_cash_rate = ''
    for index in indexes_for_cal:
        money_funds = zcfzb_data['money_funds'][index]
        transactional_finacial_asset = zcfzb_data['transactional_finacial_asset'][index]
        derivative_finacial_asset = zcfzb_data['derivative_finacial_asset'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_cash_rate = str_cash_rate + str(utils.cal_cash_rate(money_funds,transactional_finacial_asset,derivative_finacial_asset,tatol_assets)).ljust(15)
    print(' 现金与约当现金'.ljust(50) + str_cash_rate)
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    #print('资产负债比率（占总资产%：）'.ljust(15))

    
def main():
    #downloadData()
    #print time.strftime("%Y-%m-%d", time.localtime()) 
    stock_code = '600500'
    
    
    lrb = loadData(stock_code,'lrb')
    zcfzb = loadData(stock_code,'zcfzb')
    xjllb = loadData(stock_code,'xjllb')
    analyseData(lrb_data = lrb,xjllb_data = xjllb, zcfzb_data = zcfzb)

if __name__ == '__main__':
    main()