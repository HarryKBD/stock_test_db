



# -*- coding: utf-8 -*-
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

stock_file_name = 'DIS.csv' # 주가데이터 파일
#stock_file_name = '000880.KS.csv'
#stock_file_name = '005930.KS.csv'
filtered_name = 'clear_' + stock_file_name
encoding = 'euc-kr' # 문자 인코딩

#remove all null values
fd = open(stock_file_name, "rt")
new_fd = open(filtered_name, "wt")
for l in fd:
    if l.find('null') > 0:
        continue
    new_fd.write(l)
fd.close()
new_fd.close()
    

names = ['Date','Open','High','Low','Close','Adj Close','Volume']
raw_dataframe = pd.read_csv(filtered_name, names=names, encoding=encoding) #판다스이용 csv파일 로딩
raw_dataframe.info() # 데이터 정보 출력

#raw_dataframe = raw_dataframe[:3000]

full_date = raw_dataframe['Date']
del raw_dataframe['Date']

stock_info = raw_dataframe.values[1:].astype(np.float) # 금액&거래량 문자열을 부동소수점형으로 변환한다
full_date = np.array(full_date[1:])

# ['Open','High','Low','Close','Adj Close','Volume']에서 'Adj Close'까지 취함
price = stock_info[:,:-1]

y = price[:, -3]  #Close price

y = np.array(y)

plt.figure(2)
plt.plot(y, 'r')
buy = y[0]
earn = 0
last_max = y[0]
last_min = y[0]
plt.text(0, y[0], "B")
print("{}   Buy stock price: {}   earn: {}".format(full_date[0], str(buy), str(earn)))




for i in range(len(y)):
    if i == 0:
        continue
    today = y[i]
    if buy > 0:   #check if time to sell
        if today > last_max:
            last_max = today
            #print("{} Set last max at {} : {}".format(full_date[i], str(i), str(today)))
        sell_val = last_max * 0.9
        if today < sell_val: #Sell stock
            earn = earn + (today - buy)
            plt.text(i, today, "S")
            print("{}  Sell stock price: {}   earn: {}".format(full_date[i], str(today), str(earn)))
            buy = -1
            last_min = 999999999999999 #very big value
    else:   #check if time to buy
        if today < last_min:
            last_min = today
        buy_val = last_min * 1.1
        if today > buy_val:
            buy = today
            plt.text(i, today, "B")
            print("{}  Buy stock price: {}   earn: {}".format(full_date[i],str(today), str(earn)))
            last_max = today

print("initial {} ==> {}   earned: {}  {} % ".format(str(y[0]), str(today), str(earn), str(earn/y[0]*100)))
            
        

plt.xlabel('Time Period')
plt.ylabel('Stock Price')
plt.show()
        










