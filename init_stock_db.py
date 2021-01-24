

import FinanceDataReader as fdr
import hdb
import sys
import argparse
from datetime import datetime
from datetime import date
import happy
import korea_stocks_info


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
        



#from_date = datetime(2001, 1, 1)
#prepare_initial_table(conn, from_date)  #returns only 5 per query
#log_buy_stock(conn, '068270', 300000, 999)
#log_sell_stock(conn, '068270', 380000, 999)

if __name__ == "__main__":
    # append action allows to group repeating
    # options
    my_codes = korea_stocks_info.korea_stock_all
    #happy.code    
    
    parser = argparse.ArgumentParser()
       
    parser.add_argument('-c', '--code', dest='codes', required=True, action='append', 
        help="code")
    
    parser.add_argument('-t', '--to', dest='to_date', required=True, help="date to")
    parser.add_argument('-f', '--from', dest='from_date', required=True, help="date from")
    args = parser.parse_args()

#Date format 2021-01-01
    tokens = args.from_date.split("-")
    datef = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))

    tokens = args.to_date.split("-")
    datet = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))


    conn = hdb.connect_db("stock_all_by_210222.db")
    
    update_codes = args.codes

    if update_codes[0] == 'all':
        #process codes
        update_codes = my_codes
      
    print(f'updating db {datef}  {datet} with codes{update_codes}')       
    prepare_initial_table(conn, update_codes, datef, datet)
    
    
    conn.close()
 
        
        
        
        