import FinanceDataReader as fdr
import hdb
import sys
import argparse
from datetime import datetime
from datetime import date
import happy
import korea_stocks_info
import code_list


FORMAT_DATE = '%Y-%m-%d'

def prepare_initial_table(conn, code_list, date_from, date_to):
    edate_str = date_to.strftime(FORMAT_DATE)

    sdate_str = date_from.strftime(FORMAT_DATE)

    print("{} from  ==> {} to".format(sdate_str, edate_str))
    cnt = 1
    for code in code_list:
        result_list = happy.get_stock_data_from_server(code, date_from, date_to)
        hdb.insert_stock_data(conn, result_list)
        print("Getting {} data:  {} / {} ==> cnt: {}".format(code, str(cnt), str(len(code_list)), str(len(result_list))))
        cnt += 1

    #op 1: 'BUY'  2: 'SELL'

#python init_stock_db -c 283782 -c 283728


#my_codes = ['140410', '302550', '251370', '064760', '036810', '005070', '278280', '298050', '009830', '306200', '327260',
        #'218410', '099320', '001820', '009150', '066570', '012330', '102120', '036420', '005930']
        

def init_target_list(conn):
    hdb.create_target_list_table(conn)
    hdb.insert_target_list(conn, 'Health', '048260', 36500, '2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Space', '047810', 23700, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Airplaine', '067390', 5430, '2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Travel','080160', 16450, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Food system', '051500', 18850,'2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Battery','247540', 55000,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Battery','020150', 42150,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Battery','243840', 39500,'2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Battery','131390', 11000,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Battery','079810', 9500,'2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Battery','137400', 6470,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Battery/OLED', '161580', 14200,'2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, '4th','086960', 15650, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Green','009450', 55300,'2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'IT material', '178920', 29300,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Electric Medicine', '302550', 26000,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Health','054950', 35500, '2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'OLED', '347770', 16800,'2021-01-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Consumer', '036670', 9780, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Ship', '010620', 49500, '2021-02-02', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Ship', '010140', 6480,'2021-02-02', 'Dang')
    hdb.insert_target_list(conn, 'Ship', '042660', 26600,'2021-02-02', 'Dang')
    hdb.insert_target_list(conn, 'LNG/H','033500', 11000,'2021-02-02', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'LNG Parts', '013030', 14950, '2021-02-02', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Shipping','028670', 4110, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Shipping','044450', 10300, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Food system','051160', 11700, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Semiconductor','140860', 50400, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Semiconductor','083450', 20100, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, '5G','050890', 11050, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, '5G','039560', 12500, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, '5G','032640', 12100, '2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'China/Food','222040', 8150, '2021-03-01', 'Dang')
    hdb.insert_target_list(conn, 'IT material', '009150', 219000, '2020-01-01', 'Jiho')
    
    hdb.insert_target_list(conn, 'IT material', '272210', 18050, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Battery', '298000', 218500, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Space', '298050', 297816, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'IT material', '064760', 147300, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Space', '099320', 66934, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Medical', '140410', 176897, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Battery', '251370', 21900, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Battery', '327260', 32507, '2020-01-01', 'Jiho')                           

    #ETF
    hdb.insert_target_list(conn, 'ETF', '133690', 66939, '2020-02-01', 'ETF')                           
    hdb.insert_target_list(conn, 'ETF', '157490', 17185, '2020-02-01', 'ETF')                           
    hdb.insert_target_list(conn, 'ETF', '251350', 17259, '2020-02-01', 'ETF')                           
    hdb.insert_target_list(conn, 'ETF', '292150', 15227, '2020-02-01', 'ETF')                           
    hdb.insert_target_list(conn, 'ETF', '305720', 19944, '2020-02-01', 'ETF')                           
    hdb.insert_target_list(conn, 'ETF', '314250', 28680, '2020-02-01', 'ETF')                           
    
def init_current_stock(conn):
    hdb.create_current_stock_table(conn)
    hdb.insert_current_stock(conn, '009150', 219000, 92)
    hdb.insert_current_stock(conn, '009450', 49124, 204)
    hdb.insert_current_stock(conn, '010140', 6380, 782)
    hdb.insert_current_stock(conn, '010620', 57690, 187)
    hdb.insert_current_stock(conn, '047810', 34500, 581)
    hdb.insert_current_stock(conn, '272210', 18050, 1111)
    hdb.insert_current_stock(conn, '298000', 218500, 91)
    hdb.insert_current_stock(conn, '298050', 297816, 139)
    hdb.insert_current_stock(conn, '033500', 11905, 557)
    hdb.insert_current_stock(conn, '048260', 64958, 398)
    hdb.insert_current_stock(conn, '064760', 147300, 133)
    hdb.insert_current_stock(conn, '099320', 66934, 583)
    hdb.insert_current_stock(conn, '102940', 18300, 143)
    hdb.insert_current_stock(conn, '140410', 176897, 133)
    hdb.insert_current_stock(conn, '251370', 21900, 913)
    hdb.insert_current_stock(conn, '302550', 30897, 647)
    hdb.insert_current_stock(conn, '013030', 14700, 941)

    hdb.insert_current_stock(conn, '133690', 66939, 22)
    hdb.insert_current_stock(conn, '157490', 17185, 86)                           
    hdb.insert_current_stock(conn, '251350', 17259, 86)                           
    hdb.insert_current_stock(conn, '292150', 15227, 104)                           
    hdb.insert_current_stock(conn, '305720', 19944, 74)                           
    hdb.insert_current_stock(conn, '314250', 28680, 52)                           


    
    

#from_date = datetime(2001, 1, 1)
#prepare_initial_table(conn, from_date)  #returns only 5 per query
#log_buy_stock(conn, '068270', 300000, 999)
#log_sell_stock(conn, '068270', 380000, 999)

if __name__ == "__main__":
    # append action allows to group repeating
    # options
    #my_codes = korea_stocks_info.korea_stock_all
    #my_codes = code_list.my_code_list
    #my_codes = code_list.my_code_list_t.keys()
    #my_codes = korea_stocks_info.korea_stock_etf

#insert or replace into stock_basic_info(code, name_kor, name_eng, market_type) values ('133690', 'ETFTiNasd', 'ETFTiNasd', 'ETF');
#insert or replace into stock_basic_info(code, name_kor, name_eng, market_type) values ('157490', 'ETFTiSoft', 'ETFTiSoft', 'ETF');
#insert or replace into stock_basic_info(code, name_kor, name_eng, market_type) values ('251350', 'ETFKoMSCI', 'ETFKoMSCI', 'ETF');
#insert or replace into stock_basic_info(code, name_kor, name_eng, market_type) values ('292150', 'ETFTiTop10', 'ETFTiTop10', 'ETF');
#insert or replace into stock_basic_info(code, name_kor, name_eng, market_type) values ('305720', 'ETFKoBattery', 'ETFKoBattery', 'ETF');
#insert or replace into stock_basic_info(code, name_kor, name_eng, market_type) values ('314250', 'ETFKoUsFangP', 'ETFKoUsFangP', 'ETF');

#delete from stock_basic_info WHERE code='133690';
#delete from stock_basic_info WHERE code='157490';
#delete from stock_basic_info WHERE code='251350';
#delete from stock_basic_info WHERE code='292150';
#delete from stock_basic_info WHERE code='305720';
#delete from stock_basic_info WHERE code='314250';



    
   
#     parser = argparse.ArgumentParser()
       
#     parser.add_argument('-c', '--code', dest='codes', required=True, action='append', 
#         help="code")

#     parser.add_argument('-f', '--from', dest='from_date', required=True, help="date from")    
#     parser.add_argument('-t', '--to', dest='to_date', required=True, help="date to")
#     args = parser.parse_args()

# #Date format 2021-01-01
#     tokens = args.from_date.split("-")
#     datef = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))

#     tokens = args.to_date.split("-")
#     datet = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))

    conn = hdb.connect_db("stock_all.db")
    #hdb.init_stock_basic_info_table(conn, 'stock_basic_info_20210307.csv')
    #print(hdb.get_stock_names(conn, '015860'))
    
    
    ##################To fill the stock price list use this block##############################
    my_codes = hdb.get_stock_code_list_interested(conn)
    tokens = '2021-01-01'.split("-")
    datef = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
    tokens ='2021-03-18'.split("-")
    datet = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
    prepare_initial_table(conn, my_codes, datef, datet)
    ###########################################################################################
    
    ###################### To init the list of the stocks interested ##########################
    #init_target_list(conn)
    ################################################################################################
    
    
    #######################  To init the current list of the stockes owned by me ######################
    #init_current_stock(conn)
    ###################################################################################################
    
    # update_codes = args.codes


    # if update_codes[0] == 'codelist':
    #     # 한국거래소 상장종목 전체
    #     df_krx = fdr.StockListing('KRX')
    #     print(df_krx.head())
    # else:
    #     if update_codes[0] == 'all':
    #         #process codes
    #         update_codes = my_codes
      
    #     print(f'updating db {datef}  {datet} with codes{update_codes}')       
    #     prepare_initial_table(conn, update_codes, datef, datet)
    
    conn.close()
 
        
        
        
        
