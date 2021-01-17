import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import read_csv
import math
import time #helper libraries
import os
from datetime import datetime
import sqlite3




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

def insert_stock_data(conn, s_list):
    try:
        c = conn.cursor()
        for s in s_list:
            query = (
                    "insert or ignore into stocks(code, sdate, open, high, low, close, volume, change) "
                    + "values('{}', '{}', {:.1f}, {:.1f}, {:.1f}, {:.1f}, {}, 0.0)"
                    ).format(s.get_code(), s.get_date(), s.get_open(), s.get_high(),
                            s.get_low(), s.get_close(), s.get_volume())
            #print(query)
            c.execute(query)

        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)
        pass


def execute_query(conn, query):
    try:
        c = conn.cursor()
        print(query)
        c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)
        pass


if __name__ == "__main__":
    
    conn = sqlite3.connect("test_db.db")
    c = conn.cursor()
    create_trade_history_table(conn)
    create_table(conn)
    query = ("insert or replace into stocks(code, sdate, open, high, low, close, volume, change) " +
                    "values('123123', '2021-01-06', 1001.0, 1001.0, 1001.0, 1000.0, 888888, 0.0 )" )

    execute_query(conn, query)
    
    query = "select * from stocks"
    
    for row in c.execute(query):
        print(row)
    
    x = np.array([0,1,2,3,4,5])
    print(x[0:2])
    print(np.max(x[:-1]))
    print(np.min(x))
    
    conn.close()
    
    
    
    