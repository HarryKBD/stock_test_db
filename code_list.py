
my_code_list = ['140410', '302550', '251370', '064760', '036810', '005070', '278280', '298050', '009830', '306200', '327260',
        '218410', '099320', '001820', '009150', '066570', '012330', '102120', '036420', '005930']


my_code_list_t ={ 
        '140410' : 'MAJION',
        '302550' : 'RIMED', 
        '251370' : 'YMT ', 
        '064760' : 'TCK', 
        '036810' : 'SFT ', 
        '005070' : 'COSMO_NEW_MT', 
        '278280' : 'CHUNBO ', 
        '298050' : 'HYOSUNG_ADMT', 
        '009830' : 'HANHWA_SOL', 
        '306200' : 'SEA_STEEL ', 
        '327260' : 'METAL_LIFE',
        '218410' : 'RFHIC', 
        '099320' : 'SETREC_I', 
        '001820' : 'SAMHWA_CODENCER', 
        '009150' : 'SEC_MECA', 
        '066570' : 'LG_ELEC', 
        '012330' : 'H_MOBIS', 
        '036420' : 'J_CONTENTREE ',
        '005930' : 'SEC',
        '048260' : 'OSTEM_IMPL', #new 0125
        '336370' : 'SOLUS_ADMT', #new 0125
        '047810' : 'KOR_AIR_UNI', #new 0125
        '272210' : 'HANHWA_SYS',  #new 0125
        '012450' : 'HANHWA_AERO', #new 0125
        '051500' : 'CJ_FRESH' #new 0125
        }


#test code
if __name__ == "__main__":

    keys = my_code_list_t.keys()

    for k in keys:
        print(k)

