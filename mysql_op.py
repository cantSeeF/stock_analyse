#!/usr/bin/env python
# coding=utf-8

import MySQLdb

#企业价值分析表需要数据
#现金与约当现金比率 = ( 货币资金 + 约当现金 ) / 总资产    货币资金(万元)+交易性金融资产(万元)+衍生金融资产(万元) / 总资产

#应收账款比率
#存货比率

#分红数据，从tushare获取，每10股分红=每股分红*10 ，日期=除权除息日

#长期资金占不动产、厂房及设备比率 =  (长期负债 + 股东权益) / 不动产、厂房及设备 = （所有者权益+非流动负债合计）/（固定资产+在建工程+工程物资）

#毛利 =（营业收入 - 营业成本 - 研发费用 - 营业税金及附加）
#营业利润率（营业利益率） = 营业利润 / 营业收入

#现金流量允当比率 https://www.jianshu.com/p/c98dcef4f159
#现金再投资比率 https://www.jianshu.com/p/3007d9b49113


#利润表
lrb_dict = {}

#资产负债表
fzb_dict = {}

#现金流表
llb_dict = {}

def connectdb():
    print('连接到mysql服务器...')
    # 打开数据库连接
    # 
    #db = MySQLdb.connect("localhost","root","123456","stock_analyse")
    db = MySQLdb.connect(host="localhost",user="root",passwd="123456",db="stock_analyse")
    # cursor = db.cursor()
    # cursor.execute('show databases;')
    # results = cursor.fetchall()
    # print(results)
    # for row in results:
    #     print(row)
    print('连接上了!')
    return db

def createtable(db):
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()

    # 如果存在表Sutdent先删除
    #cursor.execute("DROP TABLE IF EXISTS Student")
    sql = 'CREATE TABLE IF NOT EXISTS "Student" (\
            ID CHAR(10) NOT NULL,\
            Name CHAR(8),\
            Grade INT )'

    # 创建Sutdent表
    cursor.execute(sql)

def insertdb(db):
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()

    # SQL 插入语句
    sql = """INSERT INTO Student
         VALUES ('001', 'CZQ', 70),
                ('002', 'LHQ', 80),
                ('003', 'MQ', 90),
                ('004', 'WH', 80),
                ('005', 'HP', 70),
                ('006', 'YF', 66),
                ('007', 'TEST', 100)"""

    #sql = "INSERT INTO Student(ID, Name, Grade) \
    #    VALUES ('%s', '%s', '%d')" % \
    #    ('001', 'HP', 60)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # Rollback in case there is any error
        print '插入数据失败!'
        db.rollback()

def querydb(db):
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()

    # SQL 查询语句
    #sql = "SELECT * FROM Student \
    #    WHERE Grade > '%d'" % (80)
    sql = "SELECT * FROM Student"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            ID = row[0]
            Name = row[1]
            Grade = row[2]
            # 打印结果
            print "ID: %s, Name: %s, Grade: %d" % \
                (ID, Name, Grade)
    except:
        print "Error: unable to fecth data"

def deletedb(db):
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()

    # SQL 删除语句
    sql = "DELETE FROM Student WHERE Grade = '%d'" % (100)

    try:
       # 执行SQL语句
       cursor.execute(sql)
       # 提交修改
       db.commit()
    except:
        print '删除数据失败!'
        # 发生错误时回滚
        db.rollback()

def updatedb(db):
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()

    # SQL 更新语句
    sql = "UPDATE Student SET Grade = Grade + 3 WHERE ID = '%s'" % ('003')

    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        print '更新数据失败!'
        # 发生错误时回滚
        db.rollback()

def closedb(db):
    db.close()

def main():
   db = connectdb()    # 连接MySQL数据库
   #  createtable(db)     # 创建表
   #  insertdb(db)        # 插入数据
   #  print '\n插入数据后:'
   #  querydb(db) 
   #  deletedb(db)        # 删除数据
   #  print '\n删除数据后:'
   #  querydb(db)
   #  updatedb(db)        # 更新数据
   #  print '\n更新数据后:'
   #  querydb(db)

   closedb(db)         # 关闭数据库

if __name__ == '__main__':
    main()