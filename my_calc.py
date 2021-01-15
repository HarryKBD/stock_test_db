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

# 표준화
def data_standardization(x):
    x_np = np.asarray(x)
    return (x_np - x_np.mean()) / x_np.std()
 
# Min-Max scaling
def min_max_scaling(x):
    x_np = np.asarray(x)
    return (x_np - x_np.min()) / (x_np.max() - x_np.min() + 1e-7) # 1e-7은 0으로 나누는 오류 예방차원
 
def reverse_min_max_scaling(org_x, x):
    org_x_np = np.asarray(org_x)
    x_np = np.asarray(x)
    return (x_np * (org_x_np.max() - org_x_np.min() + 1e-7)) + org_x_np.min()

# 하이퍼파라미터
input_data_column_cnt = 5  # 입력데이터의 컬럼 개수(Variable 개수)
output_data_column_cnt = 1 # 결과데이터의 컬럼 개수


lstm_cell_hidden_dim = 30   # 각 셀의 (hidden)출력 크기
forget_bias = 1.0          # 망각편향(기본값 1.0)
num_stacked_layers = 1     # stacked LSTM layers 개수
keep_prob = 1.0            # dropout할 때 keep할 비율

epoch_num = 1000           # 에폭 횟수(학습용전체데이터를 몇 회 반복해서 학습할 것인가 입력)
learning_rate = 0.01       # 학습률 (적당히 설정해놔야됨 여기서 적당히란...? )

# 데이터를 로딩한다.
#stock_file_name = 'DIS.csv' # 주가데이터 파일
stock_file_name = '000880.KS.csv'
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
del raw_dataframe['Adj Close']

stock_info = raw_dataframe.values[1:].astype(np.float) # 금액&거래량 문자열을 부동소수점형으로 변환한다
full_date = np.array(full_date[1:])
raw_dataframe.info() # 데이터 정보 출력



# ['Open','High','Low','Close','Adj Close','Volume']에서 'Adj Close'까지 취함
price = stock_info[:,:-1]
norm_price = min_max_scaling(price) # 가격형태 데이터 정규화 처리
print("price.shape: ", price.shape)
print("price[0]: ", price[0])
print("norm_price[0]: ", norm_price[0])
print("="*100) # 화면상 구분용

# ['Open','High','Low','Close','Adj Close','Volume']에서 마지막 'Volume'만 취함
# [:,-1]이 아닌 [:,-1:]이므로 주의하자! 스칼라가아닌 벡터값 산출해야만 쉽게 병합 가능
volume = stock_info[:,-1:]
norm_volume = min_max_scaling(volume) # 거래량형태 데이터 정규화 처리
print("volume.shape: ", volume.shape)
print("volume[0]: ", volume[0])
print("norm_volume[0]: ", norm_volume[0])
print("="*100) # 화면상 구분용

# 행은 그대로 두고 열을 우측에 붙여 합친다
x = np.concatenate((norm_price, norm_volume), axis=1) # axis=1, 세로로 합친다
print("x.shape: ", x.shape)
print("x[0]: ", x[0])    # x의 첫 값
print("x[-1]: ", x[-1])  # x의 마지막 값
print("="*100) # 화면상 구분용

y = x[:, [-2]] # 타켓은 주식 종가이다
print("y[0]: ",y[0])     # y의 첫 값
print("y[-1]: ",y[-1])   # y의 마지막 값





seq_length = 24            # 1개 시퀀스의 길이(시계열데이터 입력 개수)
delta = 0

dataX = [] # 입력으로 사용될 Sequence Data
dataY = [] # 출력(타켓)으로 사용
dataY_cur = []
dataY_date = []
for i in range(0, len(y) - seq_length - delta):
    xi = x[i : i+seq_length]
    yi = y[i + seq_length + delta] # 다음 나타날 주가(정답)
    y_curi = y[i + seq_length - 1]
    datei = full_date[i + seq_length - 1]
    dataX.append(xi) # dataX 리스트에 추가
    dataY.append(yi) # dataY 리스트에 추가
    dataY_cur.append(y_curi)
    dataY_date.append(datei)


train_percent = 0.8
train_size = int(len(dataY) * train_percent)
test_size = len(dataY) - train_size

trainX = np.array(dataX[0:train_size])
trainY = np.array(dataY[0:train_size])

testX = np.array(dataX[train_size:len(dataX)])
testY = np.array(dataY[train_size:len(dataY)])
testY_cur = np.array(dataY_cur[train_size:len(dataY_cur)])
testY_date = np.array(dataY_date[train_size:len(dataY_date)])


predict_date = np.array(full_date[train_size:len(dataY)])



print(trainX.shape)
# reshape input to be [samples, time steps, features]
trainX = np.reshape(trainX, (trainX.shape[0], 1, -1))
testX = np.reshape(testX, (testX.shape[0], 1, -1))
print(trainX.shape)


# create and fit the LSTM network, optimizer=adam, 25 neurons, dropout 0.1
# model = Sequential()
# model.add(LSTM(lstm_cell_hidden_dim, input_shape=(1, seq_length*input_data_column_cnt)))
# model.add(Dropout(0.1))
# model.add(Dense(1))
# model.compile(loss='mse', optimizer='adam')
# model.fit(trainX, trainY, epochs=1000, batch_size=seq_length*input_data_column_cnt, verbose=1)

#model.save('lstm_model1_1days') 
# model.save('lstm_model1_2days') 
#model.save('lstm_model1_5days') 
#model.save('lstm_model1_10days') 
# model.save('lstm_model100_066570') 
# #model.save('lstm_model2_005930') 

#model = tf.keras.models.load_model('lstm_model100_066570')
#model = tf.keras.models.load_model('lstm_model1_10days')
#model = tf.keras.models.load_model('lstm_model1_5days')
#model = tf.keras.models.load_model('lstm_model1_2days')
model = tf.keras.models.load_model('lstm_model1_1days')


# make predictions
trainPredict = model.predict(trainX)
testPredict = model.predict(testX)
print(trainPredict.shape)

# invert predictions
trainPredict = reverse_min_max_scaling(price, trainPredict)
trainY = reverse_min_max_scaling(price,trainY)
testPredict = reverse_min_max_scaling(price, testPredict)
testY = reverse_min_max_scaling(price, testY)

testY_cur = reverse_min_max_scaling(price, testY_cur)

# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(trainY, trainPredict))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(testY, testPredict))
print('Test Score: %.2f RMSE' % (testScore))

plt.figure(2)
#plt.xlim(0,200)
#plt.ylim(16,24)
#plt.plot(trainY, 'y')
#plt.plot(trainPredict, 'g')
#plt.plot(testY_cur, "y")
plt.plot(testY, 'r')
plt.plot(testPredict, 'b')
#plt.plot(price[:,3], 'b')

plt.xlabel('Time Period')
plt.ylabel('Stock Price')
plt.show()

print(len(predict_date))
max_gap = 0
#[date, cur_price, estimated, actual, gap]
#result_list = np.array([[testY_date[0], 0, 0, 0, 0]])

print(type(testPredict[0][0]))
result_list = np.array([[testY_date[0], testY_cur[0][0], testPredict[0][0], testY[0][0], abs(testPredict[0][0] - testY[0][0])]])

err_cnt = 0
diff_predict = testY_cur[0][0] - testPredict[0][0]
diff_real = testY_cur[0][0] - testY[0][0]

if diff_predict < 0 and diff_real > 0:
    err_cnt = err_cnt + 1
total = 1
for i in range(len(testY_date)):
    if i == 0:
        continue
    total = total + 1
    #print("Date: {}  curr {} , 10 business days Later: {}  ==> Actual:  {}".format(
    #    testY_date[i], testY_cur[i], testPredict[i], testY[i]))
    aa = np.array([[testY_date[i], testY_cur[i][0], testPredict[i][0], testY[i][0], abs(testPredict[i][0] - testY[i][0])]])
    #print(type(aa))
    #result_list[0] = [testY_date[i], testY_cur[i][0], testPredict[i][0], testY[i][0], abs(testPredict[i][0] - testY[i][0])]
    #np.append(result_list, [[testY_date[i], testY_cur[i][0], testPredict[i][0], testY[i][0], abs(testPredict[i][0] - testY[i][0])]], axis = 0)
    #np.append(result_list, aa, 0)
    diff_predict = testY_cur[i][0] - testPredict[i][0]
    diff_real = testY_cur[i][0] - testY[i][0]

    if diff_predict < 0 and diff_real > 0:
        err_cnt = err_cnt + 1
    result_list = np.concatenate((result_list, aa), 0)
    if max_gap < abs(testY_cur[i] - testY[i]):
        max_gap = abs(testY_cur[i] - testY[i])
        max_date = testY_date[i]
    
print("err cnt : {} / {}".format(str(err_cnt), str(total)))
















