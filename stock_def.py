# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 17:58:29 2021

@author: keybd
"""
from happy_utils import FORMAT_DATE

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


class StockTrackingResult:
    def __init__(self, code, category, added_date, base_price, origin, wanted, cnt, avg_price, name, max_date, max_price, todayp, today_rate):
        self.code = code
        self.category = category
        self.added_date = added_date
        self.base_price = base_price
        self.origin = origin
        self.wanted = wanted
        self.cnt = cnt
        self.avg_price = avg_price
        self.name = name
        self.max_date = max_date
        self.max_price = max_price
        self.todayp = todayp
        self.today_rate = today_rate
        
        self.base_rate = (self.todayp - self.base_price)/self.base_price * 100.0
        self.rate_max = (self.todayp - self.max_price)/self.max_price * 100.0
            
    def get_print_string(self):
    
        if self.cnt > 0:
            profit_rate = (self.todayp - self.avg_price)/self.avg_price*100.0

        str1 = "{7: <1} {11: <1} {0: <7} {1: <6} {2: <13} {3: <7.0f} {4: >4.1f} MAX:({9: <8}, {8: >4.0f} {10: >6.0f})=> BS [{5: <7.0f} {6: >4.0f}] ".format(
                self.category[:6], self.code, self.name, self.todayp, self.today_rate, self.base_price, self.base_rate, self.origin[0], self.rate_max, self.max_date[2:], self.max_price, self.wanted)

        str2 = "{0: <22} {1: <5}".format(" "*22, self.added_date[2:7], self.origin)
        if self.cnt > 0:
            str2 = "[{0: >7.0f} {1: <5.1f} ({2: >4})] {3: <5} ".format(self.avg_price, profit_rate, str(self.cnt), self.added_date[2:7], self.origin)

        return (str1 + str2)

