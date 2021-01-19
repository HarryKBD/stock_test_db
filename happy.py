import sqlite3
import FinanceDataReader as fdr
from datetime import datetime
from datetime import timedelta
from workalendar.asia import SouthKorea
from datetime import date
import numpy as np

FORMAT_DATE = '%Y-%m-%d'
MY_HOME='/home/pi/stock_test_db/'

cal = SouthKorea()

class Logger:
    def __init__(self, fname):
        now = datetime.now()
        self.log_file = MY_HOME + fname + '_log_' + now.strftime("%m%d") + '.txt'
        self.log_level = 5
        self.fd_opened = False
        
    def enable(self):
        self.fd = open(self.log_file, "a")
        self.fd_opened = True
        
    def w(self, msg, cprint = False, level=1):
        if self.log_level > level:
            self.fd.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "  :  " + msg + "\n")
        if cprint:
            print(msg)
        
    def set_level(level):
        self.log_level = level
        
    def disable(self):
        if self.fd_opened:
            self.fd_opened = False
            self.fd.close()


#global log
log = Logger("flow")
log.enable()    

def get_today():
    return datetime.now()

def is_working_day(t):
    return cal.is_working_day(date(t.year, t.month, t.day))

#-------------------------
#https://financedata.github.io/posts/finance-data-reader-users-guide.html

my_codes = ['068270', '005930']
code = ['140410', '302550', '251370', '064760', '036810', '005070', '278280', '298050', '009830', '306200', '327260',
        '218410', '099320', '001820', '009150', '066570', '012330', '102120', '036420', '005930']

my_codes = code



class StockPrice:
    def __init__(self, code, date, openp = 0.0, highp = 0.0, lowp = 0.0, closep=0.0, volume = 0, change=0.0):
        self.code = code
        self.date = date
        self.closep = closep
        self.openp = openp
        self.highp = highp
        self.lowp = lowp
        self.change = change
        self.volume = volume

    def to_price_text(self):
        return "{} {} {:.1f} {:.1f}".format(self.code, self.date.strftime(FORMAT_DATE), self.closep, self.change)
    def to_full_text(self):
        return "{} {} {:.1f} {:.1f} {:.1f} {:.1f} {} {:.1f}".format(
                self.code, self.date.strftime(FORMAT_DATE), 
                self.openp, self.highp, self.lowp, self.closep, self.volume, self.change)
    def get_code(self):
        return self.code
    def get_date(self):
        return self.date.strftime(FORMAT_DATE)
    def get_open(self):
        return self.openp
    def get_high(self):
        return self.highp
    def get_low(self):
        return self.lowp
    def get_close(self):
        return self.closep
    def get_volume(self):
        return self.volume
    def get_change(self):
        return self.change

def same_date(a, b):
    if a.year == b.year and a.month == b.month and a.day == b.day:
        return True
    else:
        return False

def get_stock_data_from_server(code, s_datetime, e_datetime):
    price_days = []
    col_closed = 'Close'
    sdate_str = s_datetime.strftime(FORMAT_DATE)
    edate_str = e_datetime.strftime(FORMAT_DATE)
    #print("Connecting server to get data code: {}  from: {}  to: {} ".format(code, sdate_str, edate_str))
    while True:
        df = fdr.DataReader(code, sdate_str, edate_str)
        if len(df) == 0:
            #print("No more data for code : " + code)
            break
        #print(df.head())
        openp = df['Open']
        highp = df['High']
        lowp = df['Low']
        closep = df[col_closed]
        vol = df['Volume']
        change = df['Change']

        idx = df.index
        i = 0
        for c in closep:
            last_date =  idx[i].to_pydatetime()
            dd = last_date.strftime(FORMAT_DATE)
            s = StockPrice(code, last_date, float(openp[i]), float(highp[i]), 
                    float(lowp[i]),  float(c), int(vol[i]), float(change[i]))
            price_days.append(s)
            #print(s.to_text())
            i += 1
        
        if same_date(e_datetime, last_date):
            break;
        sdate_str = "{}-{}-{}".format(last_date.year, last_date.month+1, last_date.day)

    return price_days



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


def prepare_initial_table(conn, date_from):
    now = datetime.now()
    edate_str = now.strftime(FORMAT_DATE)

    sdate_str = date_from.strftime(FORMAT_DATE)
    
    now = datetime(2021, 1,16)

    print("{} from  ==> {} to".format(sdate_str, edate_str))
    cnt = 1
    for code in my_codes:
        result_list = get_stock_data_from_server(code, date_from, now)
        insert_stock_data(conn, result_list)
        print("Getting {} data:  {} / {} ==> cnt: {}".format(code, str(cnt), str(len(my_codes)), str(len(result_list))))
        cnt += 1

    #op 1: 'BUY'  2: 'SELL'

def log_stock_trading(conn, code, op, price, vol, log_date = None):
    if log_date:
        now = log_date
    else:
        now = datetime.now()
    op_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    log.w("ACTION: {} code: {}  optime: {} price: {:.1f}".format(op, code, op_time, price), True)
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

def log_sell_stock(conn, code, price, vol, log_date = None):
    return log_stock_trading(conn, code, 'SELL', price, vol, log_date)

def log_buy_stock(conn, code, price, vol, log_date = None):
    return log_stock_trading(conn, code, 'BUY', price, vol, log_date)
 

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

#print(fdr.__version__)

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
    
    
def clearn_history_table(conn):
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



def check_today_data(conn, code, today = None):
    
    t = datetime.now()
    if today != None:
        t = today
        
    if not is_working_day(t):
        log.w("Today {} is not a working day. pass".format(t.strftime(FORMAT_DATE)))
        return 'HOLIDAY'
    
    #first update latest price in the db
    log.w("Getting today's data from server and insert into database. today is : " + t.strftime(FORMAT_DATE))
    l = get_stock_data_from_server(code, t, t)
    if len(l) != 1:
        log.w("There is no data for today..very strange....")
        return 'NO_DATA_FROM_SERVER'

    log.w("Got today's data! " + l[0].to_price_text(), True)
    insert_stock_data(conn, l)
   
    #get list of prices from last transaction date
    log_date, op = get_latest_transaction(conn, code)
    to_buy = False
    log.w("Starting date by the latest transaction: {} --> {}".format(log_date, op))
    if log_date == None:
        log.w("No transaction log...Please check... Error")
        return 'NO_LATEST_TRANSACTION'
    else:
        tokens = log_date.split(' ')[0].split('-')
        sdate = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
        if op == "SELL":
            log.w("Check if today is the time to buy")
            to_buy = True   #We don't have stock. Check if today is the time to buy
        else:
            log.w("Check if today is the time to SELL")
            to_buy = False #We hae stocks. Check if today is the time to sell

    buy_factor = 1.1
    sell_factor = 0.9
    
    valid, list_date, list_price = get_stock_data_from_db(conn, code, sdate, t)

    if not valid:
        log.w("Data is not valid... ")
        return 'NO_STOCK_DATA_IN_DB'

    if to_buy:
        #get the lowest price & date
        idx = np.argmin(list_price)
        log.w("Lowest data: {} ==> {:.1f} factor {:.1f}   today: {:.2f}".format(
                                    list_date[idx], list_price[idx], list_price[idx]*buy_factor, list_price[-1]))
        if list_price[idx]*buy_factor <= list_price[-1]:
            #buy stock
            log.w("Time to buy.....")
            #log_stock_trading(conn, code, 'BUY', list_price[-1], 8888888, t)
            return "BUYCHECK_BUY     today: {:.1f}    target: {:.1f} ({:.1f})".format(
                    list_price[-1], list_price[idx]*buy_factor, (list_price[idx]*buy_factor - list_price[-1]))

        else:
            log.w("It's not time to buy yet.")
            return "BUYCHECK_NOBUY   today: {:.1f}    target: {:.1f} ({:.1f})".format(
                    list_price[-1], list_price[idx]*buy_factor, (list_price[idx]*buy_factor - list_price[-1]))

        
    else:
        #get the highest price & date 
        idx = np.argmax(list_price)
        log.w("Highest data: {} ==> {:.1f} factor {:.1f}  today: {:.2f}".format(
                                    list_date[idx], list_price[idx], list_price[idx]*sell_factor, list_price[-1]))
        if list_price[idx]*sell_factor >=  list_price[-1]:
            #buy stock
            log.w("Time to sell.....")
            #log_stock_trading(conn, code, 'SELL', list_price[-1], 8888888, t)
            return "SELLCHECK_SELL    today: {:.1f}    target: {:.1f} ({:.1f})".format(
                    list_price[-1], list_price[idx]*sell_factor, list_price[-1] - list_price[idx]*sell_factor)

        else:
            log.w("It's not time to sell yet.")
            return "SELLCHECK_NOSELL  today: {:.1f}    target: {:.1f} ({:.1f})".format(
                    list_price[-1], list_price[idx]*sell_factor, list_price[-1] - list_price[idx]*sell_factor)


    log.w("Done")

#from_date = datetime(2001, 1, 1)
#prepare_initial_table(conn, from_date)  #returns only 5 per query
#log_buy_stock(conn, '068270', 300000, 999)
#log_sell_stock(conn, '068270', 380000, 999)

import sys


if __name__ == "__main__":

    conn = sqlite3.connect(MY_HOME + "stock_all.db")
    c = conn.cursor()

    happy_start = datetime(2021, 1, 14)
    
    if len(sys.argv) >= 2:
        if sys.argv[1] == "init":
            print("Init trading history table only. ")
            clearn_history_table(conn)
            for c in my_codes:
                log_stock_trading(conn, c, 'SELL', 999999999, 8888888, happy_start)
            conn.close()
            sys.exit()
        elif sys.argv[1] == "mark":
            print("Put your op data here")
            #clearn_history_table(conn)
            log_stock_trading(conn, '005930', 'SELL', 999999999, 8888888, happy_start)
            conn.close()
            sys.exit()

    d = datetime.now()
    #d = datetime(2021,1,15)
    for k in range(1):    
        res = []
        for c in my_codes:
            r = check_today_data(conn, c, d)
            res.append(r)
    
        #print the result
        log.w("------------------ result TODAY:  {} -------------------------".format(d.strftime(FORMAT_DATE)), True)
        
        i = 0
        for c in my_codes:
            log.w("{}  =>  {}".format(c, res[i]), True)
            i += 1
        d += timedelta(days=1)
    
    log.disable()
    conn.close()
    

