import FinanceDataReader as fdr
from datetime import datetime
from datetime import timedelta
from workalendar.asia import SouthKorea
from datetime import date
import numpy as np
import hdb
import code_list
import korea_stocks_info

FORMAT_DATE = '%Y-%m-%d'
#MY_HOME='/home/pi/stock_test_db/'
MY_HOME='./'

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
        return "{0: <6}: {1} {2: <10.0f} {3: <5.2f}".format(
                self.code, self.date.strftime(FORMAT_DATE), self.closep, self.change*100)
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


def get_highest_price_half_year(conn, code):
    today = datetime.now()
    #one_year_before = today - timedelta(days=365) 
    one_year_before = today - timedelta(days=182) 

    return get_highest_price_between(conn, code, one_year_before, today)

def get_highest_price_between(conn, code, from_datetime, to_datetime):
    valid, list_date, list_price = hdb.get_stock_data_from_db(conn, code, from_datetime, to_datetime)

    if valid != True:
        return -1, None

    max_price = max(list_price)
    result = [i for i, j in enumerate(list_price) if j == max_price]

    return list_date[result[-1]], list_price[result[-1]]



def check_today_data(conn, code, today = None, eng_name=True):
    
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

    #log.w("Got today's data! " + l[0].to_price_text(), True)
    hdb.insert_stock_data(conn, l)
    
    
    today_price = l[0].get_close()
    today_rate = l[0].get_change()*100

    category, added_date, base_price, origin = hdb.get_stock_info_interested(conn, code)
    
    if category == None:
        return "ERROR Code {}".format(code)

    cnt, avg_price = hdb.get_own_stock_info(conn, code)
    
    kor, eng = hdb.get_stock_names(conn, code)
    
    if eng_name == True:
        name = eng[0:13]
    else:
        name = kor[0:13]
    base_rate = (today_price - base_price)/base_price*100.0
    
    if cnt > 0:
        profit_rate = (today_price - avg_price)/avg_price*100.0


    max_date, max_price = get_highest_price_half_year(conn, code)
    diff_max = today_price - max_price
    rate_max = diff_max/max_price * 100.0


    str1 = "{7: <1} {0: <7} {1: <6} {2: <13} {3: <7.0f} {4: >4.1f} MAX:({9: <8}, {8: >4.0f} % {10: <7.0f})=> BASE [{5: <7.0f} {6: >4.0f} %] ".format(
            category[:6], code, name, today_price, today_rate, base_price, base_rate, origin[0], rate_max, max_date[2:], max_price)

    str2 = "{0: <28} {1: <5}".format(" "*28, added_date[2:7], origin)
    if cnt > 0:
        str2 = "MY [ {0: <8.0f} {1: <5.1f} ({2: <4}) ] {3: <5} ".format(avg_price, profit_rate, str(cnt), added_date[2:7], origin)

    log.w("Done")
    
    print(str1 + str2)

    #print("{0} => max date: {1}  price {2: 5.1f}".format(code, max_date, max_price))
    


import sys


if __name__ == "__main__":

    print_eng = True
    if len(sys.argv) >= 2:
        if sys.argv[1] == "kor":
            print_eng = False


    conn = hdb.connect_db(MY_HOME + "stock_all.db")
    code_list = hdb.get_stock_code_list_interested(conn)
    
 
    d = datetime.now()
    for code in code_list:
        r = check_today_data(conn, code, d, eng_name=print_eng)
        
        
    log.disable()
    conn.close()
