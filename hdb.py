# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 11:00:40 2021

@author: keybd
"""
import sqlite3
import csv
from datetime import datetime
from datetime import date

FORMAT_DATE = '%Y-%m-%d'

def connect_db(db_name):
    conn = sqlite3.connect(db_name)
    return conn


def get_stock_data_from_db(conn, code, s_datetime=None, e_datetime=None):
    c = conn.cursor()
    
    
    if s_datetime != None and e_datetime != None:
        #for row in c.execute('select * from stocks order by code, sdate'):
        #for row in c.execute('select * from trade_history order by op_time'):
        query = "select sdate, close from stocks where code = '{}' and sdate >= '{}' and sdate <= '{}' order by sdate".format(
                code, s_datetime.strftime(FORMAT_DATE), e_datetime.strftime(FORMAT_DATE))
    else:
        query = "select sdate, close from stocks where code = '{}' order by sdate".format(code)
    #print(query)
    cnt = 0
    full_date = []
    y = []
    for row in c.execute(query):
        full_date.append(row[0])
        y.append(float(row[1]))
        cnt += 1

    if cnt == 0:
        return False, full_date, y
    else:
        return True, full_date, y
   
def insert_stock_data(conn, s_list):
    try:
        c = conn.cursor()
        for s in s_list:
            query = (
                    "insert or replace into stocks(code, sdate, open, high, low, close, volume, change) "
                    + "values('{}', '{}', {:.1f}, {:.1f}, {:.1f}, {:.1f}, {}, 0.0)"
                    ).format(s.get_code(), s.get_date(), s.get_open(), s.get_high(),
                            s.get_low(), s.get_close(), s.get_volume())
            #print(query)
            c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)
#c.execute("insert into stocks(code, sdate, closep) values(068270, '2021-01-12', 123.456)")
#c.execute("insert into stocks(code, sdate, closep) values(068270, '2021-01-13', 123.456)")
#c.execute("insert into stocks(code, sdate, closep) values(068270, '1999-01-13', 123.456)")
#conn.commit()


def log_stock_trading(conn, code, op, price, vol, log_date = None):
    if log_date:
        now = log_date
    else:
        now = datetime.now()
    op_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    print("ACTION: {} code: {}  optime: {} price: {:.1f}".format(op, code, op_time, price))
    query = (
            "insert or ignore into trade_history(code, op_time, operation, volume, price) " + 
            "values('{}','{}','{}',{},{:.2f})"
            ).format(code, op_time, op, str(vol), price);
    try:
        c = conn.cursor()
        #print(query)
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True

def create_trade_history_table(conn):
    query = """CREATE TABLE IF NOT EXISTS trade_history(
                code TEXT NOT NULL,
                op_time DATETIME NOT NULL,
                operation TEXT NOT NULL,
                volume INT NOT NULL,
                price FLOAT NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
    except Error as e:
        print(e)
        return False
    return True

def create_table(conn):
    query = """CREATE TABLE IF NOT EXISTS stocks(
                code text NOT NULL,
                sdate date NOT NULL,
                open FLOAT NOT NULL,
                high FLOAT NOT NULL,
                low FLOAT NOT NULL,
                close FLOAT NOT NULL,
                volume INT NOT NULL,
                change FLOAT NOT NULL,
                PRIMARY KEY (code, sdate)
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
    except Error as e:
        print(e)
        return False
    return True



def get_closed_price(code, dd):
    colname = 'Close'
    df = fdr.DataReader(code, dd, dd)
    print(df.head())
    print("-"*100)
    print(len(df))
    print("-"*100)
    print(float(df[colname][0]))
    print("-"*100)
    print(type(df[colname]))
    print("-"*100)
    if len(df) == 1:
        return float(df[colname])
    else:
        return -1.0

def get_current_price(code):
    now = get_today()
    d = now.strftime(FORMAT_DATE)
    print("Today: " + d)
    return get_closed_price(code, d)


def get_stock_names(conn, code):
    query = "select name_kor, name_eng from stock_basic_info where code = '{}'".format(code)
    c = conn.cursor()
    for row in c.execute(query):
        return row[0], row[1]
    
    return None, None


def get_all_stocks_code(conn, market):
    
    code_list = []
    if market != 'all':
        return code_list
    
    query = "select code from stock_basic_info"
    c = conn.cursor()
    
    for row in c.execute(query):
        code_list.append(row[0])
    
    return code_list


def get_stock_code_list_interested(conn):
    code_list = []

    query = "select code from target_list"
    c = conn.cursor()
    
    for row in c.execute(query):
        code_list.append(row[0])
    
    return code_list

def get_stock_info_interested(conn, code):
    query = "select category, added_date, base_price, origin from target_list where code = '{}'".format(code)
    c = conn.cursor()
    
    for row in c.execute(query):
        return row[0], row[1], row[2], row[3]
    
    return None, None, None, None, None
    
def get_latest_transaction(conn, code):
    query = "select code, max(op_time), operation from trade_history where code = '{}'".format(code)
    
    #print(query)
    c = conn.cursor()
    #result = 
    #print("History returns {}" + str(result.rowcount))

    for row in c.execute(query):
        return row[1], row[2]
    now = datetime.now()
    return now.strftime(FORMAT_DATE), 'SELL'
    

def get_own_stock_info(conn, code):
    query = "select cnt, avg_price from current_stock where code = '{}'".format(code)
    c = conn.cursor()
    
    for row in c.execute(query):
        return row[0], row[1]
    
    return 0, 0.0
    
def clean_history_table(conn):
    query = "delete from trade_history"
    c = conn.cursor()
    c.execute(query)

def create_stock_basic_info_table(conn):
    query = """CREATE TABLE IF NOT EXISTS stock_basic_info(
                code TEXT NOT NULL,
                name_kor TEXT NOT NULL, 
                name_eng TEXT NOT NULL,
                market_type TEXT NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True


def create_target_list_table(conn):
    query = """CREATE TABLE IF NOT EXISTS target_list(
                category TEXT NOT NULL,            
                code TEXT PRIMARY KEY NOT NULL,
                added_date DATE NOT NULL, 
                base_price FLOAT NOT NULL,
                origin TEXT NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True


def create_trade_history_table(conn):
    query = """CREATE TABLE IF NOT EXISTS trade_history(
                code TEXT NOT NULL,
                op_time DATETIME NOT NULL,
                operation TEXT NOT NULL,
                volume INT NOT NULL,
                price FLOAT NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True

def create_current_stock_table(conn):
    query = """CREATE TABLE IF NOT EXISTS current_stock(
                code TEXT PRIMARY KEY NOT NULL,
                cnt INT NOT NULL,
                avg_price FLOAT NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True


def insert_current_stock(conn, code, avg_price, cnt):
    try:
        c = conn.cursor()
        query = (
                 "insert or replace into current_stock(code, cnt, avg_price) "
               + "values('{}', {}, {:.1f})"
               ).format(code, str(cnt), avg_price)
        print(query)
        c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)


def insert_target_list(conn, category, code, base_price, added, origin):
    try:
        c = conn.cursor()
        query = (
                 "insert or replace into target_list(category, code, added_date, base_price, origin) "
               + "values('{}', '{}', '{}', {:.1f}, '{}')"
               ).format(category, code, added, base_price, origin)
        print(query)
        c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)
    

def insert_stock_basic_info(conn, rdr):
    try:
        c = conn.cursor()
        for line in rdr:
            code = line[1].replace("'", "")
            name_kor = line[3].replace("'", "")
            name_eng = line[4].replace("'", "")
            market = line[6].replace("'", "")
            
            query = (
                    "insert or replace into stock_basic_info(code, name_kor, name_eng, market_type) "
                    + "values('{}', '{}', '{}', '{}' )"
                    ).format(code, name_kor, name_eng, market)
            #print(query)
            c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)

def init_stock_basic_info_table(conn, csv_file):
    create_stock_basic_info_table(conn)
 
    f = open(csv_file,'r')
    rdr = csv.reader(f)
 
    insert_stock_basic_info(conn, rdr)
     
    f.close()   