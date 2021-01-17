import sqlite3
import FinanceDataReader as fdr
from datetime import datetime
from workalendar.asia import SouthKorea
from datetime import date

cal = SouthKorea()



IS_TEST = True
test_today = date(2021,1,15)
#print(cal.is_working_day(date(2021,1,16)))


def get_today():
    if IS_TEST:
        return datetime(test_today.year, test_today.month, test_today.day)
    else
        return datetime.now()

def is_working_day(t):
    return cal.is_working_day(date(t.year, t.month, t.day))

#-------------------------
#https://financedata.github.io/posts/finance-data-reader-users-guide.html

FORMAT_DATE = "%Y-%m-%d"
my_codes = ['068270', '005930']
code = ['140410', '302550', '251370', '064760', '036810', '005070', '278280', '298050', '009830', '306200', '327260',
        '218410', '099320', '001820', '009150', '066570', '012330', '102120', '036420']

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
        return "{} {} {:.1f}".format(self.code, self.date.strftime(FORMAT_DATE), self.closep)
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

def get_stock_data(code, s, e):
    price_days = []
    col_closed = 'Close'
    sdate_str = s.strftime(FORMAT_DATE)
    edate_str = e.strftime(FORMAT_DATE)
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
        
        if same_date(e, last_date):
            break;
        sdate_str = "{}-{}-{}".format(last_date.year, last_date.month+1, last_date.day)

    return price_days

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
        result_list = get_stock_data(code, date_from, now)
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
    query = (
            "insert or ignore into trade_history(code, op_time, operation, volume, price) " + 
            "values('{}','{}','{}',{},{:.2f})"
            ).format(code, op_time, op, str(vol), price);
    try:
        c = conn.cursor()
        print(query)
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
    d = now.strftime("%y-%m-%d")
    print("Today: " + d)
    return get_closed_price(code, d)




#from_date = datetime(2001, 1, 1)
#prepare_initial_table(conn, from_date)  #returns only 5 per query
#log_buy_stock(conn, '068270', 300000, 999)
#log_sell_stock(conn, '068270', 380000, 999)


if __name__ == "__main__":
    t = get_today()
    if not is_working_day(t):
        print("Today is not a working day. pass")
        pass

    log_sell_stock(conn, '140410', 380000, 999, datetime(2020,1,20))

    conn = sqlite3.connect("stock.db")
    c = conn.cursor()
    create_table(conn)
    #create_trade_history_table(conn)


    #first update latest price in the db
    if not update_today_price_info(conn, code):
        print("There is no dat for today..very strange....")
        pass


    #get list of prices from last transaction date
    log_date, op, price = get_last_transaction(code)
    to_buy = False

    if log_date == None:
        print("No transaction log...Please check... ")
        sdate = t
    else:
        tokens = log_date.split('-')
        sdate = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
        if op == "SELL":
            to_buy = True   #We don't have stock. Check if time to buy
        else:
            to_buy = False #We hae stocks. Check if time to sell

    print("Starting date .. {}".format(sdate.strftime(FORMAT_TIME)))
    valid, date_list, price_list = get_simulation_data_from_db('stock_all.db', code, sdate, t)

    if not valid:
        print("Data is not valid... ")
        pass

    if to_buy:
        #get the lowest price & date



    else:
        #get the highest price & date 

    


    print("Current proce: " + str(get_current_price(test_code)))
    #insert or update the today's price


    conn.close()
