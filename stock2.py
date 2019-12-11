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
#lrb，zcfzb，xjllb,zycwzb 利润，资产负债，现金流量，主要财务指标

g_start_stock = 0
g_end_stock = 1000

g_stock_head_codes = ['000','300','600','601','603']#600最多，可以加线程
g_table_names = ['lrb','zcfzb','xjllb']
g_is_test = False
if g_is_test:
    g_stock_head_codes = ['600']
    g_start_stock = 288
    g_end_stock = 289

# mylock = thread.allocate_lock() 

def downloadThread1(talbeName):
    global g_stock_head_codes
    print(talbeName)
    print(g_stock_head_codes)

    for sd in range(0,100):
        os.path.exists('base_data/lrb000;l001.csv')
        print(talbeName)
        time.sleep(1)

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
        file_path = 'base_data/' + talbeName + stock_code + '.csv'
        # print(file_path)
        try:
            if os.path.exists(file_path):
                continue
        except Exception as e:
            print(e)
            return
        url = 'http://quotes.money.163.com/service/' + talbeName + '_' + stock_code +'.html'
        while True:
            try:
                content = web.urlopen(url,timeout=2).read()
                #print(content)
                a_utf_8 = content.decode('gb2312').encode('utf-8')
                with open('base_data/' + talbeName + stock_code + '.csv','wb') as f:
                    f.write(a_utf_8)
                    f.close()
                print(talbeName + stock_code)
                time.sleep(0.5)
                break
            except Exception as e:
                if str(e) =='HTTP Error 404: Not Found':
                    print('has not ' + talbeName + stock_code)
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

def analyseData(stock_code,is_show = False):
    lrb_data = loadData(stock_code,'lrb')
    zcfzb_data = loadData(stock_code,'zcfzb')
    xjllb_data = loadData(stock_code,'xjllb')

    if not lrb_data or not xjllb_data or not zcfzb_data:
        print('loss data')
        return
    
    local_time = time.localtime()
    cur_year = int(time.strftime("%Y", local_time))
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
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


    value_table = {'year':[cur_year - 5,cur_year - 4,cur_year - 3,cur_year - 2,cur_year - 1]}
    #print(indexes_for_cal)
    str_result = zhJust(u'资产负债比率（占总资产%：）    ') + showYear(cur_year)
    print("\033[0;37;42m{0}\033[0m".format(str_result))
    
    assetsAndLiabilities = {}
    value_table['assetsAndLiabilities'] = assetsAndLiabilities
    str_result = zhJust(u'     现金与约当现金')
    cash_rate = []
    assetsAndLiabilities['cash_rate'] = cash_rate
    indexOfSingle = 0
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        money_funds = zcfzb_data['money_funds'][index]
        transactional_finacial_asset = zcfzb_data['transactional_finacial_asset'][index]
        derivative_finacial_asset = zcfzb_data['derivative_finacial_asset'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        cash_rate.append(utils.cal_cash_rate(money_funds,transactional_finacial_asset,derivative_finacial_asset,tatol_assets))
        str_result = str_result + str(cash_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     应收账款')
    accounts_receivable_rate = []
    assetsAndLiabilities['accounts_receivable_rate'] = accounts_receivable_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        accounts_receivable = zcfzb_data['accounts_receivable'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        accounts_receivable_rate.append(utils.cal_accounts_receivable_rate(accounts_receivable,tatol_assets))
        str_result = str_result + str(accounts_receivable_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     存货')
    stock_rate = []
    assetsAndLiabilities['stock_rate'] = stock_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        stock = zcfzb_data['stock'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        stock_rate.append(utils.cal_stock_rate(stock,tatol_assets))
        str_result = str_result + str(stock_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))
    
    str_result = zhJust(u'     流动资产')
    total_current_assets_rate = []
    assetsAndLiabilities['total_current_assets_rate'] = total_current_assets_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        total_current_assets = zcfzb_data['total_current_assets'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_current_assets_rate.append(utils.cal_total_current_assets_rate(total_current_assets,tatol_assets))
        str_result = str_result + str(total_current_assets_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))
    
    str_result = zhJust(u'     总资产')
    total_assets = []
    assetsAndLiabilities['total_assets'] = total_assets
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        total_assets.append(100)
        str_result = str_result + '100'.ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     应付账款')
    accounts_payable_rate = []
    assetsAndLiabilities['accounts_payable_rate'] = accounts_payable_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        accounts_payable = zcfzb_data['accounts_payable'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        accounts_payable_rate.append(utils.cal_accounts_payable_rate(accounts_payable,tatol_assets))
        str_result = str_result + str(accounts_payable_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     流动负债')
    total_current_liability_rate = []
    assetsAndLiabilities['total_current_liability_rate'] = total_current_liability_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_current_liability_rate.append(utils.cal_total_current_liability_rate(total_current_liability,tatol_assets))
        str_result = str_result + str(total_current_liability_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     长期负债')
    total_noncurrent_liability_rate = []
    assetsAndLiabilities['total_noncurrent_liability_rate'] = total_noncurrent_liability_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        total_noncurrent_liability = zcfzb_data['total_noncurrent_liability'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_noncurrent_liability_rate.append(utils.cal_total_noncurrent_liability_rate(total_noncurrent_liability,tatol_assets))
        str_result = str_result + str(total_noncurrent_liability_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     股东权益')
    total_owners_equity_rate = []
    assetsAndLiabilities['total_owners_equity_rate'] = total_owners_equity_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        total_owners_equity = zcfzb_data['total_owners_equity'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_owners_equity_rate.append(utils.cal_total_owners_equity_rate(total_owners_equity,tatol_assets))
        str_result = str_result + str(total_owners_equity_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     总负债加股东权益')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        str_result = str_result + '100'.ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print('\n')
    str_result = zhJust(u'类别      财务比例    ') + showYear(cur_year)
    print("\033[0;37;42m{0}\033[0m".format(str_result))

    print(zhJust(u'财务结构'))
    
    financial_ratio = {}
    value_table['financial_ratio'] = financial_ratio
    str_result = zhJust(u'          负债占资产比率')
    total_liability_rate = []
    financial_ratio['total_liability_rate'] = total_liability_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        total_liability = zcfzb_data['total_liability'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_liability_rate.append(utils.cal_total_liability_rate(total_liability,tatol_assets))
        str_result = str_result + str(total_liability_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          长期资金占不动产/厂房及设备比率')
    longterm_funds_rate = []
    financial_ratio['longterm_funds_rate'] = longterm_funds_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        total_owners_equity = zcfzb_data['total_owners_equity'][index]
        total_noncurrent_liability = zcfzb_data['total_noncurrent_liability'][index]
        fixed = zcfzb_data['fixed'][index]
        construction_in_progress = zcfzb_data['construction_in_progress'][index]
        engineer_material = zcfzb_data['engineer_material'][index]
        longterm_funds_rate.append(utils.cal_longterm_funds_rate(total_owners_equity,total_noncurrent_liability,fixed,construction_in_progress,engineer_material))
        str_result = str_result + str(longterm_funds_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print(zhJust(u'偿债能力'))
    solvency = {}
    value_table['solvency'] = solvency
    str_result = zhJust(u'          流动比率')
    current_rate = []
    solvency['current_rate'] = current_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        total_current_assets = zcfzb_data['total_current_assets'][index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        current_rate.append(utils.cal_current_rate(total_current_assets,total_current_liability))
        str_result = str_result + str(current_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          速动比率')
    quick_rate = []
    solvency['quick_rate'] = quick_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        total_current_assets = zcfzb_data['total_current_assets'][index]
        stock = zcfzb_data['stock'][index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        quick_rate.append(utils.cal_quick_rate(total_current_assets,stock,total_current_liability))
        str_result = str_result + str(quick_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print(zhJust(u'经营能力'))
    management_capacity = {}
    value_table['management_capacity'] = management_capacity
    receivable_turnover_rate = []
    management_capacity['receivable_turnover_rate'] = receivable_turnover_rate
    str_result = zhJust(u'          应收账款周转率（次）')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        op_in = lrb_data['op_in'][index]
        accounts_receivable = zcfzb_data['accounts_receivable'][index]
        receivable_turnover_rate.append(utils.cal_receivable_turnover_rate(op_in,accounts_receivable))
        str_result = str_result + str(receivable_turnover_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          平均收现日数')
    average_cash_days = []
    management_capacity['average_cash_days'] = average_cash_days
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        op_in = lrb_data['op_in'][index]
        accounts_receivable = zcfzb_data['accounts_receivable'][index]
        average_cash_days.append(utils.cal_average_cash_days(op_in,accounts_receivable))
        str_result = str_result + str(average_cash_days[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          存货周转率（次）')
    inventory_turnover = []
    management_capacity['inventory_turnover'] = inventory_turnover
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        op_costs = lrb_data['op_costs'][index]
        stock = zcfzb_data['stock'][index]
        inventory_turnover.append(utils.cal_inventory_turnover(op_costs,stock))
        str_result = str_result + str(inventory_turnover[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          平均销货日数（平均在库天数）')
    average_sale_days = []
    management_capacity['average_sale_days'] = average_sale_days
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        op_costs = lrb_data['op_costs'][index]
        stock = zcfzb_data['stock'][index]
        average_sale_days.append(utils.cal_average_sale_days(op_costs,stock))
        str_result = str_result + str(average_sale_days[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          不动产及厂房及设备周转率（次）')
    equipment_turnover = []
    management_capacity['equipment_turnover'] = equipment_turnover
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        op_in = lrb_data['op_in'][index]
        fixed = zcfzb_data['fixed'][index]
        construction_in_progress = zcfzb_data['construction_in_progress'][index]
        engineer_material = zcfzb_data['engineer_material'][index]
        equipment_turnover.append(utils.cal_equipment_turnover(op_in,fixed,construction_in_progress,engineer_material))
        str_result = str_result + str(equipment_turnover[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          总资产周转率（次）')
    total_assets_turnover = []
    management_capacity['total_assets_turnover'] = total_assets_turnover
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        op_in = lrb_data['op_in'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_assets_turnover.append(utils.cal_total_assets_turnover(op_in,tatol_assets))
        str_result = str_result + str(total_assets_turnover[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print(zhJust(u'获利能力'))
    profitability = {}
    value_table['profitability'] = profitability
    str_result = zhJust(u'          股东权益报酬率RoE ',length = 30)
    return_on_equity = []
    profitability['return_on_equity'] = return_on_equity
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        net_profit_company = lrb_data['net_profit_company'][index]
        total_owners_equity = zcfzb_data['total_shareholder_parent'][index]
        return_on_equity.append(utils.cal_return_on_equity(net_profit_company,total_owners_equity))
        str_result = str_result + str(return_on_equity[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          总资产报酬率RoA ',length = 30)
    return_on_total_assets = []
    profitability['return_on_total_assets'] = return_on_total_assets
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        net_profit_company = lrb_data['net_profit_company'][index]
        total_liability_and_equity = zcfzb_data['total_liability_and_equity'][index]
        return_on_total_assets.append(utils.cal_return_on_total_assets(net_profit_company,total_liability_and_equity))
        str_result = str_result + str(return_on_total_assets[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          营业毛利率1 ',length = 29)
    gross_profit_margin = []
    profitability['gross_profit_margin'] = gross_profit_margin
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        op_in = lrb_data['op_in'][index]
        op_costs = lrb_data['op_costs'][index]
        R_and_D_exp = lrb_data['R_and_D_exp'][index]
        business_tariff_and_annex = lrb_data['business_tariff_and_annex'][index]
        gross_profit_margin.append(utils.cal_gross_profit_margin(op_in,op_costs,R_and_D_exp,business_tariff_and_annex))
        str_result = str_result + str(gross_profit_margin[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          营业利益率2 ',length = 29)
    operating_margin = []
    profitability['operating_margin'] = operating_margin
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        op_profit = lrb_data['op_profit'][index]
        op_in = lrb_data['op_in'][index]
        operating_margin.append(utils.cal_operating_margin(op_profit,op_in))
        str_result = str_result + str(operating_margin[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          经营安全边际率2/1 ',length = 30)
    operating_margin_of_safety = []
    profitability['operating_margin_of_safety'] = operating_margin_of_safety
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        op_profit = lrb_data['op_profit'][index]
        op_in = lrb_data['op_in'][index]
        op_costs = lrb_data['op_costs'][index]
        R_and_D_exp = lrb_data['R_and_D_exp'][index]
        business_tariff_and_annex = lrb_data['business_tariff_and_annex'][index]
        operating_margin_of_safety.append(utils.cal_operating_margin_of_safety(op_in,op_costs,R_and_D_exp,business_tariff_and_annex,op_profit))
        str_result = str_result + str(operating_margin_of_safety[max_count - indexOfSingle - 1]).ljust(15)  
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          净利率 = 纯益率 ',length = 30)
    net_interest_rate = []
    profitability['net_interest_rate'] = net_interest_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        net_profit = lrb_data['net_profit'][index]
        op_in = lrb_data['op_in'][index]
        net_interest_rate.append(utils.cal_net_interest_rate(net_profit,op_in))
        str_result = str_result + str(net_interest_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          每股盈余（元）')
    basic_earning_per_shares = []
    profitability['basic_earning_per_shares'] = basic_earning_per_shares
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        basic_earning_per_share = lrb_data['basic_earning_per_share'][index]
        basic_earning_per_shares.append(basic_earning_per_share)
        str_result = str_result + str(basic_earning_per_share).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          税后净利（百万元）')
    net_profits = []
    profitability['net_profits'] = net_profits
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        net_profit = lrb_data['net_profit'][index]
        net_profit = int(round(float(net_profit) / 100,0))
        net_profits.append(net_profit)
        str_result = str_result + str(net_profit).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print(zhJust(u'现金流量'))
    cash_flow = {}
    value_table['cash_flow'] = cash_flow
    str_result = zhJust(u'          现金流量比率')
    cash_flow_rate = []
    cash_flow['cash_flow_rate'] = cash_flow_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        net_flow_from_op = xjllb_data['net_flow_from_op'][index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        cash_flow_rate.append(utils.cal_cash_flow_rate(net_flow_from_op,total_current_liability))
        str_result = str_result + str(cash_flow_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          现金流量允当比率')
    cash_flow_allowance_rate = []
    cash_flow['cash_flow_allowance_rate'] = cash_flow_allowance_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]

        yyyymmdd = report_dates[index].split('-')
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
        stock_start = zcfzb_data['stock'][index]
        stock_end = 0
        paid_for_distribution_5 = 0
        while count_to_add < 5:
            net_flow_from_op_5 = net_flow_from_op_5 + xjllb_data['net_flow_from_op'][index_next]
            paid_for_longterm_5 = paid_for_longterm_5 + xjllb_data['paid_for_longterm'][index_next]
            net_cash_longterm_5 = net_cash_longterm_5 + xjllb_data['net_cash_longterm'][index_next]
            stock_end = zcfzb_data['stock'][index_next]
            paid_for_distribution_5 = paid_for_distribution_5 + xjllb_data['paid_for_distribution'][index_next]
            count_to_add = count_to_add + 1

            has_done = False
            while 1:
                index_next = index_next + 1
                if not report_dates[index_next]:
                    has_done = True
                    break
                yyyymmdd = report_dates[index_next].split('-')
                if len(yyyymmdd) < 3:
                    has_done = True
                    break
                single_month = int(yyyymmdd[1]) 
                single_day = int(yyyymmdd[2])
                if single_month == 12 and single_day == 31:
                    break
            if has_done:
                break
        cash_flow_allowance_rate.append(utils.cal_cash_flow_allowance_rate(net_flow_from_op_5,paid_for_longterm_5,net_cash_longterm_5,stock_start - stock_end,paid_for_distribution_5))
        str_result = str_result + str(cash_flow_allowance_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          现金再投资比率')
    cash_reinvestment_rate = []
    cash_flow['cash_reinvestment_rate'] = cash_reinvestment_rate
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        net_flow_from_op = xjllb_data['net_flow_from_op'][index]
        paid_for_distribution = xjllb_data['paid_for_distribution'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        cash_reinvestment_rate.append(utils.cal_cash_reinvestment_rate(net_flow_from_op,paid_for_distribution,tatol_assets,total_current_liability))
        str_result = str_result + str(cash_reinvestment_rate[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print('\n')
    str_result = zhJust(u'营业活动现金流量(百万元)        ')
    net_flow_from_ops = []
    value_table['net_flow_from_ops'] = net_flow_from_ops
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        net_flow_from_op = xjllb_data['net_flow_from_op'][index]
        net_flow_from_ops.append(int(round(float(net_flow_from_op) / 100, 0)))
        str_result = str_result + str(net_flow_from_ops[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'投资活动现金流量(百万元)        ')
    net_flows_from_investments = []
    value_table['net_flows_from_investments'] = net_flows_from_investments
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        net_flows_from_investment = xjllb_data['net_flows_from_investment'][index]
        net_flows_from_investments.append(int(round(float(net_flows_from_investment) / 100, 0)))
        str_result = str_result + str(net_flows_from_investments[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'筹资活动现金流量(百万元)        ')
    net_cash_flow_from_finaces = []
    value_table['net_cash_flow_from_finaces'] = net_cash_flow_from_finaces
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        indexOfSingle = index
        index = indexes_for_cal[index]
        net_cash_flow_from_finace = xjllb_data['net_cash_flow_from_finace'][index]
        net_cash_flow_from_finaces.append(int(round(float(net_cash_flow_from_finace) / 100, 0)))
        str_result = str_result + str(net_cash_flow_from_finaces[max_count - indexOfSingle - 1]).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    json_values = json.dumps(value_table)
    fw = open('base_data/value/' + stock_code + '.json', 'w')
    fw.write(json_values)
    fw.close()

def cal_score(stock_code):
    try:
        csvfile = open('base_data/value/' + stock_code + '.json', 'r')
    except Exception as e:
        print(stock_code + ' open wrong')
        print(e)
        return

    value_table = json.load(csvfile)
    tatal_score = 0
    #股东权益报酬率(%) RoE
    tatal_roe = 0
    is_roe_m0 = False
    for roe in value_table['profitability']['return_on_equity']:
        tatal_roe = tatal_roe + roe
    average_roe = tatal_roe / len(value_table['profitability']['return_on_equity'])
    if average_roe >= 35:
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
    elif average_roe >= 0:
        tatal_score = tatal_score + 0
    
    #print(average_roe)

def main():
    #downloadData()
    #print time.strftime("%Y-%m-%d", time.localtime()) 
    # analyseData(stock_code = '600500')
    cal_score(stock_code = '600500')

if __name__ == '__main__':
    main()