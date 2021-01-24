# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 11:00:40 2021

@author: keybd
"""
import sqlite3
from datetime import datetime
from datetime import date

FORMAT_DATE = '%Y-%m-%d'

def connect_db(db_name):
    conn = sqlite3.connect(db_name)
    return conn


def get_stock_data_from_db(conn, code, s_datetime, e_datetime):
    c = conn.cursor()
    
    #for row in c.execute('select * from stocks order by code, sdate'):
    #for row in c.execute('select * from trade_history order by op_time'):
    query = "select sdate, close from stocks where code = '{}' and sdate >= '{}' and sdate <= '{}' order by sdate".format(
            code, s_datetime.strftime(FORMAT_DATE), e_datetime.strftime(FORMAT_DATE))
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
    
    
def clean_history_table(conn):
    query = "delete from trade_history"
    c = conn.cursor()
    c.execute(query)
    
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


