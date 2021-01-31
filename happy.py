import FinanceDataReader as fdr
from datetime import datetime
from datetime import timedelta
from workalendar.asia import SouthKorea
from datetime import date
import numpy as np
import hdb
import code_list

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

my_codes_t =  code_list.my_code_list_t
my_codes = my_codes_t.keys()

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
        return "{0: <6}:{1: <15} {2} {3: <10.0f} {4: <5.2f}".format(
                self.code, my_codes_t[self.code], self.date.strftime(FORMAT_DATE), self.closep, self.change*100)
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
            s = StockPrice(code, last_date, float(openp[i]), float(highp[i]), 
                    float(lowp[i]),  float(c), int(vol[i]), float(change[i]))
            price_days.append(s)
            #print(s.to_text())
            i += 1
        
        if same_date(e_datetime, last_date):
            break;
        last_date += timedelta(days=1)
        sdate_str = "{}-{}-{}".format(last_date.year, last_date.month, last_date.day)
        #sdate_str = "{}-{}-{}".format(last_date.year, last_date.month+1, last_date.day)

    return price_days

def log_sell_stock(conn, code, price, vol, log_date = None):
    return log_stock_trading(conn, code, 'SELL', price, vol, log_date)

def log_buy_stock(conn, code, price, vol, log_date = None):
    return log_stock_trading(conn, code, 'BUY', price, vol, log_date)

#print(fdr.__version__)


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
    hdb.insert_stock_data(conn, l)
   
    #get list of prices from last transaction date
    log_date, op = hdb.get_latest_transaction(conn, code)
    to_buy = False
    log.w("Starting date by the latest transaction: {} --> {}".format(log_date, op))
    if log_date == None:
        log.w("No transaction log...Please check... Error")
        return 'NO_LATEST_TRANSACTION'
    else:
        tokens = log_date.split(' ')[0].split('-')
        sdate = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
        #sdate += timedelta(days=1)
        if op == "SELL":
            log.w("Check if today is the time to BUY from date {}".format(sdate.strftime(FORMAT_DATE)))
            to_buy = True   #We don't have stock. Check if today is the time to buy
        else:
            log.w("Check if today is the time to SELL from date {}".format(sdate.strftime(FORMAT_DATE)))
            to_buy = False #We hae stocks. Check if today is the time to sell

    buy_factor = 1.1
    sell_factor = 0.9
    
    valid, list_date, list_price = hdb.get_stock_data_from_db(conn, code, sdate, t)

    if not valid:
        log.w("Data is not valid... ")
        return 'NO_STOCK_DATA_IN_DB'

    #I Love papa
    #I love Nayun.

    if to_buy:
        #get the lowest price & date
        idx = np.argmin(list_price)
        log.w("Lowest data: {} ==> {:.1f} factor {:.1f}   today: {:.2f}".format(
                                    list_date[idx], list_price[idx], list_price[idx]*buy_factor, list_price[-1]))
        if list_price[idx]*buy_factor <= list_price[-1]:
            #buy stock
            log.w("Time to buy.....")
            #log_stock_trading(conn, code, 'BUY', list_price[-1], 8888888, t)
            return "-BUYCHECK_BUY-    today: {0: <6.0f} t: {1: <6.0f} ({2} {3:.0f})".format(
                    list_price[-1], list_price[idx]*buy_factor, list_date[idx][5:], (list_price[idx]*buy_factor - list_price[-1]))

        else:
            log.w("It's not time to buy yet.")
            return "BUYCHECK_NOBUY    today: {0: <6.0f} t: {1: <6.0f} ({2} {3:.0f})".format(
                    list_price[-1], list_price[idx]*buy_factor, list_date[idx][5:], (list_price[idx]*buy_factor - list_price[-1]))

        
    else:
        #get the highest price & date 
        idx = np.argmax(list_price)
        log.w("Highest data: {} ==> {:.1f} factor {:.1f}  today: {:.2f}".format(
                                    list_date[idx], list_price[idx], list_price[idx]*sell_factor, list_price[-1]))
        if list_price[idx]*sell_factor >=  list_price[-1]:
            #buy stock
            log.w("Time to sell.....")
            #log_stock_trading(conn, code, 'SELL', list_price[-1], 8888888, t)
            return "-SELLCHECK_SELL-  today: {0: <6.0f} t: {1: <6.0f} ({2} {3:.0f})".format(
                    list_price[-1], list_price[idx]*sell_factor, list_date[idx][5:], (list_price[-1] - list_price[idx]*sell_factor))

        else:
            log.w("It's not time to sell yet.")
            return "SELLCHECK_NOSELL  today: {0: <6.0f} t: {1: <6.0f} ({2} {3:.0f})".format(
                    list_price[-1], list_price[idx]*sell_factor, list_date[idx][5:], (list_price[-1] - list_price[idx]*sell_factor))


    log.w("Done")

#from_date = datetime(2001, 1, 1)
#prepare_initial_table(conn, from_date)  #returns only 5 per query
#log_buy_stock(conn, '068270', 300000, 999)
#log_sell_stock(conn, '068270', 380000, 999)

import sys


if __name__ == "__main__":

    conn = hdb.connect_db(MY_HOME + "stock_all.db")
    happy_start = datetime(2021, 1, 14)
    
    if len(sys.argv) >= 2:
        if sys.argv[1] == "init":
            print("Init trading history table only. ")
            hdb.clean_history_table(conn)
            for c in my_codes:
                hdb.log_stock_trading(conn, c, 'SELL', 999999999, 8888888, happy_start)
            conn.close()
            sys.exit()
        elif sys.argv[1] == "mark":
            print("Put your op data here")
            #clearn_history_table(conn)
            #hdb.log_stock_trading(conn, '048260', 'SELL', 55700.0, 133, datetime(2021,1,20))
            #hdb.log_stock_trading(conn, '336370', 'SELL', 51800.0, 133, datetime(2021,1,20))
            #hdb.log_stock_trading(conn, '047810', 'SELL', 31600.0, 133, datetime(2021,1,20))
            #hdb.log_stock_trading(conn, '272210', 'SELL', 18300.0, 133, datetime(2021,1,14))
            #hdb.log_stock_trading(conn, '012450', 'SELL', 18300.0, 133, datetime(2021,1,18))
            #hdb.log_stock_trading(conn, '051500', 'SELL', 21750.0, 133, datetime(2021,1,14))
            hdb.log_stock_trading(conn, '099320', 'SELL', 58500, 133, datetime(2021,1,28))


            #hdb.log_stock_trading(conn, '327260', 'BUY', 31750.0, 133, datetime(2021,1,25))
            #hdb.log_stock_trading(conn, '009150', 'BUY', 219000.0, 133, datetime(2021,1,25))
            #hdb.log_stock_trading(conn, '048260', 'BUY', 61000.0, 133, datetime(2021,1,25))
            #hdb.log_stock_trading(conn, '051500', 'BUY', 22950.0, 133, datetime(2021,1,25))
            #hdb.log_stock_trading(conn, '012450', 'BUY', 46000.0, 133, datetime(2021,1,25))

            #hdb.log_stock_trading(conn, '066570', 'BUY', 166500.0, 8888888, dd)
            #hdb.log_stock_trading(conn, '306200', 'BUY', 108500.0, 8888888, dd)
            #hdb.log_stock_trading(conn, '012330', 'BUY', 363000.0, 8888888, dd)
            conn.close()
            sys.exit()

    d = datetime.now()
    #d = datetime(2021,1,22)
    for k in range(1):    
        res = []
        for c in my_codes:
            r = check_today_data(conn, c, d)
            res.append(r)
    
        #print the result
        log.w("------------------ result TODAY:  {} -------------------------".format(d.strftime(FORMAT_DATE)), True)
        
        i = 0
        for c in my_codes:
            log.w("{0: <6}:{1: <15} => {2: <30}".format(c, my_codes_t[c], res[i]), True)
            i += 1
        d += timedelta(days=1)
    
    log.disable()
    conn.close()
    
