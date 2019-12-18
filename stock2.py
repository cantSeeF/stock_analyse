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
import os
import threading

import bs4
import stock as tushare_get
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import heapq

class Node:
    def __init__(self,stock_code,stock_name,score):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.score = score

    def __str__(self):
		return '%s  %s  %s' %(self.stock_code,self.stock_name,self.score)

    def __lt__(self,other):
        if isinstance(other,Node):
            return self.score < other.score
        # return self.score < other.score

    def __gt__(self,other): 
        if isinstance(other,Node):
            return self.score > other.score

    def __eq__(self,other): 
        if isinstance(other,Node):
            return self.score == other.score

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

g_stock_head_codes = ['000','002','300','600','601','603']#600最多，可以加线程
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

# def downloadThread1(talbeName):
#     global g_stock_head_codes
#     print(talbeName)
#     print(g_stock_head_codes)

#     for sd in range(0,100):
#         os.path.exists('base_data/lrb000;l001.csv')
#         print(talbeName)
#         time.sleep(1)

def downloadData():
    #判断是否有更新(最新季度？)，存在，再下载
    # 创建线程
    try:
        thread_list = []
        for stock_head in g_stock_head_codes:
            for talbeName in g_table_names:
                # thread.start_new_thread(downloadThread1, (str(talbeName),)) 
                t1= threading.Thread(target=downloadThread,args=(str(stock_head),str(talbeName),))
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

def downloadThread(stock_head,talbeName):
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

def showYear(cur_year):
    if not cur_year:
        cur_year = time.strftime("%Y", time.localtime()) 
    cur_year = int(cur_year)
    # print('|' + 'hej'.ljust(20) + '|' + 'hej'.rjust(20) + '|' + 'hej'.center(20) + '|')
    # print('hej'.center(20, '+')) #一共有20个字符, 中间使用hej, 其他用+填充
    str_year = ''
    for index in range(5,0,-1):
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
    dividend_data = g_dividend_data[stock_code]

    if not lrb_data or not xjllb_data or not zcfzb_data:
        print('loss ' + stock_code + ', unlisted')
        return
    
    local_time = time.localtime()
    cur_year = int(time.strftime("%Y", local_time))
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    max_count = 5
    indexes_for_cal_lrb = []
    for index in range(len(lrb_data['report_date'])):
        yyyymmdd = lrb_data['report_date'][index].split('-')
        if len(yyyymmdd) < 3:
            continue
        single_year = int(yyyymmdd[0])
        single_month = int(yyyymmdd[1]) 
        single_day = int(yyyymmdd[2])

        if single_year < cur_year and single_month == 12 and single_day == 31 and len(indexes_for_cal_lrb) < max_count:
            indexes_for_cal_lrb.append(index)

    len_of_year = len(indexes_for_cal_lrb)

    indexes_for_cal_zcfzb = []
    for index in range(len(zcfzb_data['report_date'])):
        yyyymmdd = zcfzb_data['report_date'][index].split('-')
        if len(yyyymmdd) < 3:
            continue
        single_year = int(yyyymmdd[0])
        single_month = int(yyyymmdd[1]) 
        single_day = int(yyyymmdd[2])

        if single_year < cur_year and single_month == 12 and single_day == 31 and len(indexes_for_cal_zcfzb) < max_count:
            indexes_for_cal_zcfzb.append(index)

    indexes_for_cal_xjllb = []
    for index in range(len(xjllb_data['report_date'])):
        yyyymmdd = xjllb_data['report_date'][index].split('-')
        if len(yyyymmdd) < 3:
            continue
        single_year = int(yyyymmdd[0])
        single_month = int(yyyymmdd[1]) 
        single_day = int(yyyymmdd[2])

        if single_year < cur_year and single_month == 12 and single_day == 31 and len(indexes_for_cal_xjllb) < max_count:
            indexes_for_cal_xjllb.append(index)


    value_table = {'year':[cur_year - 5,cur_year - 4,cur_year - 3,cur_year - 2,cur_year - 1]}
    #print(indexes_for_cal_lrb)
    str_result = zhJust(u'资产负债比率（占总资产%：）    ') + showYear(cur_year)
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

    str_result = zhJust(u'类别      财务比例    ') + showYear(cur_year)
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
        index = indexes_for_cal_zcfzb[index]
        op_costs = lrb_data['op_costs'][index]
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
                if single_month == 12 and single_day == 31:
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

    for index in range(len_of_year - 1,-1,-1):
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        yyyymmdd = zcfzb_data['report_date'][index].split('-')
        yyyy = yyyymmdd[0]
        for single_dividend in dividend_data:
            if single_dividend['year'] == yyyy:
                dividend_level.append(single_dividend)
                if len(dividend_level) >= 5:
                    break
        if len(dividend_level) >= 5:
            break

    len_of_year = len(dividend_level)
    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        yyyymmdd = zcfzb_data['report_date'][index].split('-')
        yyyy = yyyymmdd[0]
        for single_dividend in dividend_data:
            if single_dividend['year'] == yyyy:
                payment_days = payment_days + single_dividend['payment_day'].ljust(15)
    str_result = zhJust(u'类别      分红发放日    ') + payment_days

    if is_show:
        print('\n')
        print("\033[0;37;42m{0}\033[0m".format(str_result))
        print(zhJust(u'分红水平'))
    
    str_result = zhJust(u'          每10股分红（元）',29)

    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[index]
        yyyymmdd = zcfzb_data['report_date'][index].split('-')
        yyyy = yyyymmdd[0]
        for single_dividend in dividend_data:
            if single_dividend['year'] == yyyy:
                str_result = str_result + str(single_dividend['dividend']).ljust(15)
                break
    if is_show:
        print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          分红率')

    for index in range(len_of_year - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal_zcfzb[indexOfSingle]
        yyyymmdd = zcfzb_data['report_date'][index].split('-')
        yyyy = yyyymmdd[0]
        for single_dividend in dividend_data:
            if single_dividend['year'] == yyyy:
                dividend = 0
                if single_dividend['dividend'] != '--':
                    dividend = float(single_dividend['dividend'])
                payIn_capital = zcfzb_data['payIn_capital'][index]
                index = indexes_for_cal_lrb[indexOfSingle]
                net_profit_company = lrb_data['net_profit_company'][index]
                dividend_level[len_of_year - indexOfSingle - 1]['dividend_rate'] = utils.cal_dividend_rate(dividend,payIn_capital,net_profit_company)
                str_result = str_result + str(dividend_level[len_of_year - indexOfSingle - 1]['dividend_rate']).ljust(15)
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
            #if not os.path.exists(file_path):
            if True:
                print('analyse ' + stock_code)
                analyseData(stock_code = stock_code,is_show=False)
            else:
                print('json ' + stock_code + ' is exist')


def cal_score(stock_code):
    try:
        csvfile = open('base_data/value/' + stock_code + '.json', 'r')
    except Exception as e:
        print(stock_code + ' open wrong')
        print(e)
        return 0

    value_table = json.load(csvfile)
    if len(value_table['profitability']['return_on_equity']) < 5:
        return 0
    
    tatal_score = 0
    #股东权益报酬率(%) RoE
    sum_roe = 0
    is_roe_m0 = False
    min_roe = 10000
    for roe in value_table['profitability']['return_on_equity']:
        if roe < 0:
            is_roe_m0 = True
        min_roe = min(min_roe,roe)
        sum_roe = sum_roe + roe
    average_roe = sum_roe / len(value_table['profitability']['return_on_equity'])
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
    for roa in value_table['profitability']['return_on_total_assets']:
        sum_roa = sum_roa + roa
        min_roa = min(min_roa,roa)
    average_roa = sum_roa / len(value_table['profitability']['return_on_total_assets'])

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
    for net_profit in value_table['profitability']['net_profits']:
        sum_net_profit = sum_net_profit + net_profit
    average_net_profit = sum_net_profit / len(value_table['profitability']['net_profits'])

    if sum_net_profit == 0:
        tatal_score = tatal_score + 0
    elif average_net_profit >= 10000:
        tatal_score = tatal_score + 150
    elif average_net_profit >= 1000:
        tatal_score = tatal_score + 100

    #现金状况 分析
    #总资产周转率（次）
    sum_total_assets_turnover = 0
    for total_assets_turnover in value_table['management_capacity']['total_assets_turnover']:
        sum_total_assets_turnover = sum_total_assets_turnover + total_assets_turnover
    average_total_assets_turnover = sum_total_assets_turnover / len(value_table['management_capacity']['total_assets_turnover'])


    #现金与约当现金
    sum_cash_rate = 0
    for cash_rate in value_table['assetsAndLiabilities']['cash_rate']:
        sum_cash_rate = sum_cash_rate + cash_rate
    average_cash_rate = sum_cash_rate / len(value_table['assetsAndLiabilities']['cash_rate'])

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
    for average_cash_days in value_table['management_capacity']['average_cash_days']:
        sum_average_cash_days = sum_average_cash_days + average_cash_days
    average_average_cash_days = sum_average_cash_days / len(value_table['management_capacity']['average_cash_days'])
    
    if sum_average_cash_days == 0:
        tatal_score = tatal_score + 0
    elif average_average_cash_days <= 30:
        tatal_score = tatal_score + 20

    #销货日数(日)
    #平均销货日数（平均在库天数）
    sum_average_sale_days = 0
    for average_sale_days in value_table['management_capacity']['average_sale_days']:
        sum_average_sale_days = sum_average_sale_days + average_sale_days
    average_average_sale_days = sum_average_sale_days / len(value_table['management_capacity']['average_sale_days'])

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
    for gross_profit_margin in value_table['profitability']['gross_profit_margin']:
        sum_gross_profit_margin = sum_gross_profit_margin + gross_profit_margin
        min_gross_profit_margin = min(min_gross_profit_margin,gross_profit_margin)
        max_gross_profit_margin = max(max_gross_profit_margin,gross_profit_margin)
    average_gross_profit_margin = sum_gross_profit_margin / len(value_table['profitability']['gross_profit_margin'])
    
    if sum_gross_profit_margin == 0 or min_gross_profit_margin <= 5:
        tatal_score
    elif min_gross_profit_margin / average_gross_profit_margin >= 0.7 and max_gross_profit_margin / average_gross_profit_margin <= 1.3:
        tatal_score = tatal_score + 50
    
    #经营安全边际率(%)
    sum_operating_margin_of_safety = 0
    min_operating_margin_of_safety = 100
    for operating_margin_of_safety in value_table['profitability']['operating_margin_of_safety']:
        sum_operating_margin_of_safety = sum_operating_margin_of_safety + operating_margin_of_safety
        min_operating_margin_of_safety = min(min_operating_margin_of_safety,operating_margin_of_safety)
    average_operating_margin_of_safety = sum_operating_margin_of_safety / len(value_table['profitability']['operating_margin_of_safety'])

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
        if net_profits[4] > net_profits[3]:
            tatal_score = tatal_score + 30
        else:
            tatal_score = tatal_score - 30

        if net_profits[3] > net_profits[2]:
            tatal_score = tatal_score + 25
        else:
            tatal_score = tatal_score - 25

        if net_profits[2] > net_profits[1]:
            tatal_score = tatal_score + 20
        else:
            tatal_score = tatal_score - 20

        if net_profits[1] > net_profits[0]:
            tatal_score = tatal_score + 15
        else:
            tatal_score = tatal_score - 15

    #营业活动现金流量

    sum_net_flow_from_op = 0
    sum_net_flow_from_ops = value_table['net_flow_from_ops']
    for net_flow_from_op in sum_net_flow_from_ops:
        sum_net_flow_from_op = sum_net_flow_from_op + net_flow_from_op  
    
    if sum_net_flow_from_op != 0:
        if sum_net_flow_from_ops[4] > sum_net_flow_from_ops[3]:
            tatal_score = tatal_score + 30
        else:
            tatal_score = tatal_score - 30

        if sum_net_flow_from_ops[3] > sum_net_flow_from_ops[2]:
            tatal_score = tatal_score + 25
        else:
            tatal_score = tatal_score - 25

        if sum_net_flow_from_ops[2] > sum_net_flow_from_ops[1]:
            tatal_score = tatal_score + 20
        else:
            tatal_score = tatal_score - 20

        if sum_net_flow_from_ops[1] > sum_net_flow_from_ops[0]:
            tatal_score = tatal_score + 15
        else:
            tatal_score = tatal_score - 15

    sum_dividend = 0

    for dividend_level in value_table['dividend_level']:
        dividend = 0
        if dividend_level['dividend'] != '--':
            dividend = float(dividend_level['dividend'])
        sum_dividend = sum_dividend + dividend
    if len(value_table['dividend_level']) == 0:
        average_dividend = 0
    else:
        average_dividend = sum_dividend / len(value_table['dividend_level'])
    
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

def getDividendData(pro,business_data = []):
    #business_data = [{'ts_code':'600117.SH'}]
    #tushare is bad.
    # It's better that go to 163 to grap some data. At less do not waiting.
    dividend_dic = {}
    if os.path.exists("base_data/dividend/dividend.json"):
        fo = open("base_data/dividend/dividend.json", "r")
        dividend_dic = json.load(fo)
        fo.close()
    for stock_dic in business_data:
        stock_code = stock_dic['ts_code'][0:6]
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
                print(stock_code + ' dividend has download ! ')
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
    dividend_dic_json = json.dumps(dividend_dic)
    fo = open("base_data/dividend/dividend.json", "w")
    fo.write(dividend_dic_json)
    fo.close()
    print('done!')
    return dividend_dic

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
        stock_code = stock_dic['ts_code'][0:6]
        g_stock_codes[stock_code] = stock_dic
    business_file.close()

def sortHp(node):
    return node.score

def getTop():
    global g_business_data
    th = TopKHeap(200)
    #count = 1
    for stock_dic in g_business_data:
        stock_code = stock_dic['ts_code'][0:6]
        if stock_code[0:3] == '688':
            continue
        score = cal_score(stock_code = stock_code)
        node = Node(stock_code,stock_dic['name'] + ' ' + stock_dic['industry'],score)
        th.push(node)
        #count = count + 1
        # if count > 100:
        #     break
    
    topHp = th.topk()
    topHp.sort(key=sortHp,reverse = True)

    fo = open('best_long_term_shares.txt','w')

    for node in topHp:
        fo.write(str(node) + '\n')
        #print(node)
    fo.close()

def main():
    global g_dividend_data
    initGStockCodes()
    pro = tushare_get.getPro()
    #g_dividend_data = getDividendData(pro,g_business_data)
    g_dividend_data = getDividendData(pro)
    #deleteFile()
    #downloadData()
    #analyseAllData()
    # downloadTable('003816','lrb')
    # downloadTable('003816','zcfzb')
    # downloadTable('003816','xjllb')
    # analyseData(stock_code = '003816')
    #print time.strftime("%Y-%m-%d", time.localtime()) 
    getTop()
    

if __name__ == '__main__':
    main()