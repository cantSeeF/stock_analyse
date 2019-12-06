#coding=utf-8

#资产负债比率(占总资产%)
def cal_cash_rate(money_funds,transactional_finacial_asset,derivative_finacial_asset,tatol_assets):
   #现金与约当现金占比，货币资金(万元)+交易性金融资产(万元)+衍生金融资产(万元) / 总资产
   return round((float(money_funds) + transactional_finacial_asset + derivative_finacial_asset) / tatol_assets * 100,1)

def cal_accounts_receivable_rate(accounts_receivable,tatol_assets):
   #应收账款比率
   return round(float(accounts_receivable) / tatol_assets * 100,1)

def cal_stock_rate(stock,tatol_assets):
   #存货比率
   return round(float(stock) / tatol_assets * 100,1)

def cal_total_current_assets_rate(total_current_assets,tatol_assets):
   #流动资产比率
   return round(float(total_current_assets) / tatol_assets * 100,1)

def cal_accounts_payable_rate(accounts_payable,tatol_assets):
   #应付账款比率
   return round(float(accounts_payable) / tatol_assets * 100,1)

def cal_total_current_liability_rate(total_current_liability,tatol_assets):
   #流动负债比率
   return round(float(total_current_liability) / tatol_assets * 100,1)

def cal_total_noncurrent_liability_rate(total_noncurrent_liability,tatol_assets):
   #长期负债比率
   return round(float(total_noncurrent_liability) / tatol_assets * 100,1)

def cal_total_owners_equity_rate(total_owners_equity,tatol_assets):
   #股东权益比率
   return round(float(total_owners_equity) / tatol_assets * 100,1)


def cal_total_liability_rate(total_liability,tatol_assets):
   #负债占资产比率
   return round(float(total_liability) / tatol_assets * 100,1)

def cal_Longterm_funds_rate(total_owners_equity,total_noncurrent_liability,fixed,construction_in_progress,engineer_material):
   #长期资金占不动产/厂房及设备比率 （所有者权益+非流动负债合计）/（固定资产+在建工程+工程物资）
   return round((float(total_owners_equity) + total_noncurrent_liability) / (fixed + construction_in_progress + engineer_material) * 100,1)

def cal_current_rate(total_current_assets,total_current_liability):
   #流动比率
   return round(float(total_current_assets) / total_current_liability * 100,1)

def cal_quick_rate(total_current_assets,stock,total_current_liability):
   #速动比率
   return round((float(total_current_assets) - stock) / total_current_liability * 100,1)

def cal_receivable_turnover_rate(op_in,accounts_receivable):
   #应收账款周转率(次)
   return round(float(op_in) / accounts_receivable,1)

def cal_average_cash_days(op_in,accounts_receivable):
   #平均收现日数
   receivable_turnover_rate = cal_receivable_turnover_rate(op_in,accounts_receivable)
   return round(360.0 / receivable_turnover_rate,1)

def cal_inventory_turnover(op_costs,stock):
   #存货周转率(次)
   return round(float(op_costs) / stock,1)

def cal_average_sale_days(op_costs,stock):
   #平均销货日数（平均在库天数）
   inventory_turnover = cal_inventory_turnover(op_costs,stock)
   return round(360.0 / inventory_turnover,1)

def cal_equipment_turnover(op_in,fixed,construction_in_progress,engineer_material):
   #不动产/厂房及设备周转率(次)
   return round(float(op_in) / (fixed + construction_in_progress + engineer_material),1)

def cal_total_assets_turnover(op_in,tatol_assets):
   #总资产周转率
   return round(float(op_in) / tatol_assets,1)

def cal_return_on_equity(net_profit_company,total_owners_equity):
   #股东权益报酬率（RoE） = 归属于母公司所有者的净利润 / 归属于母公司所有者的股东权益
   return round(float(net_profit_company) / total_owners_equity * 100,1)

def cal_return_on_total_assets(net_profit_company,total_liability_and_equity):
   #总资产报酬率（RoA） = 归属于母公司所有者的净利润 / 总资产
   return round(float(net_profit_company) / total_liability_and_equity * 100,1)

def cal_gross_profit_margin(op_in,op_costs,R_and_D_exp,business_tariff_and_annex):
   #毛利率 =（营业收入 - 营业成本 - 研发费用 - 营业税金及附加）/ 营业收入
   return round(float(op_in - op_costs - R_and_D_exp - business_tariff_and_annex) / op_in * 100,1)

def cal_operating_margin(op_profit,op_in):
   #营业利润率（营业利益率） = 营业利润 / 营业收入
   return round(float(op_profit) / op_in * 100,1)

def cal_operating_margin_of_safety(op_in,op_costs,R_and_D_exp,business_tariff_and_annex,op_profit):
   #经营安全边际率 = 营业利益率 / 营业毛利率
   gross_profit_margin = cal_gross_profit_margin(op_in,op_costs,R_and_D_exp,business_tariff_and_annex)
   operating_margin = cal_operating_margin(op_profit,op_in)
   return round(float(operating_margin) / gross_profit_margin * 100,1)

def cal_net_interest_rate(net_profit,op_in):
   #净利率(%) = 纯益率 = 净利 / 营业收入
   return round(float(net_profit) / op_in * 100,1)

def cal_cash_flow_rate(subtotal_of_inflows,total_current_liability):
   #现金流量比率 = 经营活动现金流入 / 流动负债
   return round(float(subtotal_of_inflows) / total_current_liability * 100,1)