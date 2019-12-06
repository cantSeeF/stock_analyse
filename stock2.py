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

FONT_COLOR = 31
def getFontColor():
    global FONT_COLOR
    if FONT_COLOR == 36:
        FONT_COLOR = 31
    else:
        FONT_COLOR = FONT_COLOR + 1
    return FONT_COLOR

def analyseData(lrb_data,xjllb_data,zcfzb_data):
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

    #print(indexes_for_cal)
    str_result = zhJust(u'资产负债比率（占总资产%：）    ') + showYear(cur_year)
    print("\033[0;37;42m{0}\033[0m".format(str_result))
    
    str_result = zhJust(u'     现金与约当现金')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        money_funds = zcfzb_data['money_funds'][index]
        transactional_finacial_asset = zcfzb_data['transactional_finacial_asset'][index]
        derivative_finacial_asset = zcfzb_data['derivative_finacial_asset'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_result = str_result + str(utils.cal_cash_rate(money_funds,transactional_finacial_asset,derivative_finacial_asset,tatol_assets)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     应收账款')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        accounts_receivable = zcfzb_data['accounts_receivable'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_result = str_result + str(utils.cal_accounts_receivable_rate(accounts_receivable,tatol_assets)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     存货')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        stock = zcfzb_data['stock'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_result = str_result + str(utils.cal_stock_rate(stock,tatol_assets)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))
    
    str_result = zhJust(u'     流动资产')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        total_current_assets = zcfzb_data['total_current_assets'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_result = str_result + str(utils.cal_total_current_assets_rate(total_current_assets,tatol_assets)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))
    
    str_result = zhJust(u'     总资产')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        str_result = str_result + '100'.ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     应付账款')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        accounts_payable = zcfzb_data['accounts_payable'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_result = str_result + str(utils.cal_accounts_payable_rate(accounts_payable,tatol_assets)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     流动负债')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_result = str_result + str(utils.cal_total_current_liability_rate(total_current_liability,tatol_assets)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     长期负债')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        total_noncurrent_liability = zcfzb_data['total_noncurrent_liability'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_result = str_result + str(utils.cal_total_noncurrent_liability_rate(total_noncurrent_liability,tatol_assets)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     股东权益')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        total_owners_equity = zcfzb_data['total_owners_equity'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_result = str_result + str(utils.cal_total_owners_equity_rate(total_owners_equity,tatol_assets)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'     总负债加股东权益')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        str_result = str_result + '100'.ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print('\n')
    str_result = zhJust(u'类别      财务比例    ') + showYear(cur_year)
    print("\033[0;37;42m{0}\033[0m".format(str_result))

    print(zhJust(u'财务结构'))

    str_result = zhJust(u'          负债占资产比率')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        total_liability = zcfzb_data['total_liability'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_result = str_result + str(utils.cal_total_liability_rate(total_liability,tatol_assets)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          长期资金占不动产/厂房及设备比率')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        total_owners_equity = zcfzb_data['total_owners_equity'][index]
        total_noncurrent_liability = zcfzb_data['total_noncurrent_liability'][index]
        fixed = zcfzb_data['fixed'][index]
        construction_in_progress = zcfzb_data['construction_in_progress'][index]
        engineer_material = zcfzb_data['engineer_material'][index]
        str_result = str_result + str(utils.cal_Longterm_funds_rate(total_owners_equity,total_noncurrent_liability,fixed,construction_in_progress,engineer_material)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print(zhJust(u'偿债能力'))
    str_result = zhJust(u'          流动比率')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        total_current_assets = zcfzb_data['total_current_assets'][index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        str_result = str_result + str(utils.cal_current_rate(total_current_assets,total_current_liability)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          速动比率')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        total_current_assets = zcfzb_data['total_current_assets'][index]
        stock = zcfzb_data['stock'][index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        str_result = str_result + str(utils.cal_quick_rate(total_current_assets,stock,total_current_liability)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print(zhJust(u'经营能力'))
    str_result = zhJust(u'          应收账款周转率（次）')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        op_in = lrb_data['op_in'][index]
        accounts_receivable = zcfzb_data['accounts_receivable'][index]
        str_result = str_result + str(utils.cal_receivable_turnover_rate(op_in,accounts_receivable)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          平均收现日数')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        op_in = lrb_data['op_in'][index]
        accounts_receivable = zcfzb_data['accounts_receivable'][index]
        str_result = str_result + str(utils.cal_average_cash_days(op_in,accounts_receivable)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          存货周转率（次）')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        op_costs = lrb_data['op_costs'][index]
        stock = zcfzb_data['stock'][index]
        str_result = str_result + str(utils.cal_inventory_turnover(op_costs,stock)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          平均销货日数（平均在库天数）')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        op_costs = lrb_data['op_costs'][index]
        stock = zcfzb_data['stock'][index]
        str_result = str_result + str(utils.cal_average_sale_days(op_costs,stock)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          不动产及厂房及设备周转率（次）')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        op_in = lrb_data['op_in'][index]
        fixed = zcfzb_data['fixed'][index]
        construction_in_progress = zcfzb_data['construction_in_progress'][index]
        engineer_material = zcfzb_data['engineer_material'][index]
        str_result = str_result + str(utils.cal_equipment_turnover(op_in,fixed,construction_in_progress,engineer_material)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          总资产周转率（次）')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        op_in = lrb_data['op_in'][index]
        tatol_assets = zcfzb_data['tatol_assets'][index]
        str_result = str_result + str(utils.cal_total_assets_turnover(op_in,tatol_assets)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print(zhJust(u'获利能力'))
    str_result = zhJust(u'          股东权益报酬率RoE ',length = 30)
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        net_profit_company = lrb_data['net_profit_company'][index]
        total_owners_equity = zcfzb_data['total_shareholder_parent'][index]
        str_result = str_result + str(utils.cal_return_on_equity(net_profit_company,total_owners_equity)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          总资产报酬率RoA ',length = 30)
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        net_profit_company = lrb_data['net_profit_company'][index]
        total_liability_and_equity = zcfzb_data['total_liability_and_equity'][index]
        str_result = str_result + str(utils.cal_return_on_total_assets(net_profit_company,total_liability_and_equity)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          营业毛利率1 ',length = 29)
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        op_in = lrb_data['op_in'][index]
        op_costs = lrb_data['op_costs'][index]
        R_and_D_exp = lrb_data['R_and_D_exp'][index]
        business_tariff_and_annex = lrb_data['business_tariff_and_annex'][index]
        str_result = str_result + str(utils.cal_gross_profit_margin(op_in,op_costs,R_and_D_exp,business_tariff_and_annex)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          营业利益率2 ',length = 29)
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        op_profit = lrb_data['op_profit'][index]
        op_in = lrb_data['op_in'][index]
        str_result = str_result + str(utils.cal_operating_margin(op_profit,op_in)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          经营安全边际率2/1 ',length = 30)
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        op_profit = lrb_data['op_profit'][index]
        op_in = lrb_data['op_in'][index]
        op_costs = lrb_data['op_costs'][index]
        R_and_D_exp = lrb_data['R_and_D_exp'][index]
        business_tariff_and_annex = lrb_data['business_tariff_and_annex'][index]
        str_result = str_result + str(utils.cal_operating_margin_of_safety(op_in,op_costs,R_and_D_exp,business_tariff_and_annex,op_profit)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          净利率 = 纯益率 ',length = 30)
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        net_profit = lrb_data['net_profit'][index]
        op_in = lrb_data['op_in'][index]
        str_result = str_result + str(utils.cal_net_interest_rate(net_profit,op_in)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          每股盈余（元）')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        basic_earning_per_share = lrb_data['basic_earning_per_share'][index]
        str_result = str_result + str(basic_earning_per_share).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    str_result = zhJust(u'          税后净利（百万元）')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        net_profit = lrb_data['net_profit'][index]
        net_profit = int(round(float(net_profit) / 100,0))
        str_result = str_result + str(net_profit).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

    print(zhJust(u'现金流量'))
    str_result = zhJust(u'          现金流量比率')
    for index in range(len(indexes_for_cal) - 1,-1,-1):#需要倒序
        index = indexes_for_cal[index]
        subtotal_of_inflows = xjllb_data['subtotal_of_inflows'][index]
        total_current_liability = zcfzb_data['total_current_liability'][index]
        str_result = str_result + str(utils.cal_cash_flow_rate(subtotal_of_inflows,total_current_liability)).ljust(15)
    print("\033[0;{0};40m{1}\033[0m".format(getFontColor(),str_result))

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