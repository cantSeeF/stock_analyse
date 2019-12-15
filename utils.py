#coding=utf-8

#资产负债比率(占总资产%)
def cal_cash_rate(money_funds,settlement_provision,disburse_funds,transactional_finacial_asset,derivative_finacial_asset,tatol_assets):
   #现金与约当现金占比，货币资金(万元)+交易性金融资产(万元)+衍生金融资产(万元) / 总资产
   if tatol_assets == 0:
      return 0
   return round((float(money_funds) + settlement_provision + transactional_finacial_asset + disburse_funds + derivative_finacial_asset) / tatol_assets * 100,1)

def cal_accounts_receivable_rate(accounts_receivable,tatol_assets):
   #应收账款比率
   if tatol_assets == 0:
      return 0
   return round(float(accounts_receivable) / tatol_assets * 100,1)

def cal_stock_rate(stock,tatol_assets):
   #存货比率
   if tatol_assets == 0:
      return 0
   return round(float(stock) / tatol_assets * 100,1)

def cal_total_current_assets_rate(total_current_assets,tatol_assets):
   #流动资产比率
   if tatol_assets == 0:
      return 0
   return round(float(total_current_assets) / tatol_assets * 100,1)

def cal_accounts_payable_rate(accounts_payable,tatol_assets):
   #应付账款比率
   if tatol_assets == 0:
      return 0
   return round(float(accounts_payable) / tatol_assets * 100,1)

def cal_total_current_liability_rate(total_current_liability,tatol_assets):
   #流动负债比率
   if tatol_assets == 0:
      return 0
   return round(float(total_current_liability) / tatol_assets * 100,1)

def cal_total_noncurrent_liability_rate(total_noncurrent_liability,tatol_assets):
   #长期负债比率
   if tatol_assets == 0:
      return 0
   return round(float(total_noncurrent_liability) / tatol_assets * 100,1)

def cal_total_owners_equity_rate(total_owners_equity,tatol_assets):
   #股东权益比率
   if tatol_assets == 0:
      return 0
   return round(float(total_owners_equity) / tatol_assets * 100,1)


def cal_total_liability_rate(total_liability,tatol_assets):
   #负债占资产比率
   if tatol_assets == 0:
      return 0
   return round(float(total_liability) / tatol_assets * 100,1)

def cal_longterm_funds_rate(total_owners_equity,total_noncurrent_liability,fixed,construction_in_progress,engineer_material):
   #长期资金占不动产/厂房及设备比率 （所有者权益+非流动负债合计）/（固定资产+在建工程+工程物资）
   all_plant = fixed + construction_in_progress + engineer_material
   if all_plant == 0:
      return 0
   return round((float(total_owners_equity) + total_noncurrent_liability) / all_plant * 100,1)

def cal_current_rate(total_current_assets,total_current_liability):
   #流动比率
   if total_current_liability == 0:
      return 0
   return round(float(total_current_assets) / total_current_liability * 100,1)

def cal_quick_rate(total_current_assets,stock,prepayments,total_current_liability):
   #速动比率 = 流动资产 - 存货 - 预付款项 / 流动负债
   if total_current_liability == 0:
      return 0
   return round((float(total_current_assets) - stock - prepayments) / total_current_liability * 100,1)

def cal_receivable_turnover_rate(total_op_in,accounts_receivable):
   #应收账款周转率(次)
   if accounts_receivable == 0:
      return 0.0
   return round(float(total_op_in) / accounts_receivable,1)

def cal_average_cash_days(total_op_in,accounts_receivable):
   #平均收现日数
   receivable_turnover_rate = cal_receivable_turnover_rate(total_op_in,accounts_receivable)
   if receivable_turnover_rate == 0:
      return 0.0
   average_cash_days = round(360.0 / receivable_turnover_rate,1)
   if average_cash_days == 0:
      return 0.1
   return average_cash_days

def cal_inventory_turnover(op_costs,stock):
   #存货周转率(次)
   if stock == 0:
      return 0
   return round(float(op_costs) / stock,1)

def cal_average_sale_days(op_costs,stock):
   #平均销货日数（平均在库天数）
   inventory_turnover = cal_inventory_turnover(op_costs,stock)
   if inventory_turnover == 0:
      return 0
   return round(360.0 / inventory_turnover,1)

def cal_equipment_turnover(total_op_in,fixed,construction_in_progress,engineer_material):
   #不动产/厂房及设备周转率(次)
   plant = fixed + construction_in_progress + engineer_material
   if plant == 0:
      return 0
   return round(float(total_op_in) / plant,1)

def cal_total_assets_turnover(total_op_in,tatol_assets):
   #总资产周转率
   if tatol_assets == 0:
      return 0
   return round(float(total_op_in) / tatol_assets,1)

def cal_return_on_equity(net_profit_company,total_owners_equity):
   #股东权益报酬率（RoE） = 归属于母公司所有者的净利润 / 归属于母公司所有者的股东权益
   return round(float(net_profit_company) / total_owners_equity * 100,1)

def cal_return_on_total_assets(net_profit_company,total_liability_and_equity):
   #总资产报酬率（RoA） = 归属于母公司所有者的净利润 / 总资产
   if total_liability_and_equity == 0:
      return 0
   return round(float(net_profit_company) / total_liability_and_equity * 100,1)

def cal_gross_profit_margin(all_op_in,all_cost):
   #毛利率 =（营业收入 - 营业成本 - 研发费用 - 营业税金及附加）/ 营业收入
   if all_cost == 0:
      return 0
   return round(float(all_op_in - all_cost) / all_op_in * 100,1)

def cal_operating_margin(op_profit,total_op_in):
   #营业利润率（营业利益率） = 营业利润 / 营业收入
   if total_op_in == 0:
      return 0
   return round(float(op_profit) / total_op_in * 100,1)

def cal_operating_margin_of_safety(all_op_in,all_cost,op_profit,total_op_in):
   #经营安全边际率 = 营业利益率 / 营业毛利率
   gross_profit_margin = cal_gross_profit_margin(all_op_in,all_cost)
   operating_margin = cal_operating_margin(op_profit,total_op_in)
   if gross_profit_margin == 0:
      return 0
   return round(float(operating_margin) / gross_profit_margin * 100,1)

def cal_net_interest_rate(net_profit,total_op_in):
   #净利率(%) = 纯益率 = 净利 / 营业收入
   if total_op_in == 0:
      return 0
   return round(float(net_profit) / total_op_in * 100,1)

def cal_cash_flow_rate(net_flow_from_op,total_current_liability):
   #现金流量比率 = 经营活动产生现金流量净额 / 流动负债
   if total_current_liability == 0:
      return 0
   return round(float(net_flow_from_op) / total_current_liability * 100,1)

def cal_cash_flow_allowance_rate(net_flow_from_op_5,paid_for_longterm_5,net_cash_longterm_5,stock_5,paid_for_distribution_5):
   #现金流量允当比率 = 最近5年 经营活动产生现金流量净额 / 最近5年（资本支出 + 存货增加额 + 现金股利）
   #分母有三部分组成：5年内资本支出的总额、5年存货余额、5年分配利润的总额
   #5年资本支出总净额=∑（2012-2016）购建固定资产、无形资产和其他长期资产支付的现金-处置固定资产、无形资产和其他长期资产收回的现金净额
   #5年存货余额=2016年存货金额-2012年存货金额
   #5年分配利润总额=∑（2012-2016）分配股利、利润或偿还利息支付的现金
   divisor = paid_for_longterm_5 - net_cash_longterm_5 + stock_5 + paid_for_distribution_5
   if divisor == 0:
      return 0
   return round(float(net_flow_from_op_5) / divisor * 100,1)

def cal_cash_reinvestment_rate(net_flow_from_op,paid_for_distribution,tatol_assets,total_current_liability):
   if tatol_assets - total_current_liability == 0:
      return 0
   #现金再投资比率 = 经营活动产生现金流量净额 - 现金股利 / 固定资产毛额 + 长期投资 + 其他资产 + 营运资金 = （经营活动产生现金流量净额 - 分配股利、利润或偿付利息所支付的现金） / （总资产 - 流动负债）
   return round(float(net_flow_from_op - paid_for_distribution) / (tatol_assets - total_current_liability) * 100,1)