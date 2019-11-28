#coding=utf-8
import tushare as ts
import define
ts.set_token(define.get_token())
pro = ts.pro_api()
#df = pro.trade_cal(exchange='', start_date='20180901', end_date='20181001', is_open='1')
dfH = pro.stock_basic(is_hs='H',list_status='L',exchange='SSE')
#print(type(dfH))
foH = open("Hshares.txt", "w")
foH.write('       ts_code  symbol  name area industry market list_date\n')
for index,row in dfH.iterrows():
   foH.write((str(index) + '   ' + row['ts_code'] + '  ' + row['symbol'] + '   ' + row['name'] + ' ' + row['area'] + ' ' + row['industry'] + ' ' + row['market'] + '   ' + row['list_date']).encode('utf-8').strip())
   foH.write('\n')
foH.close()

dfS = pro.stock_basic(is_hs='S',list_status='L',exchange='SZSE')
foS = open("Sshares.txt", "w")
foS.write('       ts_code  symbol  name area industry market list_date\n')
for index,row in dfS.iterrows():
   foS.write((str(index) + '   ' + row['ts_code'] + '  ' + row['symbol'] + '   ' + row['name'] + ' ' + row['area'] + ' ' + row['industry'] + ' ' + row['market'] + '   ' + row['list_date']).encode('utf-8').strip())
   foS.write('\n')
foS.close()

print('done')
