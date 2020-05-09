#coding=utf-8
import re
import urllib2 as web
import csv
import json
import re
from bs4 import BeautifulSoup
import time,datetime
from config import define
import utils
import os
import threading
import pandas as pd
import bs4
import stock_ts as tushare_get
import tushare as ts
import sys
import copy
# import talib
import random
reload(sys)
sys.setdefaultencoding('utf-8')
from selenium import webdriver

import heapq

class Node:
    def __init__(self,stock_code,stock_name,score,remarks=''):
        self._stock_code = stock_code
        self._stock_name = stock_name
        self._score = score
        self._remarks = remarks

    @property
    def stock_code(self):
        return self._stock_code

    @stock_code.setter
    def stock_code(self,stock_code):
        if isinstance(stock_code,str):
            self._stock_code = int(stock_code)
        elif isinstance(stock_code,int):
            self._stock_code = stock_code

    @stock_code.deleter
    def stock_code(self):
        del self._stock_code

    @property
    def score(self):
        return self._score

    @property
    def stock_name(self):
        return self._stock_name

    # @property
    # def remarks(self):
    #     return self._remarks

    def add_remarks(self,add_remark):
        self._remarks = self._remarks + add_remark


    def __str__(self):
		return '%s  %s  %s %s' %(self._stock_code,self._stock_name,self._score,self._remarks)

    def __lt__(self,other):
        if isinstance(other,Node):
            return self._score < other._score
        # return self.score < other.score

    def __gt__(self,other): 
        if isinstance(other,Node):
            return self._score > other._score

    def __eq__(self,other): 
        if isinstance(other,Node):
            return self._score == other._score

class TopKHeap(object):
    def __init__(self, k):
        self.k = k
        self.data = []

    def push(self, elem):
        if len(self.data) < self.k:
            heapq.heappush(self.data, elem)
        else:
            topk_small = self.data[0].score
            if elem.score > topk_small:
                heapq.heapreplace(self.data, elem)
    def topk(self):
        return [x for x in reversed([heapq.heappop(self.data) for x in xrange(len(self.data))])]


#lrb，zcfzb，xjllb,zycwzb 利润，资产负债，现金流量，主要财务指标

g_start_stock = 0
g_end_stock = 1000

g_stock_head_codes = ['000','001','002','003','300','600','601','603']#600最多，可以加线程
g_table_names = ['lrb','zcfzb','xjllb']
g_stock_codes = {}
g_business_data = []
g_dividend_data = {}
g_is_test = False
if g_is_test:
    g_stock_head_codes = ['600']
    g_start_stock = 288
    g_end_stock = 289

# mylock = thread.allocate_lock() 

def downloadFinanceData():
    #判断是否有更新(最新季度？)，存在，再下载
    # 创建线程
    try:
        thread_list = []
        for stock_head in g_stock_head_codes:
            for talbeName in g_table_names:
                t1= threading.Thread(target=downloadFinanceThread,args=(str(stock_head),str(talbeName),))
                thread_list.append(t1)

        for t in thread_list:
            # t.setDaemon(True)  # 设置为守护线程，不会因主线程结束而中断
            t.start()
            time.sleep(0.1)
        for t in thread_list:
            t.join()  # 子线程全部加入，主线程等所有子线程运行完毕
        time.sleep(1)
    except:
        print "Error: unable to start thread"

def downloadAndUpdateDailyData(business_data = [{'ts_code':'002752.SZ'}]):
    thread_list = []
    stock_codes = []
    counts = 0
    aThreadCount = 200
    # except_code = ['000001.SH','000002.SH']
    for stock_dic in business_data:
        stock_code = stock_dic['ts_code']
        
        stock_codes.append(stock_code)
        counts = counts + 1
        if counts >= aThreadCount:
            t1= threading.Thread(target=downloadAndUpdateDailyDataThread,args=(stock_codes[:],))
            thread_list.append(t1)
            stock_codes = []
            counts = 0
            # aThreadCount = aThreadCount + 10
    if counts > 0:
        t1= threading.Thread(target=downloadAndUpdateDailyDataThread,args=(stock_codes[:],))
        thread_list.append(t1)

    for t in thread_list:
        # 不需要加锁
        # t.setDaemon(True)  # 设置为守护线程，不会因主线程结束而中断
        t.start()
        time.sleep(0.1)

    for t in thread_list:
        t.join()  # 子线程全部加入，主线程等所有子线程运行完毕

def downloadAndUpdateDailyDataThread(codes):
    count = 0
    head_str = u'日期,股票代码,名称,收盘价,最高价,最低价,开盘价,前收盘,涨跌额,涨跌幅,换手率,成交量,成交金额'
    head_str_e = ',stock_code,stock_name,tclose,high,low,topen,lclose,chg,pchg,turnover,voturnover,vaturnover'
    all_count = len(codes)
    for stock_code in codes:
        count = count + 1
        cur_day = (datetime.datetime.now() - datetime.timedelta(days=0)).strftime('%Y%m%d')
        # start_time = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y%m%d')
        start_time = '20180101'
        while True:
            try:
                stock_type = stock_code[7:9]
                if stock_code[7:9] == 'SZ':
                    market_type = 1
                else:
                    market_type = 0

                file_path = 'base_data/daily/' + stock_code[0:6] + '.csv'
                exist_file = False
                df_exist = None
                if os.path.exists(file_path):#change start_time
                    # break
                    exist_file = True
                    try:
                        df_exist = pd.read_csv('base_data/daily/' + stock_code[0:6] + '.csv', parse_dates=True, index_col=0)
                        # print(df_exist.head(1))
                        # print(df_exist.head(1).index)
                        # print(df_exist.head(1).index[0])
                        # print(df_exist.head(1).index.max())
                        first_date = df_exist.head(1).index.max()
                        first_time = datetime.date(first_date.year,first_date.month,first_date.day)
                        start_time = (first_time + datetime.timedelta(days = 1)).strftime('%Y%m%d')
                    except Exception as e:
                        os.remove('base_data/daily/' + stock_code[0:6] + '.csv')
                        exist_file = False
                        # print(e)

                url_format = 'http://quotes.money.163.com/service/chddata.html?code=%d%s&start=%s&end=%s&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER'
                url = url_format % (market_type, stock_code[0:6], start_time, cur_day)
                content = web.urlopen(url,timeout=5).read()
                a_utf_8 = content.decode('gbk').encode('utf-8')
                a_utf_8 = a_utf_8.replace(head_str,head_str_e,1)
                a_utf_8 = a_utf_8.replace('\'','')

                with open('base_data/daily/' + stock_code[0:6] + '_temp.csv','wb') as f:
                    f.write(a_utf_8)
                    f.close()
                df_cur = pd.read_csv('base_data/daily/' + stock_code[0:6] + '_temp.csv', parse_dates=True, index_col=0)
                df_cur.drop(['stock_code','stock_name'],axis = 1,inplace=True)
                if exist_file:
                    df_cur = df_cur.append(df_exist) 
                    # os.rename('name1','name2')
                df_cur.to_csv('base_data/daily/' + stock_code[0:6] + '.csv')
                os.remove('base_data/daily/' + stock_code[0:6] + '_temp.csv')

                print(stock_code + ' daily ' + str(count) + '/' + str(all_count))
                time.sleep(0.5)
                break
            except Exception as e:
                if str(e) =='HTTP Error 404: Not Found':
                    print('has not ' + stock_code)
                    break
                else:
                    print(e)
                    print('wrong ' + stock_code)
                    continue
        #print(dividend_dic)
    return

def pandasTest(stock_code = '600006'):
    tsla_df_load = pd.read_csv('base_data/daily/' + stock_code + '.csv', parse_dates=True, index_col=0)
    # print('tsla_df_load.head():\n')
    print(tsla_df_load['vaturnover'].head())
    print(tsla_df_load[['stock_code','vaturnover','tclose']].head())
    # print('tsla_df_load.head():\n', tsla_df_load._stat_axis.values.tolist())
    # print(tsla_df_load.head())

def downloadFinanceThread(stock_head,talbeName):
    global os
    for count in range(g_start_stock,g_end_stock):
        stock_code = ''
        if count < 10:
            stock_code = stock_head + '00' + str(count)
        elif count < 100:
            stock_code = stock_head + '0' + str(count)
        else:
            stock_code  = stock_head + str(count)
        
        if not g_stock_codes.has_key(stock_code):
            continue
        downloadTable(stock_code,talbeName)

def downloadTable(stock_code,table_name):
    file_path = 'base_data/' + table_name + stock_code + '.csv'
    # print(file_path)
    try:
        if os.path.exists(file_path):
            return
    except Exception as e:
        print(e)
        return
    url = 'http://quotes.money.163.com/service/' + table_name + '_' + stock_code +'.html'
    while True:
        try:
            content = web.urlopen(url,timeout=2).read()
            #print(content)
            a_utf_8 = content.decode('gb2312').encode('utf-8')
            with open('base_data/' + table_name + stock_code + '.csv','wb') as f:
                f.write(a_utf_8)
                f.close()
            print(table_name + stock_code)
            time.sleep(0.5)
            break
        except Exception as e:
            if str(e) =='HTTP Error 404: Not Found':
                print('has not ' + table_name + stock_code)
                break
            else:
                print(e)
                continue

def loadData(stock_code,table_name):
    table_name = table_name or 'lrb'
    if not stock_code:
        print('stock_code is null')
        return
    try:
        csvfile = open('base_data/' + table_name + stock_code + '.csv', 'r')
    except Exception as e:
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
    # fw = open('xjllb600500.json', 'w')
    # fw.write(json_str)
    # fw.close()
    return dictionary
    # for key in xjllb_name_dict:
    #     print(key)
    #     print(abc[xjllb_name_dict[key]])

def zhJust(string,length=28):
    difference = length -  len(string) # 计算限定长度为20时需要补齐多少个空格
    if difference == 0:  # 若差值为0则不需要补
        return string
    elif difference < 0:
        print('错误：限定的对齐长度小于字符串长度!')
        return None
    # chinese_pattern = u'[?([\u4E00-\u9FA5]'
    # if re.search(chinese_pattern,string) != None:  # 如果字符串中含有中文
    #     space = '　'  # 则对齐空格使用占用2个字符位的全角空格
    # else:
    #     space = ' '  # 否则使用占用1个字符位的半角空格
    return string + '  '*(difference) # 返回补齐空格后的字符串

def getCurYear():
    cur_year = int(time.strftime("%Y", time.localtime()))
    return cur_year

def showYear(cur_year,year_count = 5):
    if not cur_year:
        cur_year = getCurYear()
    cur_year = int(cur_year)
    # print('|' + 'hej'.ljust(20) + '|' + 'hej'.rjust(20) + '|' + 'hej'.center(20) + '|')
    # print('hej'.center(20, '+')) #一共有20个字符, 中间使用hej, 其他用+填充
    str_year = ''
    for index in range(year_count,0,-1):
        str_year = str_year + str(cur_year - index).ljust(15)
    return str_year
    #print(str_year)

g_font_color = 31
def getFontColor():
    global g_font_color
    if g_font_color == 36:
        g_font_color = 31
    else:
        g_font_color = g_font_color + 1
    return g_font_color

def analyseData(stock_code,is_show = True):
    lrb_data = loadData(stock_code,'lrb')
    zcfzb_data = loadData(stock_code,'zcfzb')
    xjllb_data = loadData(stock_code,'xjllb')
    dividend_data = []
    if g_dividend_data.has_key(stock_code):
        dividend_data = g_dividend_data[stock_code]

    if not lrb_data or not xjllb_data or not zcfzb_data:
        print('loss ' + stock_code + ', unlisted')
        return
    
    cur_year = getCurYear()
    is_get_update_year = False
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 

    report_mon = 12
    report_day = 31

    max_count = 10
    indexes_for_cal_lrb = []
    for index in range(len(lrb_data['report_date'])):
        yyyymmdd = lrb_data['report_date'][index].split('-')
        if len(yyyymmdd) < 3:
            continue
        single_year = int(yyyymmdd[0])
        single_month = int(yyyymmdd[1]) 
        single_day = int(yyyymmdd[2])

        if single_year < cur_year and single_month == report_mon and single_day == report_day and len(indexes_for_cal_lrb) < max_count:
            indexes_for_cal_lrb.append(index)
            if not is_get_update_year:
                cur_year = single_year + 1
                is_get_update_year = True

    indexes_for_cal_zcfzb = []
    for index in range(len(zcfzb_data['report_date'])):
        yyyymmdd = zcfzb_data['report_date'][index].split('-')
        if len(yyyymmdd) < 3:
            continue
        single_year = int(yyyymmdd[0])
        single_month = int(yyyymmdd[1]) 
        single_day = int(yyyymmdd[2])

        if single_year < cur_year and single_month == report_mon and single_day == report_day and len(indexes_for_cal_zcfzb) < max_count:
            indexes_for_cal_zcfzb.append(index)

    indexes_for_cal_xjllb = []
    for index in range(len(xjllb_data['report_date'])):
        yyyymmdd = xjllb_data['report_date'][index].split('-')
        if len(yyyymmdd) < 3:
            continue
        single_year = int(yyyymmdd[0])
        single_month = int(yyyymmdd[1]) 
        single_day = int(yyyymmdd[2])

        if single_year < cur_year and single_month == report_mon and single_day == report_day and len(indexes_for_cal_xjllb) < max_count:
            indexes_for_cal_xjllb.append(index)


    len_of_year = min(len(indexes_for_cal_lrb),len(indexes_for_cal_xjllb),len(indexes_for_cal_zcfzb))

    while True:
        if len(indexes_for_cal_lrb) > len_of_year:
            indexes_for_cal_lrb.pop()
            continue
        if len(indexes_for_cal_xjllb) > len_of_year:
            indexes_for_cal_xjllb.pop()
            continue
        if len(indexes_for_cal_zcfzb) > len_of_year:
            indexes_for_cal_zcfzb.pop()
            continue
        break


    value_table = {'last_year':(cur_year - 1)}
    #print(indexes_for_cal_lrb)
    str_result = zhJust(u'资产负债比率（占总资产%：）    ') + showYear(cur_year,len_of_year)
    if is_show:
        print("\033[0;37;42m{0}\033[0m".format(str_result))
    
    assetsAndLiabilities = {}
    value_table['assetsAndLiabilities'] = assetsAndLiabilities
    str_result = zhJust(u'     现金与约当现金')
    cash_rate = []
    assetsAndLiabilities['cash_rate'] = cash_rate
    indexOfSingle = 0
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        money_funds = zcfzb_data['money_funds'][index]
        settlement_provision = zcfzb_data['settlement_provision'][index]
        disburse_funds = zcfzb_data['disburse_funds'][index]
        transactional_finacial_asset = zcfzb_data['transactional_finacial_asset'][index]
        derivative_finacial_asset = zcfzb_data['derivative_finacial_asset'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        cash_rate.append(utils.cal_cash_rate(money_funds,settlement_provision,disburse_funds,transactional_finacial_asset,derivative_finacial_asset,tatol_assets))
        str_result = str_result + str(cash_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     应收账款')
    accounts_receivable_rate = []
    assetsAndLiabilities['accounts_receivable_rate'] = accounts_receivable_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        accounts_receivable = zcfzb_data['accounts_receivable'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        accounts_receivable_rate.append(utils.cal_accounts_receivable_rate(accounts_receivable,tatol_assets))
        str_result = str_result + str(accounts_receivable_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     存货')
    stock_rate = []
    assetsAndLiabilities['stock_rate'] = stock_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        stock = zcfzb_data['stock'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        stock_rate.append(utils.cal_stock_rate(stock,tatol_assets))
        str_result = str_result + str(stock_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))
    
    str_result = zhJust(u'     流动资产')
    total_current_assets_rate = []
    assetsAndLiabilities['total_current_assets_rate'] = total_current_assets_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        total_current_assets = zcfzb_data['total_current_assets'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_current_assets_rate.append(utils.cal_total_current_assets_rate(total_current_assets,tatol_assets))
        str_result = str_result + str(total_current_assets_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))
    
    str_result = zhJust(u'     总资产')
    total_assets = []
    assetsAndLiabilities['total_assets'] = total_assets
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        total_assets.append(100)
        str_result = str_result + '100'.ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     应付账款')
    accounts_payable_rate = []
    assetsAndLiabilities['accounts_payable_rate'] = accounts_payable_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        accounts_payable = zcfzb_data['accounts_payable'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        accounts_payable_rate.append(utils.cal_accounts_payable_rate(accounts_payable,tatol_assets))
        str_result = str_result + str(accounts_payable_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     流动负债')
    total_current_liability_rate = []
    assetsAndLiabilities['total_current_liability_rate'] = total_current_liability_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_current_liability_rate.append(utils.cal_total_current_liability_rate(total_current_liability,tatol_assets))
        str_result = str_result + str(total_current_liability_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     长期负债')
    total_noncurrent_liability_rate = []
    assetsAndLiabilities['total_noncurrent_liability_rate'] = total_noncurrent_liability_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        total_noncurrent_liability = zcfzb_data['total_noncurrent_liability'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_noncurrent_liability_rate.append(utils.cal_total_noncurrent_liability_rate(total_noncurrent_liability,tatol_assets))
        str_result = str_result + str(total_noncurrent_liability_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     股东权益')
    total_owners_equity_rate = []
    assetsAndLiabilities['total_owners_equity_rate'] = total_owners_equity_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        total_owners_equity = zcfzb_data['total_owners_equity'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_owners_equity_rate.append(utils.cal_total_owners_equity_rate(total_owners_equity,tatol_assets))
        str_result = str_result + str(total_owners_equity_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     总负债加股东权益')
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        str_result = str_result + '100'.ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'类别      财务比例    ') + showYear(cur_year,len_of_year)
    if is_show:
        print('\n')
        print("\033[0;37;42m{0}\033[0m".format(str_result))
        print(zhJust(u'财务结构'))
    
    financial_ratio = {}
    value_table['financial_ratio'] = financial_ratio
    str_result = zhJust(u'          负债占资产比率')
    total_liability_rate = []
    financial_ratio['total_liability_rate'] = total_liability_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        total_liability = zcfzb_data['total_liability'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_liability_rate.append(utils.cal_total_liability_rate(total_liability,tatol_assets))
        str_result = str_result + str(total_liability_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          长期资金占不动产/厂房及设备比率')
    longterm_funds_rate = []
    financial_ratio['longterm_funds_rate'] = longterm_funds_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        total_owners_equity = zcfzb_data['total_owners_equity'][index]
        total_noncurrent_liability = zcfzb_data['total_noncurrent_liability'][index]
        fixed = zcfzb_data['fixed'][index]
        construction_in_progress = zcfzb_data['construction_in_progress'][index]
        engineer_material = zcfzb_data['engineer_material'][index]
        longterm_funds_rate.append(utils.cal_longterm_funds_rate(total_owners_equity,total_noncurrent_liability,fixed,construction_in_progress,engineer_material))
        str_result = str_result + str(longterm_funds_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    if is_show:
        print(zhJust(u'偿债能力'))
    solvency = {}
    value_table['solvency'] = solvency
    str_result = zhJust(u'          流动比率')
    current_rate = []
    solvency['current_rate'] = current_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        total_current_assets = zcfzb_data['total_current_assets'][index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        current_rate.append(utils.cal_current_rate(total_current_assets,total_current_liability))
        str_result = str_result + str(current_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          速动比率')
    quick_rate = []
    solvency['quick_rate'] = quick_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        total_current_assets = zcfzb_data['total_current_assets'][index]
        stock = zcfzb_data['stock'][index]
        prepayments = zcfzb_data['prepayments'][index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        quick_rate.append(utils.cal_quick_rate(total_current_assets,stock,prepayments,total_current_liability))
        str_result = str_result + str(quick_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    if is_show:
        print(zhJust(u'经营能力'))
    management_capacity = {}
    value_table['management_capacity'] = management_capacity
    receivable_turnover_rate = []
    management_capacity['receivable_turnover_rate'] = receivable_turnover_rate
    str_result = zhJust(u'          应收账款周转率（次）')
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[indexOfSingle]
        total_op_in = lrb_data['total_op_in'][index]
        index = indexes_for_cal_zcfzb[indexOfSingle]
        accounts_receivable = zcfzb_data['accounts_receivable'][index]
        receivable_turnover_rate.append(utils.cal_receivable_turnover_rate(total_op_in,accounts_receivable))
        str_result = str_result + str(receivable_turnover_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          平均收现日数')
    average_cash_days = []
    management_capacity['average_cash_days'] = average_cash_days
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[indexOfSingle]
        total_op_in = lrb_data['total_op_in'][index]
        index = indexes_for_cal_zcfzb[indexOfSingle]
        accounts_receivable = zcfzb_data['accounts_receivable'][index]
        average_cash_days.append(utils.cal_average_cash_days(total_op_in,accounts_receivable))
        str_result = str_result + str(average_cash_days[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          存货周转率（次）')
    inventory_turnover = []
    management_capacity['inventory_turnover'] = inventory_turnover
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[indexOfSingle]
        op_costs = lrb_data['op_costs'][index]
        index = indexes_for_cal_zcfzb[indexOfSingle]
        stock = zcfzb_data['stock'][index]
        inventory_turnover.append(utils.cal_inventory_turnover(op_costs,stock))
        str_result = str_result + str(inventory_turnover[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          平均销货日数（平均在库天数）')
    average_sale_days = []
    management_capacity['average_sale_days'] = average_sale_days
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[indexOfSingle]
        op_costs = lrb_data['op_costs'][index]
        index = indexes_for_cal_zcfzb[indexOfSingle]
        stock = zcfzb_data['stock'][index]
        average_sale_days.append(utils.cal_average_sale_days(op_costs,stock))
        str_result = str_result + str(average_sale_days[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          不动产及厂房及设备周转率（次）')
    equipment_turnover = []
    management_capacity['equipment_turnover'] = equipment_turnover
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[indexOfSingle]
        total_op_in = lrb_data['total_op_in'][index]
        index = indexes_for_cal_zcfzb[indexOfSingle]
        fixed = zcfzb_data['net_value_of_fixed'][index]
        construction_in_progress = zcfzb_data['construction_in_progress'][index]
        engineer_material = zcfzb_data['engineer_material'][index]
        equipment_turnover.append(utils.cal_equipment_turnover(total_op_in,fixed,construction_in_progress,engineer_material))
        str_result = str_result + str(equipment_turnover[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          总资产周转率（次）')
    total_assets_turnover = []
    management_capacity['total_assets_turnover'] = total_assets_turnover
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[indexOfSingle]
        total_op_in = lrb_data['total_op_in'][index]
        index = indexes_for_cal_zcfzb[indexOfSingle]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_assets_turnover.append(utils.cal_total_assets_turnover(total_op_in,tatol_assets))
        str_result = str_result + str(total_assets_turnover[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    if is_show:
        print(zhJust(u'获利能力'))
    profitability = {}
    value_table['profitability'] = profitability
    str_result = zhJust(u'          股东权益报酬率RoE ',length = 30)
    return_on_equity = []
    profitability['return_on_equity'] = return_on_equity
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[indexOfSingle]
        net_profit_company = lrb_data['net_profit_company'][index]
        index = indexes_for_cal_zcfzb[indexOfSingle]
        total_owners_equity = zcfzb_data['total_shareholder_parent'][index]
        return_on_equity.append(utils.cal_return_on_equity(net_profit_company,total_owners_equity))
        str_result = str_result + str(return_on_equity[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          总资产报酬率RoA ',length = 30)
    return_on_total_assets = []
    profitability['return_on_total_assets'] = return_on_total_assets
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[indexOfSingle]
        net_profit_company = lrb_data['net_profit_company'][index]
        index = indexes_for_cal_zcfzb[indexOfSingle]
        total_liability_and_equity = zcfzb_data['total_liability_and_equity'][index]
        return_on_total_assets.append(utils.cal_return_on_total_assets(net_profit_company,total_liability_and_equity))
        str_result = str_result + str(return_on_total_assets[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          营业毛利率1 ',length = 29)
    gross_profit_margin = []
    profitability['gross_profit_margin'] = gross_profit_margin
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[index]
        op_in = lrb_data['op_in'][index]
        interest_in = lrb_data['interest_in'][index]
        eared_premiun = lrb_data['eared_premiun'][index]
        fee_and_commission_in = lrb_data['fee_and_commission_in'][index]
        estale_sales_in = lrb_data['estale_sales_in'][index]
        other_op_in = lrb_data['other_op_in'][index]

        all_op_in = op_in + interest_in + eared_premiun + fee_and_commission_in + estale_sales_in + other_op_in

        op_costs = lrb_data['op_costs'][index]
        interest_exp = lrb_data['interest_exp'][index]
        fee_and_comission_exp = lrb_data['fee_and_comission_exp'][index]
        cost_of_estate_sales = lrb_data['cost_of_estate_sales'][index]
        R_and_D_exp = lrb_data['R_and_D_exp'][index]
        surrender = lrb_data['surrender'][index]
        net_payouts = lrb_data['net_payouts'][index]
        net_tqbx = lrb_data['net_tqbx'][index]
        bond_insurance_exp = lrb_data['bond_insurance_exp'][index]
        ARE = lrb_data['ARE'][index]
        other_op_cost = lrb_data['other_op_cost'][index]
        business_tariff_and_annex = lrb_data['business_tariff_and_annex'][index]

        all_cost = op_costs + interest_exp + fee_and_comission_exp + cost_of_estate_sales + R_and_D_exp + surrender + net_payouts + \
            net_tqbx + bond_insurance_exp + ARE + other_op_cost + business_tariff_and_annex
        gross_profit_margin.append(utils.cal_gross_profit_margin(all_op_in,all_cost))
        str_result = str_result + str(gross_profit_margin[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          营业利益率2 ',length = 29)
    operating_margin = []
    profitability['operating_margin'] = operating_margin
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[index]
        op_profit = lrb_data['op_profit'][index]
        total_op_in = lrb_data['total_op_in'][index]
        operating_margin.append(utils.cal_operating_margin(op_profit,total_op_in))
        str_result = str_result + str(operating_margin[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          经营安全边际率2/1 ',length = 30)
    operating_margin_of_safety = []
    profitability['operating_margin_of_safety'] = operating_margin_of_safety
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[index]
        op_profit = lrb_data['op_profit'][index]
        total_op_in = lrb_data['total_op_in'][index]
        op_costs = lrb_data['op_costs'][index]
        R_and_D_exp = lrb_data['R_and_D_exp'][index]
        business_tariff_and_annex = lrb_data['business_tariff_and_annex'][index]


        op_in = lrb_data['op_in'][index]
        interest_in = lrb_data['interest_in'][index]
        eared_premiun = lrb_data['eared_premiun'][index]
        fee_and_commission_in = lrb_data['fee_and_commission_in'][index]
        estale_sales_in = lrb_data['estale_sales_in'][index]
        other_op_in = lrb_data['other_op_in'][index]

        all_op_in = op_in + interest_in + eared_premiun + fee_and_commission_in + estale_sales_in + other_op_in

        interest_exp = lrb_data['interest_exp'][index]
        fee_and_comission_exp = lrb_data['fee_and_comission_exp'][index]
        cost_of_estate_sales = lrb_data['cost_of_estate_sales'][index]
        surrender = lrb_data['surrender'][index]
        net_payouts = lrb_data['net_payouts'][index]
        net_tqbx = lrb_data['net_tqbx'][index]
        bond_insurance_exp = lrb_data['bond_insurance_exp'][index]
        ARE = lrb_data['ARE'][index]
        other_op_cost = lrb_data['other_op_cost'][index]
        business_tariff_and_annex = lrb_data['business_tariff_and_annex'][index]

        all_cost = op_costs + interest_exp + fee_and_comission_exp + cost_of_estate_sales + R_and_D_exp + surrender + net_payouts + \
            net_tqbx + bond_insurance_exp + ARE + other_op_cost + business_tariff_and_annex

        operating_margin_of_safety.append(utils.cal_operating_margin_of_safety(all_op_in,all_cost,op_profit,total_op_in))
        str_result = str_result + str(operating_margin_of_safety[len_of_year - indexOfSingle - 1]).ljust(15)  
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          净利率 = 纯益率 ',length = 30)
    net_interest_rate = []
    profitability['net_interest_rate'] = net_interest_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[index]
        net_profit = lrb_data['net_profit'][index]
        total_op_in = lrb_data['total_op_in'][index]
        net_interest_rate.append(utils.cal_net_interest_rate(net_profit,total_op_in))
        str_result = str_result + str(net_interest_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          每股盈余（元）')
    basic_earning_per_shares = []
    profitability['basic_earning_per_shares'] = basic_earning_per_shares
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[index]
        basic_earning_per_share = lrb_data['basic_earning_per_share'][index]
        basic_earning_per_shares.append(basic_earning_per_share)
        str_result = str_result + str(basic_earning_per_share).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          税后净利（百万元）')
    net_profits = []
    profitability['net_profits'] = net_profits
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[index]
        net_profit = lrb_data['net_profit'][index]
        net_profit = int(round(float(net_profit) / 100,0))
        net_profits.append(net_profit)
        str_result = str_result + str(net_profit).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))


    str_result = zhJust(u'          研发费用（百万元）')
    R_and_D_exps = []
    profitability['R_and_D_exps'] = R_and_D_exps
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_lrb[index]
        R_and_D_exp = lrb_data['R_and_D_exp'][index]
        R_and_D_exp = int(round(float(R_and_D_exp) / 100,0))
        R_and_D_exps.append(R_and_D_exp)
        str_result = str_result + str(R_and_D_exp).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    if is_show:print(zhJust(u'现金流量'))

    cash_flow = {}
    value_table['cash_flow'] = cash_flow
    str_result = zhJust(u'          现金流量比率')
    cash_flow_rate = []
    cash_flow['cash_flow_rate'] = cash_flow_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_xjllb[indexOfSingle]
        net_flow_from_op = xjllb_data['net_flow_from_op'][index]
        index = indexes_for_cal_zcfzb[indexOfSingle]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        cash_flow_rate.append(utils.cal_cash_flow_rate(net_flow_from_op,total_current_liability))
        str_result = str_result + str(cash_flow_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          现金流量允当比率')
    cash_flow_allowance_rate = []
    cash_flow['cash_flow_allowance_rate'] = cash_flow_allowance_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_xjllb[indexOfSingle]

        yyyymmdd = xjllb_data['report_date'][index].split('-')
        if len(yyyymmdd) < 3:
            continue
        single_year = int(yyyymmdd[0])
        single_month = int(yyyymmdd[1]) 
        single_day = int(yyyymmdd[2])
        count_to_add = 0
        index_next = index

        net_flow_from_op_5 = 0
        paid_for_longterm_5 = 0
        net_cash_longterm_5 = 0
        stock_start = zcfzb_data['stock'][indexes_for_cal_zcfzb[indexOfSingle]]
        stock_end = 0
        paid_for_distribution_5 = 0
        while count_to_add < 5:
            net_flow_from_op_5 = net_flow_from_op_5 + xjllb_data['net_flow_from_op'][index_next]
            paid_for_longterm_5 = paid_for_longterm_5 + xjllb_data['paid_for_longterm'][index_next]
            net_cash_longterm_5 = net_cash_longterm_5 + xjllb_data['net_cash_longterm'][index_next]
            paid_for_distribution_5 = paid_for_distribution_5 + xjllb_data['paid_for_distribution'][index_next]
            date_end = xjllb_data['report_date'][index_next]
            count_to_add = count_to_add + 1

            has_done = False
            while 1:
                index_next = index_next + 1
                if not xjllb_data['report_date'][index_next]:
                    has_done = True
                    break
                yyyymmdd = xjllb_data['report_date'][index_next].split('-')
                if len(yyyymmdd) < 3:
                    has_done = True
                    break
                single_month = int(yyyymmdd[1]) 
                single_day = int(yyyymmdd[2])
                if single_month == report_mon and single_day == report_day:
                    break
            if has_done:
                break
        
        for index_end in range(len(zcfzb_data['report_date'])):
            if date_end == zcfzb_data['report_date'][index_end]:
                stock_end = zcfzb_data['stock'][index_end]
        cash_flow_allowance_rate.append(utils.cal_cash_flow_allowance_rate(net_flow_from_op_5,paid_for_longterm_5,net_cash_longterm_5,stock_start - stock_end,paid_for_distribution_5))
        str_result = str_result + str(cash_flow_allowance_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          现金再投资比率')
    cash_reinvestment_rate = []
    cash_flow['cash_reinvestment_rate'] = cash_reinvestment_rate
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_xjllb[indexOfSingle]
        net_flow_from_op = xjllb_data['net_flow_from_op'][index]
        paid_for_distribution = xjllb_data['paid_for_distribution'][index]
        index = indexes_for_cal_zcfzb[indexOfSingle]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        cash_reinvestment_rate.append(utils.cal_cash_reinvestment_rate(net_flow_from_op,paid_for_distribution,tatol_assets,total_current_liability))
        str_result = str_result + str(cash_reinvestment_rate[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))
        print('\n')
    str_result = zhJust(u'营业活动现金流量(百万元)        ')
    net_flow_from_ops = []
    value_table['net_flow_from_ops'] = net_flow_from_ops
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_xjllb[index]
        net_flow_from_op = xjllb_data['net_flow_from_op'][index]
        net_flow_from_ops.append(int(round(float(net_flow_from_op) / 100, 0)))
        str_result = str_result + str(net_flow_from_ops[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'投资活动现金流量(百万元)        ')
    net_flows_from_investments = []
    value_table['net_flows_from_investments'] = net_flows_from_investments
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_xjllb[index]
        net_flows_from_investment = xjllb_data['net_flows_from_investment'][index]
        net_flows_from_investments.append(int(round(float(net_flows_from_investment) / 100, 0)))
        str_result = str_result + str(net_flows_from_investments[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'筹资活动现金流量(百万元)        ')
    net_cash_flow_from_finaces = []
    value_table['net_cash_flow_from_finaces'] = net_cash_flow_from_finaces
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_xjllb[index]
        net_cash_flow_from_finace = xjllb_data['net_cash_flow_from_finace'][index]
        net_cash_flow_from_finaces.append(int(round(float(net_cash_flow_from_finace) / 100, 0)))
        str_result = str_result + str(net_cash_flow_from_finaces[len_of_year - indexOfSingle - 1]).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))


    #分红
    payment_days = ''
    #dividend10 = ''
    dividend_level = []
    value_table['dividend_level'] = dividend_level

    for index in range(len(dividend_data) - 1,-1,-1):
        dividend_level.append(dividend_data[index])

    indexes_of_dividend = []
    for single_dividend in dividend_level:
        for index in range(len_of_year):
            indexOfSingle = index
            index = indexes_for_cal_zcfzb[index]
            yyyymmdd = zcfzb_data['report_date'][index].split('-')
            yyyy = yyyymmdd[0]
            if single_dividend['year'] == yyyy:
                indexes_of_dividend.append(index)
        

    len_of_year = len(dividend_level)
    for single_dividend in dividend_level:
        for index in range(len_of_year):
            indexOfSingle = index
            index = indexes_for_cal_zcfzb[index]
            yyyymmdd = zcfzb_data['report_date'][index].split('-')
            yyyy = yyyymmdd[0]
            if single_dividend['year'] == yyyy:
                payment_days = payment_days + single_dividend['payment_day'].ljust(15)
    str_result = zhJust(u'类别      分红发放日    ') + payment_days

    if is_show:
        print('\n')
        print("\033[0;37;42m{0}\033[0m".format(str_result))
        print(zhJust(u'分红水平'))
    
    str_result = zhJust(u'          每10股分红（元）',29)

    for single_dividend in dividend_level:
        for index in range(len_of_year):
            indexOfSingle = index
            index = indexes_for_cal_zcfzb[index]
            yyyymmdd = zcfzb_data['report_date'][index].split('-')
            yyyy = yyyymmdd[0]
            if single_dividend['year'] == yyyy:
                str_result = str_result + str(single_dividend['dividend']).ljust(15)
                break
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          分红率')

    for single_dividend in dividend_level:
        for index in range(len_of_year):
            indexOfSingle = index
            index = indexes_for_cal_zcfzb[indexOfSingle]
            yyyymmdd = zcfzb_data['report_date'][index].split('-')
            yyyy = yyyymmdd[0]
            
            if single_dividend['year'] == yyyy:
                dividend = 0
                if single_dividend['dividend'] != '--':
                    dividend = float(single_dividend['dividend'])
                payIn_capital = zcfzb_data['payIn_capital'][index]
                index = indexes_for_cal_lrb[indexOfSingle]
                net_profit_company = lrb_data['net_profit_company'][index]
                single_dividend['dividend_rate'] = utils.cal_dividend_rate(dividend,payIn_capital,net_profit_company)
                str_result = str_result + str(single_dividend['dividend_rate']).ljust(15)
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))
    
    json_values = json.dumps(value_table)
    fw = open('base_data/value/' + stock_code + '.json', 'w')
    fw.write(json_values)
    fw.close()
    
def analyseAllData():
    global os
    for stock_head in g_stock_head_codes:
        for count in range(g_start_stock,g_end_stock):
            stock_code = ''
            if count < 10:
                stock_code = stock_head + '00' + str(count)
            elif count < 100:
                stock_code = stock_head + '0' + str(count)
            else:
                stock_code  = stock_head + str(count)
            if not g_stock_codes.has_key(stock_code):
                continue
            file_path = 'base_data/value/' + stock_code + '.json'
            #print(file_path)
            if not os.path.exists(file_path):
            # if True:
                print('analyse ' + stock_code)
                analyseData(stock_code = stock_code,is_show=False)
            else:
                print('json ' + stock_code + ' is exist')


def cal_score(stock_code,end_year = 0):
    try:
        csvfile = open('base_data/value/' + stock_code + '.json', 'r')
    except Exception as e:
        print(stock_code + ' open wrong')
        print(e)
        return 0

    value_table = json.load(csvfile)
    last_year = int(value_table['last_year'])
    if end_year == 0:
        end_year = last_year
    if end_year > last_year:
        return 0
    len_year = len(value_table['profitability']['return_on_equity'])
    if len_year < 5 + last_year - end_year:
        return 0
    
    start_index = len_year - 5 - last_year + end_year

    tatal_score = 0
    #股东权益报酬率(%) RoE
    sum_roe = 0
    is_roe_m0 = False
    min_roe = 10000
    len_add = 0
    for index,roe in enumerate(value_table['profitability']['return_on_equity']):
        if index < start_index:
            continue
        if roe < 0:
            is_roe_m0 = True
        min_roe = min(min_roe,roe)
        sum_roe = sum_roe + roe
        len_add = len_add + 1
    average_roe = sum_roe / len_add
    if not is_roe_m0:
        if min_roe / average_roe < 0.3:
            tatal_score = tatal_score + 0
        elif average_roe >= 35:
            tatal_score = tatal_score + 550
        elif average_roe >= 30:
            tatal_score = tatal_score + 500
        elif average_roe >= 25:
            tatal_score = tatal_score + 450
        elif average_roe >= 20:
            tatal_score = tatal_score + 400
        elif average_roe >= 15:
            tatal_score = tatal_score + 300
        elif average_roe >= 10:
            tatal_score = tatal_score + 250
    
    #总资产报酬率(%) RoA
    sum_roa = 0
    min_roa = 10000
    len_add = 0
    for index,roa in enumerate(value_table['profitability']['return_on_total_assets']):
        if index < start_index:
            continue
        sum_roa = sum_roa + roa
        min_roa = min(min_roa,roa)
        len_add = len_add + 1
    average_roa = sum_roa / len_add

    if sum_roa == 0 or min_roa <= 0:
        tatal_score = tatal_score + 0
    elif average_roa >= 15:
        tatal_score = tatal_score + 100
    elif average_roa >= 11:
        tatal_score = tatal_score + 80
    elif average_roa >= 7:
        tatal_score = tatal_score + 50

    #税后净利 规模(百万)
    sum_net_profit = 0
    len_add = 0
    for index,net_profit in enumerate(value_table['profitability']['net_profits']):
        if index < start_index:
            continue
        sum_net_profit = sum_net_profit + net_profit
        len_add = len_add + 1
    average_net_profit = sum_net_profit / len_add

    if sum_net_profit == 0:
        tatal_score = tatal_score + 0
    elif average_net_profit >= 10000:
        tatal_score = tatal_score + 150
    elif average_net_profit >= 1000:
        tatal_score = tatal_score + 100

    #现金状况 分析
    #总资产周转率（次）
    sum_total_assets_turnover = 0
    len_add = 0
    for index,total_assets_turnover in enumerate(value_table['management_capacity']['total_assets_turnover']):
        if index < start_index:
            continue
        sum_total_assets_turnover = sum_total_assets_turnover + total_assets_turnover
        len_add = len_add + 1
    average_total_assets_turnover = sum_total_assets_turnover / len_add


    #现金与约当现金
    sum_cash_rate = 0
    len_add = 0
    for index,cash_rate in enumerate(value_table['assetsAndLiabilities']['cash_rate']):
        if index < start_index:
            continue
        sum_cash_rate = sum_cash_rate + cash_rate
        len_add = len_add + 1
    average_cash_rate = sum_cash_rate / len_add

    if average_total_assets_turnover == 0 or average_cash_rate == 0:
        tatal_score = tatal_score + 0
    elif average_total_assets_turnover >= 0.8:
        if average_cash_rate > 10:
            tatal_score = tatal_score + 50
    else:
        if average_cash_rate >= 20:
            tatal_score = tatal_score + 50

    #收现日数(日)
    #平均收现日数
    sum_average_cash_days = 0
    len_add = 0
    for index,average_cash_days in enumerate(value_table['management_capacity']['average_cash_days']):
        if index < start_index:
            continue
        sum_average_cash_days = sum_average_cash_days + average_cash_days
        len_add = len_add + 1
    average_average_cash_days = sum_average_cash_days / len_add
    
    if sum_average_cash_days == 0:
        tatal_score = tatal_score + 0
    elif average_average_cash_days <= 30:
        tatal_score = tatal_score + 20

    #销货日数(日)
    #平均销货日数（平均在库天数）
    sum_average_sale_days = 0
    len_add = 0
    for index,average_sale_days in enumerate(value_table['management_capacity']['average_sale_days']):
        if index < start_index:
            continue
        sum_average_sale_days = sum_average_sale_days + average_sale_days
        len_add = len_add + 1
    average_average_sale_days = sum_average_sale_days / len_add

    if sum_average_sale_days == 0:
        tatal_score = tatal_score + 0
    elif average_average_sale_days <= 30:
        tatal_score = tatal_score + 20

    #收现日数+销货日数(日)
    if sum_average_sale_days == 0 or sum_average_cash_days == 0:
        tatal_score = tatal_score + 0
    elif average_average_cash_days + average_average_sale_days <= 40:
        tatal_score = tatal_score + 20
    elif average_average_cash_days + average_average_sale_days <= 60:
        tatal_score = tatal_score + 10

    #毛利率(%)
    #营业毛利率'
    sum_gross_profit_margin = 0
    min_gross_profit_margin = 100
    max_gross_profit_margin = 0
    len_add = 0
    for index,gross_profit_margin in enumerate(value_table['profitability']['gross_profit_margin']):
        if index < start_index:
            continue
        sum_gross_profit_margin = sum_gross_profit_margin + gross_profit_margin
        min_gross_profit_margin = min(min_gross_profit_margin,gross_profit_margin)
        max_gross_profit_margin = max(max_gross_profit_margin,gross_profit_margin)
        len_add = len_add + 1
    average_gross_profit_margin = sum_gross_profit_margin / len_add
    
    if sum_gross_profit_margin == 0 or min_gross_profit_margin <= 5:
        tatal_score
    elif min_gross_profit_margin / average_gross_profit_margin >= 0.7 and max_gross_profit_margin / average_gross_profit_margin <= 1.3:
        tatal_score = tatal_score + 50
    
    #经营安全边际率(%)
    sum_operating_margin_of_safety = 0
    min_operating_margin_of_safety = 100
    len_add = 0
    for index,operating_margin_of_safety in enumerate(value_table['profitability']['operating_margin_of_safety']):
        if index < start_index:
            continue
        sum_operating_margin_of_safety = sum_operating_margin_of_safety + operating_margin_of_safety
        min_operating_margin_of_safety = min(min_operating_margin_of_safety,operating_margin_of_safety)
        len_add = len_add + 1
    average_operating_margin_of_safety = sum_operating_margin_of_safety / len_add

    if sum_operating_margin_of_safety == 0 or min_operating_margin_of_safety <= 5:
        tatal_score
    elif average_operating_margin_of_safety >= 70:
        tatal_score = tatal_score + 50
    elif average_operating_margin_of_safety >= 50:
        tatal_score = tatal_score + 30
    elif average_operating_margin_of_safety >= 30:
        tatal_score = tatal_score + 10

    # 税后净利 积分算法(当年的净利比去年是增加还是减少，增加则加分，减少则减分)
    net_profits = value_table['profitability']['net_profits']

    #len_net_profits = len(net_profits)
    if sum_net_profit != 0:
        if net_profits[start_index + 4] > net_profits[start_index + 3]:
            tatal_score = tatal_score + 30
        else:
            tatal_score = tatal_score - 30

        if net_profits[start_index + 3] > net_profits[start_index + 2]:
            tatal_score = tatal_score + 25
        else:
            tatal_score = tatal_score - 25

        if net_profits[start_index + 2] > net_profits[start_index + 1]:
            tatal_score = tatal_score + 20
        else:
            tatal_score = tatal_score - 20

        if net_profits[start_index + 1] > net_profits[start_index]:
            tatal_score = tatal_score + 15
        else:
            tatal_score = tatal_score - 15

    #营业活动现金流量

    sum_net_flow_from_op = 0
    sum_net_flow_from_ops = value_table['net_flow_from_ops']
    for index,net_flow_from_op in enumerate(sum_net_flow_from_ops):
        if index < start_index:
            continue
        sum_net_flow_from_op = sum_net_flow_from_op + net_flow_from_op  
    
    if sum_net_flow_from_op != 0:
        if sum_net_flow_from_ops[start_index + 4] > sum_net_flow_from_ops[start_index + 3]:
            tatal_score = tatal_score + 30
        else:
            tatal_score = tatal_score - 30

        if sum_net_flow_from_ops[start_index + 3] > sum_net_flow_from_ops[start_index + 2]:
            tatal_score = tatal_score + 25
        else:
            tatal_score = tatal_score - 25

        if sum_net_flow_from_ops[start_index + 2] > sum_net_flow_from_ops[start_index + 1]:
            tatal_score = tatal_score + 20
        else:
            tatal_score = tatal_score - 20

        if sum_net_flow_from_ops[start_index + 1] > sum_net_flow_from_ops[start_index + 0]:
            tatal_score = tatal_score + 15
        else:
            tatal_score = tatal_score - 15

    sum_dividend = 0

    dividend_count = 0
    for index in range(len(value_table['dividend_level']) - 1,-1,-1):
        dividend_level = value_table['dividend_level'][index]
        if int(dividend_level['year']) > end_year:
            continue
        dividend = 0
        if dividend_level.has_key('dividend_rate'):
            dividend = float(dividend_level['dividend_rate'])
        sum_dividend = sum_dividend + dividend
        dividend_count = dividend_count + 1
        if dividend_count >= 5:
            break
    if len(value_table['dividend_level']) == 0:
        average_dividend = 0
    else:
        if dividend_count == 0:
            dividend_count = 1
        average_dividend = sum_dividend / dividend_count
    
    if average_dividend == 0:
        tatal_score = tatal_score + 0
    elif average_dividend >= 30:
        tatal_score = tatal_score + 50
    elif average_dividend >= 20:
        tatal_score = tatal_score + 20

    #print(stock_code + ' score ' + str(tatal_score))
    return tatal_score
    
def gethtml():
    content = web.urlopen('http://quotes.money.163.com/f10/gszl_600500.html#11a01').read()
    soup = bs4.BeautifulSoup(content,features="lxml")
    #输出第一个 title 标签
    # print(soup.head.contents[1])
    # print soup.head.meta.attrs
    #print (soup.head.meta['content'].decode('utf-8'))
    #print soup.head.contents[0]
    
    # #输出第一个 title 标签的标签名称
    # print soup.title.name
    
    # #输出第一个 title 标签的包含内容
    #print soup.head.meta.strings
    
    # #输出第一个 title 标签的父标签的标签名称
    # print soup.title.parent.name
    
    # #输出第一个  p 标签
    # print soup.p

    # #输出第一个  p 标签的 class 属性内容
    # print soup.body['class']
    
    # #输出第一个  a 标签的  href 属性内容
    # print soup.a['href']
    # '''
    # soup的属性可以被添加,删除或修改. 再说一次, soup的属性操作方法与字典一样
    # '''
    # #修改第一个 a 标签的href属性为 http://www.baidu.com/
    # soup.a['href'] = 'http://www.baidu.com/'
    
    # #给第一个 a 标签添加 name 属性
    # soup.a['name'] = u'百度'
    
    # #删除第一个 a 标签的 class 属性为
    # del soup.a['class']
    
    # ##输出第一个  p 标签的所有子节点
    # print soup.body.contents
    
    # #输出第一个  a 标签
    # print soup.a
    
    # #输出所有的  a 标签，以列表形式显示
    # print soup.find_all('a')
    
    # #输出第一个 id 属性等于  link3 的  a 标签
    # print soup.find(id="link3")
    
    # #获取所有文字内容
    # print(soup.get_text())
    
    # #输出第一个  a 标签的所有属性信息
    # print soup.a.attrs
    
    # for link in soup.find_all('a'):
    #     #获取 link 的  href 属性内容
    #     print(link.get('href'))
    
    # #对soup.p的子节点进行循环输出    
    # for child in soup.body.children:
    #     print(child)
    
    # #正则匹配，名字中带有b的标签
    # for tag in soup.find_all(re.compile("b")):
    #     print(tag.name)

def crawlDividendFrom163Thread(dividend_dic,codes = []):
    count = 0
    for stock_code in codes:
        stock_code = stock_code
        count = count + 1
        if dividend_dic.has_key(stock_code):
            print(stock_code + ' has got')
            continue
        while True:
            try:
                url = 'http://quotes.money.163.com/f10/fhpg_' + stock_code + '.html'
                content = web.urlopen(url,timeout=5).read()
                soup = bs4.BeautifulSoup(content,features="lxml")
                inner_box = soup.body.contents[7].contents[9]
                tbody = inner_box.contents[3]
                dividend_dic[stock_code] = []
                for index in range(len(tbody.contents)):
                    if index < 3:
                        continue
                    if index > 12:
                        break
                    tr = tbody.contents[index]
                    if type(tr) == bs4.element.Tag:
                        if str(tr.contents[0].contents[0]) == u'暂无数据':
                            break
                        year = str(tr.contents[1].string)
                        dividend = str(tr.contents[4].string)
                        payment_day = str(tr.contents[6].string)
                        #print('分红年度：' + tr.contents[1].string + ' 派息：' + tr.contents[4].string + ' 发放日：' + tr.contents[6].string)
                        dividend_dic[stock_code].append({'year':year,'dividend':dividend,'payment_day':payment_day})
                time.sleep(0.1)
                print(stock_code + ' dividend has download ! ' + str(count))
                break
            except Exception as e:
                if str(e) =='HTTP Error 404: Not Found':
                    print('has not ' + stock_code)
                    break
                if str(e) == 'HTTP Error 500: Internal Server Error':
                    print('server error form 163. Code:' + stock_code)
                    break
                else:
                    print(e)
                    continue
        #print(dividend_dic)
    return

def crawlDividendFromSinaThread(dividend_dic,codes = []):
    #存在封ip的风险，暂时只下载高分的股票
    count = 0
    for stock_code in codes:
        stock_code = stock_code
        count = count + 1
        if dividend_dic.has_key(stock_code):
            print(stock_code + ' has got')
            continue
        while True:
            try:
                url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/' + stock_code + '.phtml'
                content = web.urlopen(url,timeout=5).read()
                soup = bs4.BeautifulSoup(content,features="lxml")
                # inner_box = soup.body.contents[7].contents[9]
                # tbody = inner_box.contents[3]
                # dividend_dic[stock_code] = []
                # for index in range(len(tbody.contents)):
                #     if index < 3:
                #         continue
                #     if index > 12:
                #         break
                #     tr = tbody.contents[index]
                #     if type(tr) == bs4.element.Tag:
                #         if str(tr.contents[0].contents[0]) == u'暂无数据':
                #             break
                #         year = str(tr.contents[1].string)
                #         dividend = str(tr.contents[4].string)
                #         payment_day = str(tr.contents[6].string)
                #         #print('分红年度：' + tr.contents[1].string + ' 派息：' + tr.contents[4].string + ' 发放日：' + tr.contents[6].string)
                #         dividend_dic[stock_code].append({'year':year,'dividend':dividend,'payment_day':payment_day})
                time.sleep(random.randint(0,5)) 
                print(stock_code + ' dividend has download ! ' + str(count))
                break
            except Exception as e:
                if str(e) =='HTTP Error 404: Not Found':
                    print('has not ' + stock_code)
                    break
                if str(e) == 'HTTP Error 500: Internal Server Error':
                    print('server error form 163. Code:' + stock_code)
                    break
                else:
                    print(e)
                    continue
        #print(dividend_dic)
    return

def getDividendData(pro,business_data = []):
    # business_data = [{'ts_code':'600117.SH'}]
    #tushare is bad.
    # It's better that go to 163 to grap some data. At less do not waiting.

    dividend_dic = {}
    if os.path.exists("base_data/dividend/dividend.json"):
        fo = open("base_data/dividend/dividend.json", "r")
        dividend_dic = json.load(fo)
        fo.close()

    thread_list = []
    stock_codes = []
    counts = 0
    aThreadCount = 300
    for stock_dic in business_data:
        stock_code = stock_dic['ts_code'][0:6]
        stock_codes.append(stock_code)
        counts = counts + 1
        if counts >= aThreadCount:
            t1= threading.Thread(target=crawlDividendFrom163Thread,args=(dividend_dic,stock_codes[:],))
            thread_list.append(t1)
            stock_codes = []
            counts = 0
    if counts > 0:
        t1= threading.Thread(target=crawlDividendFrom163Thread,args=(dividend_dic,stock_codes[:],))
        thread_list.append(t1)

    for t in thread_list:
        # 不需要加锁
        # t.setDaemon(True)  # 设置为守护线程，不会因主线程结束而中断
        t.start()
        time.sleep(0.1)

    for t in thread_list:
        t.join()  # 子线程全部加入，主线程等所有子线程运行完毕

    dividend_dic_json = json.dumps(dividend_dic)
    fo = open("base_data/dividend/dividend.json", "w")
    fo.write(dividend_dic_json)
    fo.close()
    print('done!')
    return dividend_dic

def crawlStockValueFromWeb():
    #估值
    #算法，n年(一般是10)净利润增长平均值，预测未来m年(10)(1、一般公司不超过6年；2、优质公司不超过9年；)净利润，
    #净利润合计除以流通股本就是合理买入估值
    tops = getTop(is_save = False,rule_names = ['more05','less05'],number=500)
    value_dic = {}
    count = 0
    browser = webdriver.Chrome()
    url = 'https://www.touzid.com/company/dnp.html#/'
    browser.get(url)
    fo = open('product/estimate_value' + '.txt','w')
    already_got = True
    for key in tops:
        for node in tops[key]:
            count = count + 1
            stock_code = node.stock_code[7:9] + node.stock_code[0:6]
            if stock_code == 'SH603288':
                already_got = False
            if already_got:
                continue
            if value_dic.has_key(stock_code):
                print(stock_code + ' has got')
                continue
            while True:
                try:
                    url = 'https://www.touzid.com/company/dnp.html#/' + stock_code
                    browser.get(url)
                    # browser.execute_script('var box = document.getElementsByClassName("el-popup-parent--hidden");\
                    #     box[0].style.height = "100%";\
                    #     box[0].style.overflow = "scroll";')
                    
                    element = browser.find_elements_by_class_name('cell')
                    buy_price = 0
                    cur_price = 0
                    for i in range(len(element)):
                        # print(element[i].text)
                        if element[i].text == u'合理买入价格':
                            buy_price = element[i + 1].text
                        if element[i].text == u'当前价格':
                            cur_price = element[i + 1].text
                        if buy_price != 0 and cur_price != 0:
                            break
                    value_dic[stock_code] = {'buy_price':buy_price,'cur_price':cur_price}
                    time.sleep(1.0)
                    value_str = str(node) + ' 当前价格：' + cur_price + ' 估计价格：' + buy_price
                    print(value_str)
                    if buy_price == 0:
                        buy_price == 1
                    if count < 100 or cur_price / buy_price < 1.2:
                        fo.write(value_str + '\n')
                    break
                except Exception as e:
                    # print(e)
                    time.sleep(1.0)
                    break
    fo.close()

def getAllotmentData(pro,business_data = []):
    # business_data = [{'ts_code':'600117.SH'}]
    #tushare is bad.
    # It's better that go to 163 to grap some data. At less do not waiting.

    allotment_dic = {}
    if os.path.exists("base_data/dividend/allotment.json"):
        fo = open("base_data/dividend/allotment.json", "r")
        allotment_dic = json.load(fo)
        fo.close()

    thread_list = []
    stock_codes = []
    counts = 0
    aThreadCount = 300
    for stock_dic in business_data:
        stock_code = stock_dic['ts_code'][0:6]
        stock_codes.append(stock_code)
        counts = counts + 1
        # if counts >= aThreadCount:
        #     t1= threading.Thread(target=crawlDividendFromSinaThread,args=(allotment_dic,stock_codes[:],))
        #     thread_list.append(t1)
        #     stock_codes = []
        #     counts = 0
    if counts > 0:
        t1= threading.Thread(target=crawlDividendFromSinaThread,args=(allotment_dic,stock_codes[:],))
        thread_list.append(t1)

    for t in thread_list:
        # 不需要加锁
        # t.setDaemon(True)  # 设置为守护线程，不会因主线程结束而中断
        t.start()
        time.sleep(0.1)

    for t in thread_list:
        t.join()  # 子线程全部加入，主线程等所有子线程运行完毕

    allotment_dic_json = json.dumps(allotment_dic)
    fo = open("base_data/dividend/allotment.json", "w")
    fo.write(allotment_dic_json)
    fo.close()
    print('done!')
    return allotment_dic

def deleteFile():
    for stock_head in g_stock_head_codes:
        for talbeName in g_table_names:
            for count in range(g_start_stock,g_end_stock):
                stock_code = ''
                if count < 10:
                    stock_code = stock_head + '00' + str(count)
                elif count < 100:
                    stock_code = stock_head + '0' + str(count)
                else:
                    stock_code  = stock_head + str(count)
                file_path = 'base_data/' + talbeName + stock_code + '.csv'
                if os.path.exists(file_path) and not g_stock_codes.has_key(stock_code):
                    os.remove(file_path)
                    print('remove ' + talbeName + stock_code)

def initGStockCodes():
    global g_business_data,g_stock_codes
    business_file = open("base_data/business/business.json", "r")
    g_business_data = json.load(business_file)
    #g_stock_codes
    for stock_dic in g_business_data:
        if stock_dic['industry'] == 'industry':
            continue
        stock_code = stock_dic['ts_code'][0:6]
        g_stock_codes[stock_code] = stock_dic
    business_file.close()

def sortHp(node):
    return node.score

def getTop(is_save = True,rule_names = ['more05','less05','more03','less03','less01'],number = 500):
    global g_business_data

    local_time = time.localtime()
    cur_year = 2020
    score_year = 2019
    
    rule_names = ['less05']
    tops = {}

    for rule_name in rule_names:
        th = TopKHeap(number)
        #count = 1
        for stock_dic in g_business_data:
            stock_code = stock_dic['ts_code']
            if stock_code[0:3] == '688':
                continue

            # if stock_code[0] != '3':
            #     continue

            # if not (stock_dic['industry'] == u'食品'):
            #     continue
            if stock_dic['industry'] == u'银行' or stock_dic['industry'] == u'全国地产' or stock_dic['industry'] == u'房产服务' or stock_dic['industry'] == u'区域地产':
                continue
            num = 0
            if rule_name[-2] == '0':
                num = int(rule_name[-1])
            else:
                num = int(rule_name[-2:-1])
            
            list_year = int(stock_dic['list_date'][0:4])
            if num == 0:
                continue
            # if rule_name[0:4] == 'more':
            #     if cur_year - list_year < num:
            #         continue
            # elif rule_name[0:4] == 'less':
            #     if cur_year - list_year >= num:
            #         continue
            # else:
            #     continue
            if list_year >= cur_year - 1:
                continue
            
            score = cal_score(stock_code[0:6],score_year)
            node = Node(stock_code,stock_dic['name'] + ' ' + stock_dic['industry'],score,str(cur_year - list_year + 1) + 'year' )
            th.push(node)

        tops[rule_name] = th
        print(rule_name + ' has get top')
    topHps = {}
    for rule_name in rule_names:
        th = tops[rule_name]
        topHp = th.topk()
        topHp.sort(key=sortHp,reverse = True)
        topHps[rule_name] = topHp
        if is_save:
            fo = open('product/best_long_term_shares_all_' + str(score_year) + rule_name + '.txt','w')
            # fo = open('product/best_long_term_shares_sever' + rule_name + '.txt','w')
            # fo = open('product/best_long_term_shares_product' + rule_name + '.txt','w')
            # fo = open('product/best_long_term_shares_hotel' + rule_name + '.txt','w')

            for node in topHp:
                stock_code = node.stock_code
                try:
                    csvfile = open('base_data/value/' + stock_code[0:6] + '.json', 'r')
                except Exception as e:
                    print(stock_code + ' open wrong')
                    print(e)
                value_table = json.load(csvfile)
                last_year = int(value_table['last_year'])
                if score_year == 0 or score_year > last_year:
                    score_year = last_year
                len_year = len(value_table['assetsAndLiabilities']['cash_rate'])
                start_index = len_year - 5 - last_year + score_year

                cash_rate = value_table['assetsAndLiabilities']['cash_rate'][start_index + 4]
                roe = value_table['profitability']['return_on_equity'][start_index + 4]
                net_profit = value_table['profitability']['net_profits'][start_index + 4]
                R_and_D_exp = value_table['profitability']['R_and_D_exps'][start_index + 4]
                r_profit_rate = 0
                if net_profit != 0:
                    r_profit_rate = round(float(R_and_D_exp) / net_profit * 100,1)
                fo.write(str(node) + ' 现金占比' + str(cash_rate) + '%' + ' roe' + str(roe) + '% 净利' + str(net_profit) + ' 研发占比' + str(r_profit_rate) + '%\n')
            print(rule_name + ' has done')
            fo.close()
    return topHps

def getIndustryTop(is_save = True,number = 15):
    global g_business_data

    local_time = time.localtime()
    cur_year = getCurYear()
    cur_year = 2020
    score_year = 2019
    
    tops = {}

    industry_map = {}
    #count = 1
    for stock_dic in g_business_data:
        stock_code = stock_dic['ts_code']
        if stock_code[0:3] == '688':
            continue
        
        list_year = int(stock_dic['list_date'][0:4])
        if not industry_map.has_key(stock_dic['industry']):
            industry_map[stock_dic['industry']] = TopKHeap(number)
        th = industry_map[stock_dic['industry']]
        
        score = cal_score(stock_code[0:6],score_year)
        node = Node(stock_code,stock_dic['name'] + ' ' + stock_dic['industry'],score,str(cur_year - list_year + 1) + 'year' )
        th.push(node)

    if not is_save:
        return industry_map

    fo = open('product/industry_best_all.txt','w')

    for key in industry_map:
        th = industry_map[key]
        topHp = th.topk()
        topHp.sort(key=sortHp,reverse = True)
        show_number = 0
        for node in topHp:
            stock_code = node.stock_code
            try:
                csvfile = open('base_data/value/' + stock_code[0:6] + '.json', 'r')
            except Exception as e:
                print(stock_code + ' open wrong')
                print(e)
            value_table = json.load(csvfile)
            last_year = int(value_table['last_year'])
            if score_year == 0 or score_year > last_year:
                    score_year = last_year
            len_year = len(value_table['assetsAndLiabilities']['cash_rate'])
            start_index = len_year - 5 - last_year + score_year
            cash_rate = value_table['assetsAndLiabilities']['cash_rate'][start_index + 4]
            roe = value_table['profitability']['return_on_equity'][start_index + 4]
            net_profit = value_table['profitability']['net_profits'][start_index + 4]
            R_and_D_exp = value_table['profitability']['R_and_D_exps'][start_index + 4]
            r_profit_rate = 0
            if net_profit != 0:
                r_profit_rate = round(float(R_and_D_exp) / net_profit * 100,1)
            show_number = show_number + 1
            # if show_number > 2 and node.score < 500:
            #     continue
            fo.write(str(node) + ' 现金占比' + str(cash_rate) + '%' + ' roe' + str(roe) + '% 净利' + str(net_profit) + ' 研发占比' + str(r_profit_rate) + '%\n')
        fo.write('\n')
        print(key + ' has done')
    fo.close()

def getTopAllScore(is_save = True,rule_names = ['more05','less05','more03','less03','less01'],number = 300):
    global g_business_data

    local_time = time.localtime()
    cur_year = 2020
    score_year = 2019
    
    rule_names = ['less05']
    tops = {}

    for rule_name in rule_names:
        th = TopKHeap(number)
        #count = 1
        for stock_dic in g_business_data:
            stock_code = stock_dic['ts_code']
            if stock_code[0:3] == '688':
                continue

            # if stock_code[0] != '3':
            #     continue

            if stock_dic['industry'] == u'银行' or stock_dic['industry'] == u'全国地产' or stock_dic['industry'] == u'房产服务' or stock_dic['industry'] == u'区域地产':
                continue
            num = 0
            if rule_name[-2] == '0':
                num = int(rule_name[-1])
            else:
                num = int(rule_name[-2:-1])
            
            list_year = int(stock_dic['list_date'][0:4])
            if num == 0:
                continue
            # if rule_name[0:4] == 'more':
            #     if cur_year - list_year < num:
            #         continue
            # elif rule_name[0:4] == 'less':
            #     if cur_year - list_year >= num:
            #         continue
            # else:
            #     continue
            if list_year >= cur_year:
                continue
            
            scores = []
            score_of_year = ''
            score = 0
            for index in range(6):
                score0 = cal_score(stock_code[0:6],score_year - index)
                # if score0 > 0:
                scores.append(score0)
                score_of_year = score_of_year + ' ' + str(score_year - index) + ':' + str(score0)
                score = score + score0

            score_len = len(scores)
            if score_len == 0:
                score_len = 1
            score = scores[0]
            # score = score / score_len
            node = Node(stock_code,stock_dic['name'] + ' ' + stock_dic['industry'],score,str(cur_year - list_year + 1) + 'year' )
            node.add_remarks(score_of_year)
            th.push(node)

        tops[rule_name] = th
        print(rule_name + ' has get top')
    topHps = {}
    for rule_name in rule_names:
        th = tops[rule_name]
        topHp = th.topk()
        topHp.sort(key=sortHp,reverse = True)
        topHps[rule_name] = topHp
        if is_save:
            fo = open('product/best_shares_all_score' + str(score_year) + rule_name + '.txt','w')
            # fo = open('product/best_long_term_shares_sever' + rule_name + '.txt','w')
            # fo = open('product/best_long_term_shares_product' + rule_name + '.txt','w')
            # fo = open('product/best_long_term_shares_hotel' + rule_name + '.txt','w')

            for node in topHp:
                stock_code = node.stock_code
                try:
                    csvfile = open('base_data/value/' + stock_code[0:6] + '.json', 'r')
                except Exception as e:
                    print(stock_code + ' open wrong')
                    print(e)
                value_table = json.load(csvfile)
                last_year = int(value_table['last_year'])
                if score_year == 0 or score_year > last_year:
                    score_year = last_year
                len_year = len(value_table['assetsAndLiabilities']['cash_rate'])
                start_index = len_year - 5 - last_year + score_year

                cash_rate = value_table['assetsAndLiabilities']['cash_rate'][start_index + 4]
                roe = value_table['profitability']['return_on_equity'][start_index + 4]
                net_profit = value_table['profitability']['net_profits'][start_index + 4]
                R_and_D_exp = value_table['profitability']['R_and_D_exps'][start_index + 4]
                r_profit_rate = 0
                if net_profit != 0:
                    r_profit_rate = round(float(R_and_D_exp) / net_profit * 100,1)
                fo.write(str(node) + ' 现金占比' + str(cash_rate) + '%' + ' roe' + str(roe) + '% 净利' + str(net_profit) + ' 研发占比' + str(r_profit_rate) + '%\n')
            print(rule_name + ' has done')
            fo.close()
    return topHps

def getDaysBestGroup(begin = '20200110',end = '20200110'):
    global g_business_data
    days_group = []
    # g_business_data = g_business_data[0:100]
    all_count = len(g_business_data)
    days_count = 10
    for num in range(days_count):
        days_group.append({})
    count = 0
    for stock_dic in g_business_data:
        stock_code = stock_dic['ts_code'][0:6]
        count = count + 1
        if stock_code[0:3] == '688':
            continue

        file_path = 'base_data/daily/' + stock_code + '.csv'
        if not os.path.exists(file_path):
            continue
        try:
            df = pd.read_csv('base_data/daily/' + stock_code[0:6] + '.csv', parse_dates=True, index_col=0)
        except Exception as e:
            continue
        # df.shape[0] get cow length
        # df = df.head(1)
        # print(df)
        industry = stock_dic['industry']
        if(industry == 'industry'):
            continue
        for num in range(days_count):
            if df.shape[0] <= num:
                break
            timestamp = df.iloc[num].name
            dateStr = str(timestamp.year) + '-' + str(timestamp.month) + '-' + str(timestamp.day)
            chg = df.iloc[num].at['chg']
            lclose = df.iloc[num].at['lclose']

            if chg == 'None' or lclose == 'None':
                continue
            rate = round( float(chg) / float(lclose) * 10000)
            
            group_dic = days_group[num]
            if group_dic.has_key(industry):
                value = group_dic[industry]
                value['rate'] = value['rate'] + rate
                value['count'] = value['count'] + 1
            else:
                group_dic[industry] = {'rate':rate,'count':1,'date':dateStr}
        
        work_rate = round(float(count) / all_count * 1000)
        print ' ' + str(count) + ' ' + str(work_rate / 10) + '%\r',
    
    def sortGroup(elem):
        return elem['average']
    for num in range(days_count):
        group_dic = days_group[num]
        group_list = []
        for key in group_dic:
            group_dic[key]['average'] = round(group_dic[key]['rate'] / group_dic[key]['count']) / 100
            group_dic[key]['industry'] = key
            group_list.append(group_dic[key])

        group_list.sort(key=sortGroup,reverse = True)
        # print(group_dic)
        fo = open('product/best_days_group' + group_dic[key]['date'] + '.txt','w')
        for dic in group_list:
            fo.write(dic['industry'] + ' ' + str(dic['average']) + '\n')
        fo.close()
    print('\ndone')
        
def getGroupAllStock(industry):
    findStr = []
    all_count = len(g_business_data)
    count = 0
    for stock_dic in g_business_data:
        count = count + 1
        stock_code = stock_dic['ts_code'][0:6]
        if stock_code[0:3] == '688':
            continue
        if stock_dic['industry'] != industry:
            continue
        file_path = 'base_data/daily/' + stock_code + '.csv'
        if not os.path.exists(file_path):
            continue
        try:
            df = pd.read_csv('base_data/daily/' + stock_code[0:6] + '.csv', parse_dates=True, index_col=0)
        except Exception as e:
            continue
        # dateStr = str(timestamp.year) + '-' + str(timestamp.month) + '-' + str(timestamp.day)
        chg = df.iloc[0].at['chg']
        lclose = df.iloc[0].at['lclose']

        if chg == 'None' or lclose == 'None':
            continue
        rate = round( float(chg) / float(lclose) * 10000) / 100
        score = cal_score(stock_code = stock_code)
        findStr.append({'code':stock_dic['ts_code'],'name':stock_dic['name'],'rate':rate,'score':score})

        work_rate = round(float(count) / all_count * 1000)
        print ' ' + str(count) + ' ' + str(work_rate / 10) + '%\r',

    findStr.sort(key = lambda elem: elem['score'], reverse = True)
    fo = open('product/' + industry + '.txt','w')
    for detail in findStr:
        string = detail['code'] + ' ' + detail['name'] + ' ' + str(detail['rate']) + '% ' + str(detail['score']) + '\n'
        fo.write(string)
    fo.close()

def get_EMA(df,N,close_name = 'close'):
    for i in range(len(df)):
        if i==0:
            df.loc[i,'ema']=df.loc[i,close_name]
#            df.ix[i,'ema']=0
        if i>0:
            df.ix[i,'ema']=(2*df.ix[i,close_name]+(N-1)*df.ix[i-1,'ema'])/(N+1)
    ema=list(df['ema'])
    return ema
 
def get_MACD(df,short=12,long=26,M=9):
    # MACD 似乎数量只要够就行了，不要太多
    a=get_EMA(df,short)
    b=get_EMA(df,long)
    diff = pd.Series(a)-pd.Series(b)
    for i in range(len(df)):
        df.ix[i,'diff'] = diff[i]
    # print(df['diff'])
    for i in range(len(df)):
        if i==0:
            df.ix[i,'dea']=df.ix[i,'diff']
        if i>0:
            df.ix[i,'dea']=((M-1)*df.ix[i-1,'dea']+2*df.ix[i,'diff'])/(M+1)
    df['macd']=2*(df['diff']-df['dea'])
    return df

def getStockDataFrame(stock_code):
    file_path = 'base_data/daily/' + stock_code + '.csv'
    df = None
    if os.path.exists(file_path):
        df = pd.read_csv('base_data/daily/' + stock_code + '.csv', parse_dates=True, index_col=0)
    return df

def getDayMACD(stock_code = '300803'):
    df = getStockDataFrame(stock_code)
    df = df.iloc[::-1]
    df = get_MACD(df)
    # dif,dea,bar = talib.MACD(df.tclose.values)
    # # dif,dea,bar = talib.MACD(df.chg.values,fastperiod=12,slowperiod=26,signalperiod=9)
    return df[['diff','dea','macd']]

def getMonthMACD(stock_code = '000333'):
    df = getStockDataFrame(stock_code)
    # df = df.iloc[::-1]
    df_period = df.to_period('M')
    print(df_period.head())
    # print(df['2019-11'])
    # print(df['2016':'2017'].head(2))
    # df = get_MACD(df)
    

def getAllCate():
    all_cate = {}
    for stock_dic in g_business_data:
        cate = stock_dic['industry']
        all_cate[cate] = 1
    for key in all_cate:
        print(key)

def getQFQTSData(stock='000333.SZ',freq = 'M',start_date = '20100101'):
    #qfq = 前复权
    cur_day = time.strftime("%Y%m%d", time.localtime()) 
    stock_code = stock
    df = ts.pro_bar(ts_code=stock_code,adj='qfq',freq=freq, start_date=start_date, end_date=cur_day)
    # print(df)
    df = df.dropna(axis=0, how='any')
    # print(df)
        # time.sleep(0.1)
    return df

def findStockBySu():
    # get top
    # get stock qfq data
    # get stock macd
    # get stocks which month data show status-A
    # show that stocks
    tops = getTop(is_save = False,rule_names = ['more05','less05'],number=500)
    # tops = {'abc':[Node('300753.SZ','美的集团 家电',0, 'nyear')]}
    month_count = 15
    useful_node_string_up = []
    useful_node_string_down = []
    for _ in range(month_count):
        useful_node_string_up.append([])
        useful_node_string_down.append([])
    for key in tops:
        # stock_df = []
        count = 0
        for node_init in tops[key]:
            count = count + 1
            time.sleep(0.1)
            stock_code = node_init.stock_code

            print('get qfq ' + stock_code + ' ' + key + ' count = ' + str(count))
            print('calc ' + stock_code + '\n')

            if not os.path.exists('base_data/month/' + stock_code[0:6] + '.csv'):                   #判断是否存在文件夹如果不存在则创建为文件夹
                df = getQFQTSData(stock_code)
                # print(df)
                df.to_csv('base_data/month/' + stock_code[0:6] + '.csv')
            else:
                df = pd.read_csv('base_data/month/' + stock_code[0:6] + '.csv', parse_dates=True, index_col=0)

            if len(df) < 5:
                continue
            df = df.iloc[::-1]
            df.index = range(0,len(df)) 
            # df.reindex(index=df['trade_date'])
            # df=df.sort_values(by = 'trade_date',ascending=True)
            # print(df)
            df = get_MACD(df)
            # dif,dea,bar = talib.MACD(df.tclose.values)
            # # dif,dea,bar = talib.MACD(df.chg.values,fastperiod=12,slowperiod=26,signalperiod=9)
            df = df[['close','trade_date','diff','dea','macd']].tail(month_count + 2)
            df = df.iloc[::-1]
            # print(df)
            df.index = range(0,len(df)) 
            for cur_month in range(month_count):
                node = copy.deepcopy(node_init)
                up_list = useful_node_string_up[cur_month]
                down_list = useful_node_string_down[cur_month]

                macd0 = df.loc[cur_month,'macd']
                macd1 = df.loc[cur_month + 1,'macd']
                macd2 = df.loc[cur_month + 2,'macd']
                # print(df)
                # aa = df.ix[0,'diff']
                if macd0 > 0 and df.loc[cur_month,'diff'] > macd0 and df.loc[cur_month,'dea'] > macd0:#黄蓝线在红柱上面
                # if df.loc[0,'macd'] > 0 and df.loc[0,'diff'] > 0 and df.loc[0,'dea'] > 0:#不考虑线在柱上方
                    if df.loc[cur_month + 1,'macd'] < 0:
                        node.add_remarks(' ' + str(df.loc[cur_month,'trade_date'])[2:6] + ':' + str(round(df.loc[cur_month,'close'],1)))
                        up_list.append(node)
                        continue
                    
                    # if macd1 > 0 and df.loc[1,'diff'] > macd1 and df.loc[1,'dea'] > macd1:#
                    # if macd1 > 0:
                    #     if macd2 < 0:
                    #         useful_node.append(node)
                    #         continue
                    # macd3 = df.loc[3,'macd']
                    if macd0 > macd1 and macd1 < macd2 :
                        node.add_remarks(' mid_a ')
                        node.add_remarks(' ' + str(df.loc[cur_month,'trade_date'])[2:6] + ':' + str(round(df.loc[cur_month,'close'],1)))
                        up_list.append(node)
                        continue

                if macd0 > 0 and df.loc[cur_month,'diff'] > 0 and df.loc[cur_month,'dea'] > 0:#不考虑线在柱上方
                    if df.loc[cur_month + 1,'macd'] < 0:
                        node.add_remarks(' ' + str(df.loc[cur_month,'trade_date'])[2:6] + ':' + str(round(df.loc[cur_month,'close'],1)))
                        down_list.append(node)
                        continue
                    if macd0 > macd1 and macd1 < macd2 :
                        node.add_remarks(' mid_a ')
                        node.add_remarks(' ' + str(df.loc[cur_month,'trade_date'])[2:6] + ':' + str(round(df.loc[cur_month,'close'],1)))
                        down_list.append(node)
                        continue
                del node
                
    cur_year = int(time.strftime("%Y", time.localtime()))
    cur_month = int(time.strftime("%m", time.localtime()))

    fo = open('product/status_a.txt','w')

    for index_month in range(month_count):
        up_list = useful_node_string_up[index_month]
        up_list_len = len(up_list)
        down_list = useful_node_string_down[index_month]
        up_list.extend(down_list)
        index_count = 0
        that_year = cur_year
        that_month = cur_month - index_month - 1
        if that_month < 1:
            that_year = cur_year - 1
            that_month = that_month + 12

        fo.write('\n' + str(that_year) + '-' + str(that_month) + ':\n')
        for node in up_list:
            index_count = index_count + 1
            stock_code = node.stock_code
            try:
                csvfile = open('base_data/value/' + stock_code[0:6] + '.json', 'r')
            except Exception as e:
                print(stock_code + ' open wrong')
                print(e)

            value_table = json.load(csvfile)
            last_year = int(value_table['last_year'])
            score_year = last_year
            len_year = len(value_table['assetsAndLiabilities']['cash_rate'])
            start_index = len_year - 5 - last_year + score_year
            cash_rate = value_table['assetsAndLiabilities']['cash_rate'][start_index + 4]
            roe = value_table['profitability']['return_on_equity'][start_index + 4]
            net_profit = value_table['profitability']['net_profits'][start_index + 4]
            R_and_D_exp = value_table['profitability']['R_and_D_exps'][start_index + 4]

            r_profit_rate = 0
            if net_profit != 0:
                r_profit_rate = round(float(R_and_D_exp) / net_profit * 100,1)
            str_up = str(node) + ' 现金占比' + str(cash_rate) + '%' + ' roe' + str(roe) + '% 净利' + str(net_profit) + ' 研发占比' + str(r_profit_rate) + '% ' + '\n'
            if index_count > up_list_len:
                str_up = '** ' + str_up
            fo.write(str_up)
    print('done')


    fo.close()

def findStockBySuByFirstRate():
    tops = getTop(is_save = False,rule_names = ['less09'],number=200)
    # tops = {'abc':[Node('603986.SH','美的集团 家电',0, 'nyear')]}
    predict_up_months = 3
    happy_count = 0
    sad_count = 0
    expectation = 0
    work_count = 0
    fo = open('product/su_first_rate' + str(predict_up_months) + '.txt','w')
    for key in tops:
        # stock_df = []
        count = 0
        for node in tops[key]:
            count = count + 1
            time.sleep(0.1)
            stock_code = node.stock_code
            df = getQFQTSData(stock_code)
            print('get qfq ' + stock_code + ' ' + key + ' count = ' + str(count))
            print('calc ' + stock_code + '\n')
            if len(df) < 5:
                continue
            df = df.iloc[::-1]
            df.index = range(0,len(df)) 
            df = get_MACD(df)
            # print(df)
            df.index = range(0,len(df)) 
            first_red = False
            is_begin_find = False
            begin_stock = 0
            end_stock = 0
            len_df = len(df)
            for i in range(len(df)):
                if i == 0:
                    continue

                if not is_begin_find:
                    if df.loc[i,'macd'] >= 0:
                        first_red = True
                    else:
                        if not first_red:
                            continue
                        else:
                            is_begin_find = True
                else:
                    # is_get_red = df.loc[i,'macd'] > 0 and df.loc[i,'diff'] > df.loc[i,'dea'] and df.loc[i,'dea'] > df.loc[i,'macd']
                    is_get_red = df.loc[i,'macd'] > 0 and df.loc[i,'diff'] > 0 and df.loc[i,'dea'] > 0
                    if is_get_red:
                        if df.loc[i - 1,'macd'] < 0:
                            begin_stock = df.loc[i,'close']
                            if i + predict_up_months <= len_df - 1:
                                end_stock = df.loc[i + predict_up_months,'close']
                                difference = end_stock - begin_stock
                                if difference > 0:
                                    happy_count = happy_count + 1
                                else:
                                    sad_count = sad_count + 1
                                fo.write(str(node) + '\n profit ' + str(round(difference,2)) + '\n')
                                month_rate = round(difference / begin_stock * 100,2)
                                fo.write(str(month_rate) + '%')
                                fo.write('\n')
                                expectation = expectation + month_rate
                                work_count = work_count + 1
                                print(stock_code + ' has done')
                            break
                            
    fo.write('happy end rate: ' + str(round(float(happy_count) / (happy_count + sad_count) * 100,2)) + '%')
    fo.write('expectation: ' + str(expectation / work_count) + '%')
    fo.close()

def findBigMACD():
    path = 'base_data/month'
    folder = os.path.exists(path)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径

    global g_business_data
    cur_year = getCurYear()

    # fo = open('product/macd_rate.txt','w')
    macd_rate_table = {}
    count = 0
    for stock_dic in g_business_data:
        stock_code = stock_dic['ts_code']
        if stock_code[0:3] == '688':
            continue
        list_year = int(stock_dic['list_date'][0:4])
        if cur_year - list_year <= 1:
            continue

        print('calc ' + stock_code + '\n')
        count = count + 1
        print(str(count) + '\n')

        if not os.path.exists('base_data/month/' + stock_code[0:6] + '.csv'):
            df = getQFQTSData(stock_code)
            df.to_csv('base_data/month/' + stock_code[0:6] + '.csv')
        else:
            df = pd.read_csv('base_data/month/' + stock_code[0:6] + '.csv', parse_dates=True, index_col=0)
        
        if len(df) < 5:
            continue
        df = df.iloc[::-1]
        df.index = range(0,len(df)) 
        df = get_MACD(df)
        df = df.iloc[::-1]
        macd_add = 0
        macd_count = 0
        # print(df)
        for i in range(len(df)):
            # 10年内的就够了
            macd_count = macd_count + 1
            if macd_add > 120:
                break
            if df.loc[i,'macd'] > 0:
                macd_add = macd_add + 1

        macd_rate_table[stock_code] = {'macd_rate':round(float(macd_add) / len(df) * 100, 2),'name':stock_dic['name']}
        # 其实要多个线程的，太慢了
    json_values = json.dumps(macd_rate_table)
    fw = open('product/macd_rate.json', 'w')
    fw.write(json_values)
    fw.close()

def analyseMACDRate():
    if not os.path.exists('product/macd_rate.json'):
        findBigMACD()
    global g_stock_codes
    fo = open('product/macd_rate.json', 'r')
    macd_rate_table = json.load(fo)
    score_year = 2018
    cur_year = getCurYear()
    fo.close()
    th = TopKHeap(250)
    for key,stock_macd_rate in macd_rate_table.iteritems():
        stock_code = key[0:6]
        if stock_code[0:3] == '688':
                continue
        
        if g_stock_codes.has_key(stock_code):
            stock_dic = g_stock_codes[stock_code]
            list_year = int(stock_dic['list_date'][0:4])
            score = cal_score(stock_code[0:6],score_year)
            node = Node(key,stock_dic['name'] + ' ' + stock_dic['industry'],stock_macd_rate['macd_rate'],
                str(cur_year - list_year + 1) + 'year score:' + str(score))
            th.push(node)
    topHp = th.topk()
    topHp.sort(key=sortHp,reverse = True)
    fo = open('product/macd_rate_sort_2016.txt','w')

    count = 0
    for node in topHp:
        stock_code = node.stock_code
        try:
            csvfile = open('base_data/value/' + stock_code[0:6] + '.json', 'r')
        except Exception as e:
            print(stock_code + ' open wrong')
            print(e)
        count = count + 1
        value_table = json.load(csvfile)
        last_year = int(value_table['last_year'])
        if score_year == 0 or score_year > last_year:
            score_year = last_year
        len_year = len(value_table['assetsAndLiabilities']['cash_rate'])
        start_index = len_year - 5 - last_year + score_year

        cash_rate = value_table['assetsAndLiabilities']['cash_rate'][start_index + 4]
        roe = value_table['profitability']['return_on_equity'][start_index + 4]
        net_profit = value_table['profitability']['net_profits'][start_index + 4]
        R_and_D_exp = value_table['profitability']['R_and_D_exps'][start_index + 4]
        r_profit_rate = 0
        if net_profit != 0:
            r_profit_rate = round(float(R_and_D_exp) / net_profit * 100,1)
        fo.write(str(node) + ' 现金占比' + str(cash_rate) + '%' + ' roe' + str(roe) + '% 净利' + str(net_profit) + ' 研发占比' + str(r_profit_rate) + '% '  + str(count) + '\n')
    print('done')
    fo.close()
                
def findStockByProfit():
    tops = getTop(is_save = False,rule_names = ['more05','less05'],number=5)
    # testProfit(tops,stock_start_month = '12')
    testProfit(tops,stock_start_month = '01')

def testProfit(tops,stock_start_month = '12'):
    stock_code = '000333.SZ'
    # stock_code = '300785.SZ'
    # stock_code = '002949.SZ'
    cur_year = getCurYear()
    fo = open('product/profit_test' + stock_start_month + '.txt','w')
    for key in tops:
            # stock_df = []
            count = 0
            for node in tops[key]:
                stock_code = node.stock_code
                df = getQFQTSData(stock_code)
                # print(df)
                len_df = len(df)
                map_diff = {}
                count = 1
                str_diff = ''
                str_net = ''
                for i in range(len(df)):
                    # if df.ix[i + 12,'close']:
                    if i < (len_df - 12):
                        # df.ix[i,'year_add'] = df.ix[i,'close'] - df.ix[i + 12,'close']
                        trade_date = df.ix[i,'trade_date'] 
                        if trade_date[4:6] == stock_start_month:
                            # map_diff[str(cur_year - count)] = df.ix[i,'close'] - df.ix[i + 12,'close']
                            str_diff = str_diff + '  ' + str(cur_year - count) + ':' + str(round(df.ix[i,'close'] - df.ix[i + 12,'close'],1))
                            count = count + 1
                            if count == 5:
                                break
                    # else:
                        # df.ix[i,'year_add'] = 0
                # print(map_diff)

                csvfile = open('base_data/value/' + stock_code[0:6] + '.json', 'r')
                value_table = json.load(csvfile)
                csvfile.close()
                # net_profit = value_table['profitability']['net_profits'][-1]
                net_profits = value_table['profitability']['net_profits']
                net_start_year = 2014
                map_rate = {}
                len_net = len(net_profits)
                for i in range(len_net):
                    if i == 0:
                        continue
                    map_rate[str(net_start_year + i)] = float(net_profits[i]) / net_profits[i - 1]
                    str_net = str(net_start_year + i) + ':' + str(round((float(net_profits[i]) / net_profits[i - 1] - 1) * 100,2)) + '  ' + str_net
                # print(net_profits)
                # print(map_rate)
                
                fo.write(str(node) + '\n')
                fo.write('利润增长  ' + str_net + '\n')
                fo.write('股票增长  ' + str_diff + '\n')
                fo.write('\n\n')

    fo.close()

def togDownloadAndUpdateDailyData():
    tops = getTop(is_save = False,rule_names = ['more01'],number=500)
    stock_codes = []
    for key in tops:
        for node in tops[key]:
            stock_code = node.stock_code
            stock_codes.append({'ts_code':stock_code})

    # business_data = [{'ts_code':'002752.SZ'}]
    downloadAndUpdateDailyData(stock_codes)

def AnalyseDailyEMA():
    global g_stock_codes
    tops = getIndustryTop(is_save = False,number = 15)
    # th = TopKHeap(2)
    # th.push(Node('002770.SH','美的集团 家电',0, 'nyear'))
    # th.push(Node('002377.SZ','美的集团 家电',0, 'nyear'))
    # th.push(Node('300087.SZ','美的集团 家电',0, 'nyear'))
    # tops = {'abc':th}
    cur_year = 2020
    score_year = 2019
    # node_map = {}
    node_maps = [{},{},{},{},{},{},{},{},{},{}]
    date_list = []
    industry_count = 0
    for key in tops:
        # stock_df = []
        industry_count = industry_count + 1
        count = 0
        th = tops[key]
        topHp = th.topk()
        topHp.sort(key=sortHp,reverse = True)
        # topHp = th
        print('\n')
        for node in topHp:
            count = count + 1
            # time.sleep(0.1)
            stock_code = node.stock_code
            name = node.stock_name

            print('get qfq ' + stock_code + ' ' + name + ' count = ' + str(industry_count) + '..' + str(count))

            if not os.path.exists('base_data/daily/' + stock_code[0:6] + '.csv'):                   #判断是否存在文件夹如果不存在则创建为文件夹
                cur_day = (datetime.datetime.now() - datetime.timedelta(days=400)).strftime('%Y%m%d')
                df = getQFQTSData(stock_code,freq = 'D',start_date = cur_day)
                # print(df)
                df.to_csv('base_data/daily/' + stock_code[0:6] + '.csv')
            else:
                df = pd.read_csv('base_data/daily/' + stock_code[0:6] + '.csv', parse_dates=True, index_col=0)

            if len(df) < 100:
                continue
            df = df.iloc[::-1]
            df.index = range(0,len(df)) 
            # df.reindex(index=df['trade_date'])
            # df=df.sort_values(by = 'trade_date',ascending=True)
            # print(df)
            fast_line = get_EMA(df,14)

            slow_line = get_EMA(df,60)
            pd_diff = pd.Series(fast_line)-pd.Series(slow_line)
            pd_diff = pd_diff.iloc[::-1]
            pd_diff.index = range(0,len(pd_diff)) 
            # print(pd_diff)
            df = df.iloc[::-1]
            df.index = range(0,len(df)) 
            # print(df)
            

            for node_index in range(len(node_maps)):
                node_map = node_maps[node_index]
                start_index = node_index * 5
                up_count = 0
                for index in range(40):
                    diff = pd_diff[index + start_index]
                    if diff > 0:
                        up_count = up_count + 1
                    else:
                        # if up_count == 0:
                        break
                if up_count > 0:
                    up_count_str = str(up_count) + '天'
                    if up_count >= 40:
                        up_count_str = '40+天'
                        up_count = 40
                    close = df.ix[start_index,'close']
                    close_date = str(df.ix[start_index,'trade_date'])
                    last_close = df.ix[start_index + up_count,'close']
                    last_date = str(df.ix[start_index + up_count,'trade_date'])
                    up_count_str = up_count_str + ' ' + close_date + ':' + str(round(close,2)) + ' ' + last_date +  ':' + str(round(last_close,2))
                    # print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),stock_code + ' ' + name + ' ' + up_count_str + '\n'))
                    # print(up_count_str)
                    node_copy = copy.deepcopy(node)
                    node_copy.add_remarks(' ' + up_count_str)
                    industry_name = g_stock_codes[stock_code[0:6]]['industry']
                    if not node_map.has_key(industry_name):
                        node_map[industry_name] = []
                    useful_node = node_map[industry_name]
                    useful_node.append(node_copy)

    for node_index in range(len(node_maps)):
        node_map = node_maps[node_index]
        cur_day = (datetime.datetime.now() - datetime.timedelta(days=node_index * 7)).strftime('%Y%m%d')
        fo = open('product/industry_ema/daily_ema_industry_' + cur_day + '.txt','w')

        key_list = []
        for key in node_map:
            key_list.append(key)
        key_list.sort()

        for index in range(len(key_list)):
            key = key_list[index]
            useful_node = node_map[key]
            fo.write(str(key) + '%\n')
            for node in useful_node:
                stock_code = node.stock_code
                try:
                    csvfile = open('base_data/value/' + stock_code[0:6] + '.json', 'r')
                except Exception as e:
                    print(stock_code + ' open wrong')
                    print(e)
                value_table = json.load(csvfile)
                last_year = int(value_table['last_year'])
                if score_year == 0 or score_year > last_year:
                        score_year = last_year
                len_year = len(value_table['assetsAndLiabilities']['cash_rate'])
                start_index = len_year - 5 - last_year + score_year
                cash_rate = value_table['assetsAndLiabilities']['cash_rate'][start_index + 4]
                roe = value_table['profitability']['return_on_equity'][start_index + 4]
                net_profit = value_table['profitability']['net_profits'][start_index + 4]
                R_and_D_exp = value_table['profitability']['R_and_D_exps'][start_index + 4]
                r_profit_rate = 0
                if net_profit != 0:
                    r_profit_rate = round(float(R_and_D_exp) / net_profit * 100,1)

                fo.write(str(node) + ' 现金占比' + str(cash_rate) + '%' + ' roe' + str(roe) + '% 净利' + str(net_profit) + ' 研发占比' + str(r_profit_rate) + '%\n')
        fo.close()

def findByCurrentDownAndUp():
    global g_stock_codes
    tops = getIndustryTop(is_save = False,number = 15)
    # th = TopKHeap(2)
    # th.push(Node('002770.SH','美的集团 家电',0, 'nyear'))
    # th.push(Node('002377.SZ','美的集团 家电',0, 'nyear'))
    # th.push(Node('300087.SZ','美的集团 家电',0, 'nyear'))
    # tops = {'abc':th}
    cur_year = 2020
    score_year = 2019
    # node_map = {}
    down_node = []
    up_node = []
    industry_count = 0
    for key in tops:
        # stock_df = []
        industry_count = industry_count + 1
        count = 0
        th = tops[key]
        topHp = th.topk()
        topHp.sort(key=sortHp,reverse = True)
        # topHp = th
        print('\n')
        for node in topHp:
            count = count + 1
            # time.sleep(0.1)
            stock_code = node.stock_code
            name = node.stock_name

            print('get qfq ' + stock_code + ' ' + name + ' count = ' + str(industry_count) + '..' + str(count))

            if not os.path.exists('base_data/daily/' + stock_code[0:6] + '.csv'):                   #判断是否存在文件夹如果不存在则创建为文件夹
                cur_day = (datetime.datetime.now() - datetime.timedelta(days=400)).strftime('%Y%m%d')
                df = getQFQTSData(stock_code,freq = 'D',start_date = cur_day)
                # print(df)
                df.to_csv('base_data/daily/' + stock_code[0:6] + '.csv')
            else:
                df = pd.read_csv('base_data/daily/' + stock_code[0:6] + '.csv', parse_dates=True, index_col=0)

            if len(df) < 100:
                continue
            df.index = range(0,len(df)) 
            
            cur_close = df.ix[0,'close']
            biggest_close = 0
            smallest_close = cur_close
            for index in range(20):
                daily_close = df.ix[index,'close']
                if daily_close > biggest_close:
                    biggest_close = daily_close
                if daily_close < smallest_close:
                    smallest_close = daily_close

            if biggest_close / cur_close > 1.1:
                node_copy = copy.deepcopy(node)
                down_node.append(node_copy)

            if smallest_close * 1.1 < cur_close:
                node_copy = copy.deepcopy(node)
                up_node.append(node_copy)

    fo_down = open('product/industry_ema/daily_ema_down.txt','w')
    fo_up = open('product/industry_ema/daily_ema_up.txt','w')
    for node_index in range(len(down_node)):
        node = down_node[node_index]
        stock_code = node.stock_code
        try:
            csvfile = open('base_data/value/' + stock_code[0:6] + '.json', 'r')
        except Exception as e:
            print(stock_code + ' open wrong')
            print(e)
        value_table = json.load(csvfile)
        last_year = int(value_table['last_year'])
        if score_year == 0 or score_year > last_year:
                score_year = last_year
        len_year = len(value_table['assetsAndLiabilities']['cash_rate'])
        start_index = len_year - 5 - last_year + score_year
        cash_rate = value_table['assetsAndLiabilities']['cash_rate'][start_index + 4]
        roe = value_table['profitability']['return_on_equity'][start_index + 4]
        net_profit = value_table['profitability']['net_profits'][start_index + 4]
        R_and_D_exp = value_table['profitability']['R_and_D_exps'][start_index + 4]
        r_profit_rate = 0
        if net_profit != 0:
            r_profit_rate = round(float(R_and_D_exp) / net_profit * 100,1)
        fo_down.write(str(node) + ' 现金占比' + str(cash_rate) + '%' + ' roe' + str(roe) + '% 净利' + str(net_profit) + ' 研发占比' + str(r_profit_rate) + '%\n')
    fo_down.close()

    for node_index in range(len(up_node)):
        node = up_node[node_index]
        stock_code = node.stock_code
        try:
            csvfile = open('base_data/value/' + stock_code[0:6] + '.json', 'r')
        except Exception as e:
            print(stock_code + ' open wrong')
            print(e)
        value_table = json.load(csvfile)
        last_year = int(value_table['last_year'])
        if score_year == 0 or score_year > last_year:
                score_year = last_year
        len_year = len(value_table['assetsAndLiabilities']['cash_rate'])
        start_index = len_year - 5 - last_year + score_year
        cash_rate = value_table['assetsAndLiabilities']['cash_rate'][start_index + 4]
        roe = value_table['profitability']['return_on_equity'][start_index + 4]
        net_profit = value_table['profitability']['net_profits'][start_index + 4]
        R_and_D_exp = value_table['profitability']['R_and_D_exps'][start_index + 4]
        r_profit_rate = 0
        if net_profit != 0:
            r_profit_rate = round(float(R_and_D_exp) / net_profit * 100,1)
        fo_up.write(str(node) + ' 现金占比' + str(cash_rate) + '%' + ' roe' + str(roe) + '% 净利' + str(net_profit) + ' 研发占比' + str(r_profit_rate) + '%\n')
    fo_up.close()

def getValueFromJson(para_dic = {'stock_code':'300753','target_name':'return_on_equity','years':[2018,2017]}):#5年内
    # para_dic = {'stock_code':'300753','target_name':'return_on_equity','years':[2018,2017]}
    stock_code = para_dic['stock_code']
    target_name = para_dic['target_name']
    years = para_dic['years']
    category_dict = {'profitability':{'return_on_equity':1}}
    category_name = 'profitability'
    for key in category_dict:
        if category_dict[key].has_key(target_name):
            category_name = key
            break
    try:
        csvfile = open('base_data/value/' + stock_code[0:6] + '.json', 'r')
    except Exception as e:
        print(stock_code + ' open wrong')
        print(e)
    value_table = json.load(csvfile)

    target_values = {}
    last_year = int(value_table['last_year'])
    # print(value_table[category_name][target_name])
    len_year = len(value_table['assetsAndLiabilities']['cash_rate'])
    for score_year in years:
        index = score_year - last_year + len_year - 1
        if index >= len_year or index < 0:
            target_values[str(score_year)] = 0
        target_values[str(score_year)] = value_table[category_name][target_name][index]
    # print(target_values)
    return target_values

def analyseROE():
    tops = getTop(is_save = False,rule_names = ['more05','less05'],number=400)
    # tops = {'abc':[Node('300753.SZ','美的集团 家电',0, 'nyear')]}
    useful_node = []
    count = 0
    fo = open('product/roe_with_price.txt','w')

    for key in tops:
        # stock_df = []
        for node_init in tops[key]:
            count = count + 1
            time.sleep(0.1)
            stock_code = node_init.stock_code

            print('get qfq ' + stock_code + ' ' + key + ' count = ' + str(count))
            print('calc ' + stock_code + '\n')
            
            years = [2018,2017,2016,2015,2014]
            roes = getValueFromJson({'stock_code':stock_code,'target_name':'return_on_equity','years':years})

            fo.write(str(node_init) + '\n')

            if not os.path.exists('base_data/month/' + stock_code[0:6] + '.csv'):                   #判断是否存在文件夹如果不存在则创建为文件夹
                df = getQFQTSData(stock_code)
                # print(df)
                df.to_csv('base_data/month/' + stock_code[0:6] + '.csv')
            else:
                df = pd.read_csv('base_data/month/' + stock_code[0:6] + '.csv', parse_dates=True, index_col=0)

            if len(df) < 5:
                continue

            year_price = {}
            for year in years:
                year_price[str(year + 1)] = {}
            # print(df)
            year_index = 0
            year = years[year_index]
            month_begin = '04'
            month_end = '12'
            month_str1 = str(year + 1) + month_begin
            month_str2 = str(year + 1) + month_end
            for i in range(len(df)):
                trade_date = str(df.ix[i,'trade_date'])
                if trade_date[0:6] == month_str2:
                    year_price[str(year + 1)][month_end] = round(df.loc[i,'close'],1)
                if trade_date[0:6] == month_str1:
                    year_index = year_index + 1
                    if year_index >= len(years):
                        break
                    year_price[str(year + 1)][month_begin] = round(df.ix[i,'close'],1)
                    year = years[year_index]
                    month_str1 = str(year + 1) + month_begin
                    month_str2 = str(year + 1) + month_end
                
            fo.write(str(roes) + '\n')
            fo.write(str(year_price) + '\n\n')
            # print(roes)
            # print(year_price)
    fo.close()


def updateAll():
    def mkdir(path):
        folder = os.path.exists(path)
        if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
            print (path + " create")
        else:
            print (path + " is exist")
		
    mkdir('base_data\\business')
    mkdir('base_data\\daily')
    mkdir('base_data\\dividend')
    mkdir('base_data\\value')
    mkdir('product')
    
    global g_dividend_data
    pro = tushare_get.getPro()
    tushare_get.getBusinessData(pro)
    initGStockCodes()
    downloadFinanceData()
    g_dividend_data = getDividendData(pro,g_business_data)
    # downloadAndUpdateDailyData(g_business_data)# Sometimes,just update high-score stock
    # findBigMACD()
    analyseAllData()

def main():
    global g_dividend_data
    initGStockCodes()
    pro = tushare_get.getPro()
    # findStockBySu()
    # tushare_get.getDividendFromTSData(pro,g_business_data)
    # getQFQTSData(g_business_data)
    # downloadAndUpdateDailyData(g_business_data)
    # togDownloadAndUpdateDailyData()
    # g_dividend_data = getDividendData(pro,g_business_data)
    # g_dividend_data = getAllotmentData(pro,g_business_data)
    g_dividend_data = getDividendData(pro)
    # deleteFile()
    # downloadFinanceData()
    # analyseAllData()
    # stock_code = '600519'
    # downloadTable(stock_code,'lrb')
    # downloadTable(stock_code,'zcfzb')
    # downloadTable(stock_code,'xjllb')
    # analyseData(stock_code = stock_code)
    # score = cal_score(stock_code,2017)
    # print(score)
    # score = cal_score(stock_code,2018)
    # print(score)
    # score = cal_score(stock_code,2019)
    # print(score)
    # print('score: ' + str(score))
    #print time.strftime("%Y-%m-%d", time.localtime()) 
    # getTopAllScore()
    # getIndustryTop()
    #getAllCate()
    # pandasTest('002770')
    # getDaysBestGroup()
    # getGroupAllStock(u'商品城')
    # getMonthMACD()
    # findStockByProfit()
    # findBigMACD()
    # findStockBySuByFirstRate()
    # analyseMACDRate()
    # getQFQTSData() 
    # AnalyseDailyEMA()
    crawlStockValueFromWeb()
    # getValueFromJson()
    # analyseROE()
    # findByCurrentDownAndUp()
    # getTop()
    

if __name__ == '__main__':
    main()
    # updateAll()