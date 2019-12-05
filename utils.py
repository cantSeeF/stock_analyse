#coding=utf-8

#资产负债比率(占总资产%)
def cal_cash_rate(money_funds,transactional_finacial_asset,derivative_finacial_asset,tatol_assets):
   #现金与约当现金占比，货币资金(万元)+交易性金融资产(万元)+衍生金融资产(万元) / 总资产
   return (money_funds + transactional_finacial_asset + derivative_finacial_asset) / tatol_assets * 100
def cal_accounts_receivable_rate(accounts_receivable,tatol_assets):
   #应收账款比率
   return accounts_receivable / tatol_assets
