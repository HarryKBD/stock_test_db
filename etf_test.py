# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 15:20:58 2021

@author: keybd
"""


import hdb
import sys
import argparse
from datetime import datetime
from datetime import date
import happy
import korea_stocks_info
import code_list
import math
import matplotlib.pyplot as plt
import numpy as np


def test_profit_2(code, fdate, price):
    initial_budget = 300000000
    take_percent = 1
    buy_percent = 1
    taken_money = 0
    initial_invest = 250000000
    scnt = 0
    current_budget =   50000000
    invested = 0
    #total_taken = 0
    this_mon = '00'
    avg_price = 0
    
    rates = []
    dates = []
    sprices = []
    
    #first buy start
    scnt = math.floor(initial_invest/price[0])
    current_budget = initial_budget - (scnt*price[0])
    invested = scnt*price[0]
    fdate = fdate[1:]
    price = price[1:]
    avg_price = price[0]
    
    for idx in range(len(fdate)):

        tokens = fdate[idx].split('-')
        if tokens[0] == '2019' and tokens[1] == '12':
            break
        if this_mon != tokens[1]:
            #buy
            rate = (price[idx] - avg_price)/avg_price * 100
            value = price[idx] * scnt
            org_value = avg_price * scnt

            
            if abs(rate) > 10.0:
                #print(f'------- {fdate[idx]} =>  today: {price[idx]}, avg: {avg_price:.1f} rate: {rate:.1f} scnt: {scnt} current_budget: {current_budget}')
                if rate > 0:
                    earn = value - org_value
                    toget = math.floor(earn * take_percent)
                    cnt = math.floor(toget/price[idx])
                    taken_money = cnt * price[idx]
                    current_budget += taken_money
                    scnt -= cnt
                    #invested -= taken_money
                   # print(f' {fdate[idx]}  earned ==> today: {price[idx]}, avg: {avg_price:.1f} ==> earn: {earn}, so sell cnt: {cnt}  currens scnt: {scnt} current_budget: {current_budget}')
                else:
                    #minus now
                    lost = org_value - value
                    tobuy = lost * buy_percent
                    cnt = math.floor(tobuy/price[idx])
                    scnt += cnt
                    toinvest = cnt * price[idx]
                    current_budget -= toinvest
                    avg_price = (org_value + toinvest)/scnt
                   # print(f'{fdate[idx]}   lost ==> today: {price[idx]}, avg: {avg_price:.1f} ==> lost: {lost}, so buy cnt: {cnt}  currens scnt: {scnt}  current_budget: {current_budget}')

                value = scnt * price[idx]
                earn = (value + current_budget) - initial_budget
                profit_rate = earn / initial_budget * 100.0
                
                rates.append(earn)
                dates.append(fdate[idx])
                sprices.append(price[idx])
                this_mon = tokens[1]
               # print(f'{code} => data: {fdate[idx]} today_price: {price[idx]}: ==>  earn: {earn} avg_price: {avg_price} scnt: {scnt} prate: {profit_rate:.1f} budget: {current_budget}')

    print(f'{code} => data: {fdate[idx]} today_price: {price[idx]}: ==>  earn: {earn} avg_price: {avg_price} scnt: {scnt} prate: {profit_rate:.1f} budget: {current_budget}')
    
    return rates, dates, sprices
        


#take profit when we have some profit (over 10 % )
def test_data(code, fdate, price, takep):
    take_profit = takep
    take_percent = 5.0
    taken_money = 0
    invest = 1000000
    scnt = 0
    total_invested = 0
    this_mon = '00'
    

    
    rates = []
    dates = []
    sprices = []
    for idx in range(len(fdate)):
        tokens = fdate[idx].split('-')
        if tokens[0] == '2019' and tokens[1] == '12':
            break
        if this_mon != tokens[1]:
            #buy
            to_invest = invest
            if scnt > 0:
                value = scnt * price[idx]
                earn = value - total_invested
                profit_rate = earn / total_invested * 100.0
    
            
                if take_profit and profit_rate > 10:
                    toget = math.floor(earn * 0.2)
                    #to_invest = invest - toget
                    cnt = math.floor(toget/price[idx])
                    taken_money += cnt * price[idx]
                    scnt -= cnt
                    
            
            buy_cnt = math.floor(to_invest/price[idx])
            scnt += buy_cnt
            total_invested += buy_cnt * price[idx]
            value = scnt * price[idx]
            earn = value - total_invested + taken_money
            profit_rate = earn / total_invested * 100.0
            average = total_invested/scnt
            
            rates.append(profit_rate)
            dates.append(fdate[idx])
            sprices.append(price[idx])
            this_mon = tokens[1]
    
    
    if take_profit:
        print(f'{code} => data: {fdate[idx]} : buy:{buy_cnt} invested: {total_invested}  vaule: {value} ==>  earn: {earn}  rate: {profit_rate:.1f} today: {price[idx]} scnt: {scnt} taken: {taken_money}')
    else:
        print(f'{code} => data: {fdate[idx]} : buy:{buy_cnt} invested: {total_invested}  vaule: {value} ==>  earn: {earn}  rate: {profit_rate:.1f} today: {price[idx]} scnt: {scnt} ')
 

    
    return rates, dates, sprices
        
            
            




if __name__ == "__main__":
    
    #conn = hdb.connect_db("stock_all_by_210222.db")
    conn = hdb.connect_db("stock_all.db")

    #test_code_list = ['122630', '292150', '278540', '305540', '091160', '233740', '102110', '251350', '310970', '005930', '292150', '157490', '139250']
    #test_code_list = ['292150', '305720', '157490', '091160', '139250', '102970']
    test_code_list = ['292150', '305720', '157490', '139260']
    #test_code_list = ['122630']
       
    for c in test_code_list:
        valid, fdate, price = hdb.get_stock_data_from_db(conn, c)
        if valid:
            fig, ax1 = plt.subplots()
            #rates, dates, sprices = test_data(c, fdate, price, True)
            
            rates, dates, sprices = test_profit_2(c, fdate, price)
            dates = np.array(dates)
            max_x_lbls = 8
            test_cnt = len(dates)
            if test_cnt > max_x_lbls:
                x_interval = int(test_cnt/max_x_lbls)
                for i in range(len(dates)):
                    if i % x_interval != 0 and i != test_cnt -1:
                        dates[i] = ''
            plt.xticks(rotation=90)
            xs = np.linspace(0, test_cnt-1, test_cnt)
            plt.xticks(xs, dates)
            ax1.plot(rates, 'r')
            ax2 = ax1.twinx()
            ax2.plot(sprices, color='y')
            
            # rates, dates, sprices = test_data(c, fdate, price, False)
            # rates, dates, sprices = test_profit_2(c, fdate, price)
            # dates = np.array(dates)
            # max_x_lbls = 8
            # test_cnt = len(dates)
            # if test_cnt > max_x_lbls:
            #     x_interval = int(test_cnt/max_x_lbls)
            #     for i in range(len(dates)):
            #         if i % x_interval != 0 and i != test_cnt -1:
            #             dates[i] = ''
            # plt.xticks(rotation=90)
            # xs = np.linspace(0, test_cnt-1, test_cnt)
            # plt.xticks(xs, dates)
            # ax1.plot(rates, 'b')
            print('-'*100)
            
            plt.show()
        else:
            print(f'code {c} is not valid')
    conn.close()
 