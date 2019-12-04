#coding=utf-8
import re
import urllib2 as web
import csv
import json
import re
from bs4 import BeautifulSoup
from time import sleep
#lrb，zcfzb，xjllb,zycwzb 利润，资产负债，现金流量，主要财务指标

start_stock = 600500
end_stock = 600502
table_names = ['lrb','zcfzb','xjllb']
def downloadData():
    #判断是否有更新，存在，再下载
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
                    sleep(1)
                    break
                except Exception as e:
                    if str(e) =='HTTP Error 404: Not Found':
                        break
                    else:
                        print(e)
                        continue

name_dict = {}
# exp = expense
# op = operating
# in = income
lrb_name_dict = {
    u'报告日期':'report_date',
    u'营业总收入':'total_op_in',
    u'营业收入':'op_in',
    u'利息收入':'interest_in',
    u'已赚保费':'eared_premiun',
    u'手续费及佣金收入':'fee_and_commission_in',
    u'房地产销售收入':'estale_sales_in',
    u'其他业务收入':'other_op_in',
    u'营业总成本':'total_op_costs',
    u'营业成本':'op_costs',
    u'利息支出':'interest_exp',
    u'手续费及佣金支出':'fee_and_comission_exp',
    u'房地产销售成本':'cost_of_estate_sales',
    u'研发费用':'R_and_D_exp',
    u'退保金':'surrender',
    u'赔付支出净额':'net_payouts',
    u'提取保险合同准备金净额':'net_tqbx',
    u'保单红利支出':'bond_insurance_exp',
    u'分保费用':'ARE',
    u'其他业务成本':'other_op_cost',
    u'营业税金及附加':'business_tariff_and_annex',
    u'销售费用':'selling_exp',
    u'管理费用':'admin_exp',
    u'财务费用':'finacial_exp',
    u'资产减值损失':'assets_impairment_loss',
    u'公允价值变动收益':'gyjzbdsy',
    u'投资收益':'investment_in',
    u'对联营企业和合营企业的投资收益':'income_in_ventures',
    u'汇兑收益':'exchange_in',
    u'期货损益':'futures_profit_loss',
    u'托管收益':'custody_in',
    u'补贴收入':'subsidy_in',
    u'其他业务利润':'other_business_profit',
    u'营业利润':'op_profit',
    u'营业外收入':'non-op_in',
    u'营业外支出':'op_exp',
    u'非流动资产处置损失':'non-current_loss',
    u'利润总额':'total_profit',
    u'所得税费用':'in_tax_expense',
    u'未确认投资损失':'unrecongnized_loss',
    u'净利润':'net_profile',
    u'归属于母公司所有者的净利润':'net_profile_company',
    u'被合并方在合并前实现净利润':'net_profile_combined',
    u'少数股东损益':'minority_profit_loss',
    u'基本每股收益':'basic_earning_per_share',
    u'稀释每股收益':'diluted_earning_per_share'
}
zcfzb_name_dict = {
    u'报告日期':'report_date',
    u'货币资金':'money_funds',
    u'结算备付金':'settlement_provision',
    u'拆出资金':'disburse_funds',
    u'交易性金融资产':'transactional_finacial_asset',
    u'衍生金融资产':'derivative_finacial_asset',
    u'应收票据':'bill_receivable',
    u'应收账款':'accounts_receivable',
    u'预付款项':'prepayments',
    u'应收保费':'premium_receivable',
    u'应收分保账款':'reinsurance_receivable',
    u'应收分保合同准备金':'receivables_for_insure_contrat',
    u'应收利息':'interest_receivable',
    u'应收股利':'dividends_receivable',
    u'其他应收款':'other_receivalbe',
    u'应收出口退税':'export_tax_receivable',
    u'应收补贴款':'subsidy_receivable',
    u'应收保证金':'margin_receivable',
    u'内部应收款':'internal_receivable',
    u'买入返售金融资产':'buy-back_asset',
    u'存货':'stock',
    u'待摊费用':'prepaid_expenses',
    u'待处理流动资产损益':'pending_assets',
    u'一年内到期的非流动资产':'within_one_non-current',
    u'其他流动资产':'other_current_assets',
    u'流动资产合计':'total_current_assets',
    u'发放贷款及垫款':'loads_and_advances',
    u'可供出售金融资产':'available_for_sale_finacial_assets',
    u'持有至到期投资':'hold_to_maturity_investment',
    u'长期应收款':'long-term_receivable',
    u'长期股权投资':'long-term_equity_investment',
    u'其他长期投资':'other_long-term_investment',
    u'投资性房地产':'investment_real_estate',
    u'固定资产原值':'original_value_of_fixed',
    u'累计折旧':'accumulated_depreciation',
    u'固定资产净值':'net_value_of_fixed',
    u'固定资产减值准备':'provision_for_gdzcjz',
    u'固定资产':'fixed',
    u'在建工程':'construction_in_progress',
    u'工程物资':'engineer_material',
    u'固定资产清理':'liquidation_of_fix',
    u'生产性生物资产':'productive_biological_assets',
    u'公益性生物资产':'non-profit_biological_assets',
    u'油气资产':'oil-gass_assets',
    u'无形资产':'intangible_assets',
    u'开发支出':'development_exp',
    u'商誉':'goodwill',
    u'长期待摊费用':'long-tern_prepaid_exp',
    u'股权分置流通权':'right_to_trade',
    u'递延所得税资产':'deferred_tax_assets',
    u'其他非流动资产':'other_non-current_assets',
    u'非流动资产合计':'tatol_non-current_assets',
    u'资产总计':'tatol_assets',
    u'短期借款':'short-tern_loan',
    u'向中央银行借款':'borrowing_from_central_bank',
    u'吸收存款及同业存放':'deposits',
    u'拆入资金':'funding',
    u'交易性金融负债':'transactional_finacial_liabilites',
    u'衍生金融负债':'derivative_financial_liabilities',
    u'应付票据':'notes_payable',
    u'应付账款':'accounts_payable',
    u'预收账款':'advance_payment',
    u'卖出回购金融资产款':'sale_of_repurchase',
    u'应付手续费及佣金':'fees_and_commissions',
    u'应付职工薪酬':'payable_employees',
    u'应交税费':'taxes_payable',
}


xjllb_name_dict = {
    u'报告日期':'taxes_payable',
    u'销售商品、提供劳务收到的现金':'taxes_payable',
    u'客户存款和同业存放款项净增加额':'taxes_payable',
    u'向中央银行借款净增加额':'taxes_payable',
    u'向其他金融机构拆入资金净增加额':'taxes_payable',
    u'收到原保险合同保费取得的现金':'taxes_payable',
    u'收到再保险业务现金净额':'taxes_payable',
    u'保户储金及投资款净增加额':'taxes_payable',
    u'处置交易性金融资产净增加额':'taxes_payable',
    u'收取利息、手续费及佣金的现金':'taxes_payable',
    u'拆入资金净增加额':'taxes_payable',
    u'回购业务资金净增加额':'taxes_payable',
    u'收到的税费返还':'taxes_payable',
    u'收到的其他与经营活动有关的现金':'taxes_payable',
    u'经营活动现金流入小计':'taxes_payable',
    u'购买商品、接受劳务支付的现金':'taxes_payable',
    u'客户贷款及垫款净增加额':'taxes_payable',
    u'存放中央银行和同业款项净增加额':'taxes_payable',
    u'支付原保险合同赔付款项的现金':'taxes_payable',
    u'支付利息、手续费及佣金的现金':'taxes_payable',
    u'支付保单红利的现金':'taxes_payable',
    u'支付给职工以及为职工支付的现金':'taxes_payable',
    u'支付的各项税费':'taxes_payable',
    u'支付的其他与经营活动有关的现金':'taxes_payable',
    u'经营活动现金流出小计':'taxes_payable',
    u'经营活动产生的现金流量净额':'taxes_payable',
    u'收回投资所收到的现金':'taxes_payable',
    u'取得投资收益所收到的现金':'taxes_payable',
    u'处置固定资产、无形资产和其他长期资产所收回的现金净额':'taxes_payable',
    u'处置子公司及其他营业单位收到的现金净额':'taxes_payable',
    u'收到的其他与投资活动有关的现金':'taxes_payable',
    u'减少质押和定期存款所收到的现金':'taxes_payable',
    u'投资活动现金流入小计':'taxes_payable',
    u'购建固定资产、无形资产和其他长期资产所支付的现金':'taxes_payable',
    u'投资所支付的现金':'taxes_payable',
    u'质押贷款净增加额':'taxes_payable',
    u'取得子公司及其他营业单位支付的现金净额':'taxes_payable',
    u'支付的其他与投资活动有关的现金':'taxes_payable',
    u'增加质押和定期存款所支付的现金':'taxes_payable',
    u'投资活动现金流出小计':'taxes_payable',
    u'投资活动产生的现金流量净额':'taxes_payable',
    u'吸收投资收到的现金':'taxes_payable',
    u'其中：子公司吸收少数股东投资收到的现金':'taxes_payable',
    u'取得借款收到的现金':'taxes_payable',
    u'发行债券收到的现金':'taxes_payable',
    u'收到其他与筹资活动有关的现金':'taxes_payable',
    u'筹资活动现金流入小计':'taxes_payable',
    u'偿还债务支付的现金':'taxes_payable',
    u'分配股利、利润或偿付利息所支付的现金':'taxes_payable',
    u'其中：子公司支付给少数股东的股利、利润':'taxes_payable',
    u'支付其他与筹资活动有关的现金':'taxes_payable',
    u'筹资活动现金流出小计':'taxes_payable',
    u'筹资活动产生的现金流量净额':'taxes_payable',
    u'汇率变动对现金及现金等价物的影响':'taxes_payable',
    u'现金及现金等价物净增加额':'taxes_payable',
    u'加:期初现金及现金等价物余额':'taxes_payable',
    u'期末现金及现金等价物余额':'taxes_payable',
    u'净利润':'taxes_payable',
    u'少数股东损益':'taxes_payable',
    u'未确认的投资损失':'taxes_payable',
    u'资产减值准备':'taxes_payable',
    u'固定资产折旧、油气资产折耗、生产性物资折旧':'taxes_payable',
    u'无形资产摊销':'taxes_payable',
    u'长期待摊费用摊销':'taxes_payable',
    u'待摊费用的减少':'taxes_payable',
    u'预提费用的增加':'taxes_payable',
    u'处置固定资产、无形资产和其他长期资产的损失':'taxes_payable',
    u'固定资产报废损失':'taxes_payable',
    u'公允价值变动损失':'taxes_payable',
    u'递延收益增加(减：减少)':'taxes_payable',
    u'预计负债':'taxes_payable',
    u'财务费用':'taxes_payable',
    u'投资损失':'taxes_payable',
    u'递延所得税资产减少':'taxes_payable',
    u'递延所得税负债增加':'taxes_payable',
    u'存货的减少':'taxes_payable',
    u'经营性应收项目的减少':'taxes_payable',
    u'已完工尚未结算款的减少(减:增加)':'taxes_payable',
    u'已结算尚未完工款的增加(减:减少)':'taxes_payable',
    u'其他':'taxes_payable',
    u'经营活动产生现金流量净额':'taxes_payable',
    u'债务转为资本':'taxes_payable',
    u'一年内到期的可转换公司债券':'taxes_payable',
    u'融资租入固定资产':'taxes_payable',
    u'现金的期末余额':'taxes_payable',
    u'现金的期初余额':'taxes_payable',
    u'现金等价物的期末余额':'taxes_payable',
    u'现金等价物的期初余额':'taxes_payable',
    u'现金及现金等价物的净增加额':'taxes_payable',
}
def csvToJson(csvPath,jsonPath):
    csvfile = open('600500lrb.csv', 'r')


def loadData():
    csvfile = open('600500lrb.csv', 'r')
    dictionary = {}
    for row in csvfile:
        #row.decode('utf-8').encode('gb2312')
        row = row.replace('--', '0')
        row = re.sub(u"\\(.*?\\)", "", row)
        array = row.split(',')
        key = lrb_name_dict[array[0].decode('utf-8')]
        del array[0]
        dictionary[key] = array
        #print(key)
    print(len(dictionary))
    json_str = json.dumps(dictionary)
    abc = json.loads(json_str)
    fw = open('600500lrb.json', 'w')
    fw.write(json_str)
    fw.close()

    for key in lrb_name_dict:
        print(key)
        print(abc[lrb_name_dict[key]])
    
def main():
    downloadData()
    #loadData()

if __name__ == '__main__':
    main()