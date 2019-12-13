#coding=utf-8
import tushare as ts
from config import local
import json
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

#df = pro.trade_cal(exchange='', start_date='20180901', end_date='20181001', is_open='1')



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
# df = pro.dividend(ts_code='600500.SH')
# for index,row in df.iterrows():
#    print((str(index)+'   '+row['ts_code']+'  '+str(row['ex_date'])+' '+str(row['cash_div'])).encode('utf-8').strip())
# print('done')

def getBusinessData(proApi):
   is_he_list = ['N','H','S']
   list_status_list = ['L','P']
   exchange_list = ['SSE','SZSE']

   business_table = []
   for is_he in is_he_list:
      for list_status in list_status_list:
         for exchange in exchange_list:
            print('get ' + exchange + ' ' + is_he + ' ' + list_status)
            df = proApi.stock_basic(is_hs=is_he,list_status=list_status,exchange=exchange)
            #print(type(df))
            for index,row in df.iterrows():
               single_stock = {}
               single_stock['ts_code'] = row['ts_code']
               single_stock['symbol'] = row['symbol']
               single_stock['name'] = row['name']
               single_stock['area'] = row['area'] or 'area'
               single_stock['industry'] = row['industry'] or 'industry'
               single_stock['market'] = row['market']
               single_stock['list_date'] = row['list_date']
               business_table.append(single_stock)

   print('write ...')
   business_json_str = json.dumps(business_table)
   #business_json_str = business_json_str.encode('utf-8').strip()
   fo = open("base_data/business/business.json", "w")
   fo.write(business_json_str)
   fo.close()
   print('done!')

def downTxt(pro):
   dfH = pro.stock_basic(is_hs='N',list_status='P',exchange='SSE')
   #print(type(dfH))
   foH = open("Hshares_n.txt", "w")
   foH.write('       ts_code  symbol  name area industry market list_date\n')
   for index,row in dfH.iterrows():
      ts_code_h = row['ts_code']
      symbol_h = row['symbol']
      name_h = row['name']
      area_h = row['area'] or 'area'
      industry_h = row['industry'] or 'industry'
      market_h = row['market']
      list_date_h = row['list_date']

      foH.write((str(index)+'   '+ts_code_h+'  '+symbol_h+'   '+name_h+' '+ area_h+' '+industry_h+' '+market_h+'   '+list_date_h).encode('utf-8').strip())
      foH.write('\n')
   foH.close()

   # dfS = pro.stock_basic(is_hs='S',list_status='L',exchange='SZSE')
   # foS = open("Sshares_s.txt", "w")
   # foS.write('       ts_code  symbol  name area industry market list_date\n')
   # for index,row in dfS.iterrows():
   #    ts_code_s = row['ts_code']
   #    symbol_s = row['symbol']
   #    name_s = row['name']
   #    area_s = row['area'] or 'area'
   #    industry_s = row['industry'] or 'industry'
   #    market_s = row['market']
   #    list_date_s = row['list_date']
   #    foS.write((str(index)+'   '+ts_code_s+'  '+symbol_s+'   '+name_s+' '+ area_s+' '+industry_s+' '+market_s+'   '+list_date_s).encode('utf-8').strip())
   #    foS.write('\n')
   # foS.close()
def main():
   ts.set_token(local.get_token())
   pro = ts.pro_api()
   getBusinessData(pro)
   #downTxt(pro)
if __name__ == '__main__':
    main()
