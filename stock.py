#coding=utf-8
import tushare as ts
from config import define
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
ts.set_token(define.get_token())
pro = ts.pro_api()
#df = pro.trade_cal(exchange='', start_date='20180901', end_date='20181001', is_open='1')
'''
dfH = pro.stock_basic(is_hs='H',list_status='L',exchange='SSE')
#print(type(dfH))
foH = open("Hshares.txt", "w")
foH.write('       ts_code  symbol  name area industry market list_date\n')
for index,row in dfH.iterrows():
   ts_code_h = row['ts_code']
   symbol_h = row['symbol']
   name_h = row['name']
   area_h = row['area']
   industry_h = row['industry']
   market_h = row['market']
   list_date_h = row['list_date']
   foH.write((str(index)+'   '+ts_code_h+'  '+symbol_h+'   '+name_h+' '+ area_h+' '+industry_h+' '+market_h+'   '+list_date_h).encode('utf-8').strip())
   foH.write('\n')
foH.close()

dfS = pro.stock_basic(is_hs='S',list_status='L',exchange='SZSE')
foS = open("Sshares.txt", "w")
foS.write('       ts_code  symbol  name area industry market list_date\n')
for index,row in dfS.iterrows():
   ts_code_s = row['ts_code']
   symbol_s = row['symbol']
   name_s = row['name']
   area_s = row['area']
   industry_s = row['industry']
   market_s = row['market']
   list_date_s = row['list_date']
   foS.write((str(index)+'   '+ts_code_s+'  '+symbol_s+'   '+name_s+' '+ area_s+' '+industry_s+' '+market_s+'   '+list_date_s).encode('utf-8').strip())
   foS.write('\n')
foS.close()
'''
'''
df = pro.hs_const(hs_type='SH') 
for index,row in df.iterrows():
   print((str(index)+'   '+row['ts_code']+'  '+str(row['in_date'])+'   '+str(row['out_date'])+' '+str(row['is_new'])).encode('utf-8').strip())
'''
'''
df = pro.stock_company(exchange='SZSE') 
num = 1
for index,row in df.iterrows():
   #控制台输出为GBK
   print((str(index)+str(row['ts_code'])+str(row['chairman'])+str(row['secretary'])+str(row['email'])).decode('utf-8').encode('GBK'))
   # print(row)
   # print(row['email'])
   # print('\n')
   num = num + 1
   if num > 2:
      break
'''
'''
df = pro.daily(ts_code='000333.SZ', start_date='20190701', end_date='20191128')
df.head(10)
print(df)
'''
# for index,row in df.iterrows():
#    print(row)

#df = pro.cashflow(ts_code='000333.SH', start_date='20141101', end_date='20181129',ann_date='20181129',period='20181231',report_type='1',comp_type='1')
#print(df)
df = pro.dividend(ts_code='600500.SH')
for index,row in df.iterrows():
   print((str(index)+'   '+row['ts_code']+'  '+str(row['ex_date'])+' '+str(row['cash_div'])).encode('utf-8').strip())
print('done')
