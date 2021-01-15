
"""
Created on Tue Dec 29 22:42:02 2020

@author: keybd
"""
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import read_csv
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.layers.core import Dense, Activation, Dropout
import tensorflow as tf
import time #helper libraries
import os
from datetime import datetime


#start_price, end_price, real_money, current_value, total_cnt, invest, current
class Simulation_result:
    def __init__(self, s, e, real, cur, cnt, s_invest):
        self.s_price = s
        self.e_price = e
        self.real_money = real
        self.current_value = cur
        self.test_cnt = cnt
        self.init_investment = s_invest
        self.current_invest = self.real_money + self.current_value
        self.profit_rate = (self.current_invest - self.init_investment)/self.init_investment*100.0

    def set_config(self, csv_file, buy_ratio, sell_ratio, take_earning, invest_year, buy_cnt, sell_cnt):
        self.f_name = csv_file
        self.buy_ratio = buy_ratio
        self.sell_ratio = sell_ratio
        self.take_earning = take_earning
        self.invest_year = invest_year
        self.buy_cnt = buy_cnt
        self.sell_cnt = sell_cnt
    def get_config_string(self):
        return "{:.2f} {:.2f} {} {} {} {}".format(self.buy_ratio, self.sell_ratio, self.take_earning, str(self.invest_year), str(self.buy_cnt), str(self.sell_cnt))
    
    def to_excel_string(self):
        return self.get_config_string() + " " + "{} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}\n".format(
            self.f_name, self.s_price, self.e_price, self.real_money, self.current_value, self.test_cnt, self.init_investment,
            self.current_invest, self.profit_rate)

    def to_friendly_string(self):
        return "{} : Initial {:.2f} =>  {:.2f}  start: {:.2f} today: {:.2f}  test_cnt:{} profit: {:.2f} ({:.2f}%) real: {:.2f}".format(
            self.f_name, self.init_investment, self.current_invest, self.s_price, self.e_price, str(self.test_cnt),
            (self.current_invest - self.init_investment), self.profit_rate, self.real_money)
    

def simulate_trading(csv_file, list_date, list_price, invest_year = 3, take_earning=False, buy_factor=1.1, sell_factor=0.9, buy_begin=True, draw_plot = False):
    test_cnt = len(list_date)
    y = list_price
    initial_invest = 10000000
    invest = initial_invest
    real_money = 0
    start_idx = 0
    buy_cnt = 0
    sell_cnt = 0
    
    if draw_plot:
        dates = np.array(list_date)
        plt.figure(2)
        max_x_lbls = 8
        if test_cnt > max_x_lbls:
            x_interval = int(test_cnt/max_x_lbls)
            for i in range(len(dates)):
                if i % x_interval != 0 and i != test_cnt -1:
                    dates[i] = ''
                    
        plt.xticks(rotation=90)
        xs = np.linspace(0, test_cnt-1, test_cnt)
        plt.xticks(xs, dates)
        plt.plot(y[start_idx:], 'r')
    
    if buy_begin:
        buy = y[start_idx]
        s_cnt = math.floor(invest/buy)
        invest = invest - s_cnt * buy
        buy_cnt += 1
        if draw_plot:
            plt.text(0, y[start_idx], 'b')
        #print("{}   Buy stock price: {}   cnt: {}   invest: {} ".format(full_date[start_idx], str(buy), str(s_cnt), str(invest)))
    else:
        buy = 0
        s_cnt = 0
        
        
    last_max = y[start_idx]
    last_min = y[start_idx]
    
    for i in range(len(y)):
        if buy_begin and i == start_idx:
            continue
        today = y[i]
        if buy > 0: #check if time to sell
            if today > last_max:
                last_max = today
            sell_val = last_max * sell_factor
            if today < sell_val:
                #Sell stock
                invest = invest + s_cnt*today
                if draw_plot:
                    plt.text(i-start_idx, today, "s")
                if take_earning and invest > initial_invest:
                    real_money = real_money + (invest-initial_invest)
                    invest = initial_invest
                #print("{}  Sell stock prince: {}  cnt: {}   score: {:.2f}  real: {:.2f}".format(list_date[i], str(today), s_cnt, ((invest-initial_invest+real_money)/initial_invest*100), real_money))
                sell_cnt += 1
                s_cnt = 0
                buy = 0
                last_min = 999999999999999999 #Very big value
        else:
            if today < last_min:
                last_min = today
            buy_val = last_min * buy_factor
            if today > buy_val:
                buy = today
                buy_cnt += 1
                s_cnt = math.floor(invest/buy)
                invest = invest - s_cnt*buy
                if draw_plot:
                    plt.text(i-start_idx, today, "b")
                #print("{}   Buy stock price: {}  cnt: {}  ".format(list_date[i], str(today), str(s_cnt)))
                last_max = today
                    
    current_invest = invest + today * s_cnt
            
    #print("Initial {}   ==>  {:.2f}  start: {:.2f} today: {:.2f}  cnt:{}   earned:  {:.2f}  {:.2f} %  (real_money:  {:.2f}) ".format(
    #        initial_invest, current_invest, y[0], today, str(s_cnt), real_money + current_invest - initial_invest, (((current_invest - initial_invest)+real_money)/initial_invest * 100), real_money))
    
    #print("total cnt: " + str(test_cnt))
    if draw_plot:            
        plt.xlabel('Time Period')
        plt.ylabel('Stock Price')
        plt.show()
    #to return
    #start_price, end_price, real_money, current_value, total_cnt, invest, current, profit rate
    r = Simulation_result(y[0], today, real_money, current_invest, test_cnt, initial_invest)
    r.set_config(csv_file, buy_factor, sell_factor, take_earning, invest_year, buy_cnt, sell_cnt)
    
    return r
    

    
#main begins
dir_name = './csv2/'

end_year = '2020'
end_mon = '06'

def get_simulation_data(f_name):
    prefix = dir_name
    clear_prefix = dir_name + 'clear/'
    stock_file_name = prefix + f_name
    filtered_name = clear_prefix + 'clear_' + f_name
    encoding = 'euc-kr'
    
    fd = open(stock_file_name, "rt")
    new_fd = open(filtered_name, "wt")
    
    #remove all null values
    fd = open(stock_file_name, "rt")
    new_fd = open(filtered_name, "wt")
    first_line = True
    invalid_file = False
    for l in fd:
        if first_line:
            first_line = False
            continue
        if l.find('null') > 0:
            continue
        tokens = l.split(',')
        ll = tokens[0].split('-')
        year = ll[0]
        mon = ll[1]
        if (year >= end_year and mon >= end_mon) or (year > end_year):
            #print("Skip " + year + " " + mon)
            continue
        if year >= '2015':
            if tokens[4] == '0':
                print(stock_file_name + ":" + tokens[0] + " zero")
                invalid_file = True
                break
            new_fd.write(l)
    fd.close()
    new_fd.close()
    
    if invalid_file:
        os.remove(filtered_name)
        return False, np.array(0), np.array(0)
    else:
        names = ['Date','Open','High','Low','Close','Volume','Adj Close']
        raw_dataframe = pd.read_csv(filtered_name, names=names, encoding=encoding) 
        #raw_dataframe.info()
        
        full_date = raw_dataframe['Date']
        del raw_dataframe['Date']
        
        stock_info = raw_dataframe.values[1:].astype(np.float)
        full_date = np.array(full_date[1:])
        
        price = stock_info[:, :-1]
        y = price[:, -2]
        return True, full_date, y




days_per_year = 240



# y=5
# csv_file = '002787.KS.csv'
# need_cnt = days_per_year * y

# date_list, price_list = get_simulation_data(csv_file)
# simulate_from = -1 * need_cnt
# r = simulate_trading(csv_file, date_list[simulate_from:], price_list[simulate_from:], take_earning = False, invest_year = 5, buy_factor=1.1, sell_factor= 0.9, draw_plot=True)



# print(r.to_friendly_string())


years = [1, 3, 5]
buy_factors = [1.1, 1.15, 1.2, 1.25, 1.3]
sell_factors = [0.7, 0.75, 0.8, 0.85, 0.9]
t_earnings = [False, True]

years = [1]
buy_factors = [1.1]
sell_factors = [0.9]
t_earnings = [False]

test_list = []

code = ['140410', '302550', '251370', '064760', '036810', '005070', '278280', '298050', '009830', '306200', '327260',
        '218410', '099320', '001820', '009150', '066570', '012330', '102120', '036420']
# code = ['005930', '000660', '051910','207940','005380','035420','006400',
#         '068270','035720','012330','028260','002700','096770','005490','051900',
#         '091990','066570','036570','017670','034730','105560','003550','055550',
#         '015760','018260','032830','009150','326030','090430','251270','033780',
#         '086790','011170','018880','009830','000810','010950','009540','010130']

#code = ['032680']

for c in code:
    test_list.append( c + ".csv")

now = datetime.now() 
log_file = 'simulate_' + now.strftime("%m%d_%H%M") + '.txt'
log_fd = open(log_file, "wt")

from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir(dir_name) if isfile(join(dir_name, f))]

progress_cnt = len(years) * len(onlyfiles)
cur_test = 0
cur_file_idx = 1



#for csv_file in test_list:
for csv_file in onlyfiles:
    # if csv_file not in onlyfiles:
    #     print(csv_file + " does not exist")
    #     continue
    valid, date_list, price_list = get_simulation_data(csv_file)
    if not(valid):
        print("Skipping invalid file: " + csv_file)
        continue
    for y in years:
        print("Processing file {} {}/{}   {:.2f} %".format(
            csv_file, str(cur_file_idx), str(len(onlyfiles)), (cur_test/progress_cnt)*100.0))
        for b in buy_factors:
            for s in sell_factors:
                for e in t_earnings:
                    need_cnt = days_per_year * y
                    cnt = len(date_list)
                    if cnt >= need_cnt:
                        simulate_from = -1 * need_cnt
                        r = simulate_trading(csv_file, date_list[simulate_from:], price_list[simulate_from:], take_earning = e, invest_year = y, buy_factor=b, sell_factor= s, draw_plot=True)
                        print(r.to_excel_string())
                        log_fd.writelines(r.to_excel_string())
        cur_test = cur_test + 1
    cur_file_idx = cur_file_idx + 1
    
log_fd.close()


    
    
  
def create_r(tokens):
    buy_r = float(tokens[0])
    sell_r = float(tokens[1])
    take_earning = False
    if tokens[2] == 'True':
        take_earning = True
    year_n = int(tokens[3])
    buy_cnt = int(tokens[4])
    sell_cnt = int(tokens[5])
    fname = tokens[6]
    s_price = float(tokens[7])
    e_price = float(tokens[8])
    real_m = float(tokens[9])
    v = float(tokens[10])
    d_cnt = float(tokens[11])
    init_m = float(tokens[12])
    curr_m = float(tokens[13])
    p_ratio = float(tokens[14])
    r = Simulation_result(s_price, e_price, real_m, v, d_cnt, init_m)
    r.set_config(fname, buy_r, sell_r, take_earning, year_n, buy_cnt, sell_cnt)
    return r
        
    

def get_stat(list_r, b, s, y, t):
    #statistics
    item_cnt = 0
    sum_ratio = 0.0
    minus_cnt = 0
    sum_profit = 0.0
    good_cnt = 0
    bad_cnt = 0
    avg_profit_ratio = 0.0
    avg_profit = 0.0
    
    for r in list_r:
        if r.buy_ratio == b and r.sell_ratio == s and r.invest_year == y and r.take_earning == t:
            item_cnt += 1
            sum_ratio += r.profit_rate
            if r.profit_rate < 0:
                minus_cnt += 1
            if r.profit_rate > 50.0:
                good_cnt += 1
            if r.profit_rate < -50.0:
                bad_cnt += 1
            sum_profit += r.current_invest - r.init_investment
    
    if item_cnt > 0:
        #total count
        #average profit ratio
        avg_profit_ratio = sum_ratio / item_cnt
        #minus count
        #average profit
        avg_profit = sum_profit / item_cnt
        #over 50% count
        #lower 50% cnt
    
    return item_cnt, avg_profit_ratio, minus_cnt, good_cnt, bad_cnt, avg_profit



result = []

fname = log_file #'simulate_0110_1820.txt'
#fname = 'simulate_0110_2155.txt'
f = open(fname, 'rt')

for l in f:
    t = l.split(" ")
    r = create_r(t)
    result.append(r)

b_factor = 1.1
s_factor = 0.9
inv_year = 3
take_earning = False

years = [1, 3, 5]
buy_factors = [1.1, 1.15, 1.2, 1.25, 1.3]
sell_factors = [0.7, 0.75, 0.8, 0.85, 0.9]
t_earnings = [False, True]

years = [3]
buy_factors = [1.1]
sell_factors = [0.9]
t_earnings = [False]

for b_factor in buy_factors:
    for s_factor in sell_factors:
        for inv_year in years:
            for etake in t_earnings:
                #print("{:.2f}  {:.2f}   {}  {}".format(b_factor, s_factor, str(inv_year), etake))
                item_cnt, avg_profit_ratio, minus_cnt, good_cnt, bad_cnt, avg_profit = get_stat(result, b_factor, s_factor, inv_year, etake)                
                if item_cnt > 0:
                    print("{:.2f} {:.2f} year: {} Take: {} total: {}  avg_profit: {:.2f} avg_profit_ratio {:.2f} good: {}  bad: {}  minus: {}".format(
                        b_factor, s_factor, str(inv_year), etake, str(item_cnt), avg_profit, avg_profit_ratio, good_cnt, bad_cnt, minus_cnt))

f.close()

