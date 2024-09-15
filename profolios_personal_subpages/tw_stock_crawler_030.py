#%%
# 基本面_財報分析 
#%%

import requests
from bs4 import BeautifulSoup
import os
import re
from fake_useragent import UserAgent
from io import StringIO
import json
import pandas as pd
import numpy as np
import datetime, time, random
import random
import sqlite3
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px



#%%
# 上市
# 每日股價爬蟲
# 所有資料，存進sqlite
# 寫成function
# 最多五次


def daily_price(date):
    url = f'https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={date}&type=ALLBUT0999&response=json&_=1706840905505'
    
    # 生成隨機的使用者代理
    ua = UserAgent()
    user_agent = ua.random

    # headers 數據
    headers = {
        'User-Agent': user_agent,
    }

    max_retries = 5  # 最大重試次數
    current_retry = 0

    while current_retry < max_retries:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 如果伺服器回傳錯誤碼，拋出異常
            break  # 如果成功，跳出迴圈
        except requests.exceptions.RequestException as e:
            print(f'Error connecting to the server: {e}')
            current_retry += 1
            if current_retry < max_retries:
                print(f'Retrying... ({current_retry}/{max_retries})')
                time.sleep(5 + random.uniform(0, 5)) 
            else:
                print('Max retries reached. Exiting.')
                raise  # 如果重試次數用完仍然失敗，拋出異常

    response_data = json.loads(response.text)
    ninth_title_fields = response_data["tables"][8]["fields"]
    ninth_title_data = response_data["tables"][8]["data"]
    df = pd.DataFrame(ninth_title_data, columns=ninth_title_fields)
    
    df["漲跌(+/-)"] = df["漲跌(+/-)"].apply(lambda x: re.search(r'[-+]', x).group() if re.search(r'[-+]', x) else None)
    
    # 
    df = df.apply(lambda col: col.apply(lambda x: x.replace(',', '') if isinstance(x, str) else x))

    # 
    numeric_columns = ['成交股數', '成交筆數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '最後揭示買價', '最後揭示買量', '最後揭示賣價', '最後揭示賣量', '本益比']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    # 
    string_columns = ['證券代號','證券名稱', '漲跌(+/-)']
    df[string_columns] = df[string_columns].astype(str)
    
    # 要存sqlite，不能使用 multiIndex
    # df = df.set_index(['證券代號','證券名稱'])
    
    return df

# daily_price('20230303')




#%%
# 上市
# 所有資料，存進sqlite 單一table
# 改成可選日期範圍 
# strftime('%Y%m%d') 方法，格式化字串


def store_daily_price_to_sqlite(start_date, end_date):
    db_file = r'G:\我的雲端硬碟\000-AI\py\18-STOCK\tw_financial_reports\daily_price.db'
    
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        conn.close()

    conn = sqlite3.connect(db_file)
    
    cur = conn.cursor()
    
    start_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
    
    current_dt = start_dt
    
    while current_dt <= end_dt:
        current_date_str = current_dt.strftime('%Y%m%d')
        table_name = f'daily_price_2019'  # _{current_date_str}
        
        try:
            df = daily_price(current_date_str)
            df['日期'] = current_date_str 
            df.to_sql(table_name, conn, if_exists='append', index=False)
            print(f'Successfully stored data for {current_date_str} into table {table_name}')
        except Exception as e:
            print(f'Error storing data for {current_date_str}: {e}')
        
        time.sleep(5 + random.uniform(0, 5))
        current_dt += datetime.timedelta(days=1)
    
    conn.close()

# 
# start_date = '20190204'
# end_date = '20240303'
# store_daily_price_to_sqlite(start_date, end_date)




#%%
# 上櫃
# 每日股價爬蟲
# 所有資料，存進sqlite
# 寫成function
# 最多五次



def daily_price_otc(date):
    
    year_w = date[:4] 
    year = int(year_w) - 1911
    month = date[4:6]
    day = date[6:8]
    url = f'https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d={year}/{month}/{day}&se=EW&_=1710149320138'

    # 
    ua = UserAgent()
    user_agent = ua.random

    # 
    headers = {
        'User-Agent': user_agent,
    }

    max_retries = 5 
    current_retry = 0

    while current_retry < max_retries:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()   
            break  
        except requests.exceptions.RequestException as e:
            print(f'Error connecting to the server: {e}')
            current_retry += 1
            if current_retry < max_retries:
                print(f'Retrying... ({current_retry}/{max_retries})')
                time.sleep(5 + random.uniform(0, 5))  
            else:
                print('Max retries reached. Exiting.')
                raise   

    response_data = json.loads(response.text)

    aa_data = response_data.get('aaData', [])

    selected_columns = [
        '公司代號', '公司名稱', '收盤價', '漲跌', '開盤價', '最高價', '最低價', 
        '成交股數', '成交金額', '成交筆數', '最後揭示買價', '最後揭示買量', '最後揭示賣價','最後揭示賣量',
        '發行股數', '次日漲停價', '次日跌停價'
    ]

    df = pd.DataFrame(aa_data, columns=selected_columns)
    df.rename(columns={'公司名稱': '證券名稱'}, inplace=True)
    df.rename(columns={'公司代號': '證券代號'}, inplace=True)
    
    df['收盤價'] = pd.to_numeric(df['收盤價'], errors='coerce')
    df['開盤價'] = pd.to_numeric(df['開盤價'], errors='coerce')
    df['收盤價'] = df['收盤價'].astype(float)
    df['開盤價'] = df['開盤價'].astype(float)
    df['漲跌價差'] = round(df['收盤價'] - df['開盤價'], 2)
    
    df['漲跌(+/-)'] = df['漲跌價差'].apply(lambda x: '-' if x < 0 else '+')
    df['漲跌價差'] = abs(df['漲跌價差'])

    return df 



# date = '20240103'
# daily_price_otc(date)





#%%
# 上櫃
# 所有資料，存進sqlite 單一table
# 改成可選日期範圍 
# strftime('%Y%m%d') 方法，格式化字串


def store_daily_price_otc_to_sqlite(start_date, end_date):
    db_file = r'G:\我的雲端硬碟\000-AI\py\18-STOCK\tw_financial_reports\daily_price_otc.db'
    
    # if not os.path.exists(db_file):
    #     conn = sqlite3.connect(db_file)
    #     conn.close()

    conn = sqlite3.connect(db_file)
    
    cur = conn.cursor()
    
    start_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
    
    current_dt = start_dt
    
    while current_dt <= end_dt:
        current_date_str = current_dt.strftime('%Y%m%d')
        table_name = f'daily_price_otc_2021'  # _{current_date_str}
        
        try:
            df = daily_price_otc(current_date_str)
            df['日期'] = current_date_str 
            df.to_sql(table_name, conn, if_exists='append', index=False)
            print(f'Successfully stored data for {current_date_str} into table {table_name}')
        except Exception as e:
            print(f'Error storing data for {current_date_str}: {e}')
        
        time.sleep(5 + random.uniform(0, 5))
        current_dt += datetime.timedelta(days=1)
    
    conn.close()

#  
# start_date = '20190101'
# end_date = '20240314'
# store_daily_price_otc_to_sqlite(start_date, end_date)






#%%
# 上市+上櫃
# 月報爬蟲
# 單一年月
# 迴圈印出所有產業別
# 包成def 
# 加上提取欄位['年']、['月']



def get_monthly_report(year, month):
    # 上市
    url = f'https://mops.twse.com.tw/nas/t21/sii/t21sc03_{year}_{month}_0.html'
    # 上櫃
    # url = f'https://mops.twse.com.tw/nas/t21/otc/t21sc03_{year}_{quarter}_0.html'
    
    # 生成隨機的使用者代理
    ua = UserAgent()
    user_agent = ua.random

    # headers 數據
    headers = {
        'User-Agent': user_agent,
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = 'big5'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 迴圈印出全部產業別
    table_index_list = range(len(soup.find_all('th', class_='tt', align='left')))
    all_dfs = []

    for table_index in table_index_list:
        # 產業別
        industry_title_element = soup.find_all('th', class_='tt', align='left')[table_index]
        industry_title = industry_title_element.get_text(strip=True) if industry_title_element else None

        # 表格
        data_table_element = soup.find_all('td', colspan='2')[table_index]
        data_table_html = str(data_table_element)
        
        # 使用StringIO包裝HTML字符串
        data_table_io = StringIO(data_table_html)
        df = pd.read_html(data_table_io, encoding='big5')[0]
        
        # 更改column名稱
        df.columns = df.columns.get_level_values(1)
        df = df.rename(columns={'公司 代號': '公司代號'})

        # 轉成數字(之後做計算)
        numeric_columns = ['當月營收', '上月營收', '去年當月營收', '上月比較 增減(%)', '去年同月 增減(%)', '當月累計營收', '去年累計營收', '前期比較 增減(%)']
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

        # 備註放上產業別
        df['備註'] = industry_title 
        
        if url.startswith('https://mops.twse.com.tw/nas/t21/sii'):
            df['上市櫃'] = '上市' 
        elif url.startswith('https://mops.twse.com.tw/nas/t21/otc'):
            df['上市櫃'] = '上櫃' 


        df['年份'] = f'{year}'
        df['月份'] = f'{month}'
        
        # 當月營收中，NaN 的整行刪除
        df = df[~df['當月營收'].isnull()]

        # 刪除「公司代號」中出現「合計」的行數
        df = df[df['公司代號'] != '合計']

        # 「公司代號」、「公司名稱」列為 indexes
        # df = df.set_index(['公司代號', '公司名稱'])

        all_dfs.append(df)

    # 所有的 df 合併
    final_df = pd.concat(all_dfs)

    return final_df

#
# year = '111'
# month = '2'
# final_df = get_monthly_report(year, month)
# final_df



#%%
# 上市+上櫃
# 月報爬蟲
# 可選日期範圍
# 迴圈印出所有產業別
# 存進sqlite 單一table



def store_monthly_report_to_sqlite(start_date, end_date):
    db_file = r'G:\我的雲端硬碟\000-AI\py\18-STOCK\tw_financial_reports\monthly_report.db'
    conn = sqlite3.connect(db_file)

    start_year = start_date[:4]
    start_month = str(int(start_date[4:6])) if start_date[4] != '0' else start_date[5]
    end_year = end_date[:4]
    end_month = str(int(end_date[4:6])) if end_date[4] != '0' else end_date[5]
    
    current_year = int(start_year) - 1911
    current_month = int(start_month)
    end_year = int(end_year) - 1911

    # 數據類型
    column_types = {
        '公司代號': 'TEXT',
        '公司名稱': 'TEXT',
        '當月營收': 'REAL',
        '上月營收': 'REAL',
        '去年當月營收': 'REAL',
        '上月比較 增減(%)': 'REAL',
        '去年同月 增減(%)': 'REAL',
        '當月累計營收': 'REAL',
        '去年累計營收': 'REAL',
        '前期比較 增減(%)': 'REAL',
        '備註': 'TEXT',
        '年份': 'TEXT',
        '月份': 'TEXT',
    }
    
    while current_year <= int(end_year):
        while (current_year < int(end_year) and current_month <= 12) or (current_year == int(end_year) and current_month <= int(end_month)):
                                                                         
            try:
                final_df = get_monthly_report(current_year, current_month)
                table_name = f'monthly_report_2019'
                final_df.to_sql(table_name, conn, if_exists='append', index=False, dtype=column_types)
                print(f'Successfully stored data for {current_year}-{current_month} into table {table_name}')
            
            except Exception as e:
                    print(f'Error storing data for {current_year}-{current_month}: {e}')
                    
            time.sleep(5 + random.uniform(0, 5))
            
            current_month += 1
            
            if current_month > 12:
                current_year += 1
                current_month = 1
        
        current_year += 1
            
    conn.close()

# 
# start_date = '20190101'
# end_date = '20240230'
# store_monthly_report_to_sqlite(start_date, end_date)




#%%
# 季報爬蟲
# 資產負債表，包成def 
# random header
# 有的季度會有備註，最上面會多一個表格，需要改抓def[2]
# 有的公司會多兩欄，前一年度-01-10 資料
# 金融保險業較特殊，會需要改payload


def get_bs_data(stock_code, year, quarter): 
    url = 'https://mops.twse.com.tw/mops/web/ajax_t164sb03'

    ua = UserAgent()
    user_agent = ua.random

    headers = {
        'User-Agent': user_agent,
    }
    
    # payload 數據
    payload = {
        'encodeURIComponent': '1',
        'step': '1',
        'firstin': '1',
        'off': '1',
        'keyword4': '',
        'code1': '',
        'TYPEK2': '',
        'checkbtn': '',
        'queryName': 'co_id',
        'inpuType': 'co_id',
        'TYPEK': 'all',
        'isnew': 'false',
        'co_id': stock_code,  
        'year': year,    
        'season': quarter   
    }

    response = requests.post(url, data=payload, headers=headers)

    # if response.status_code == 200:
    #     next
    # else:
    #     print(f'Error: {response.status_code}')

    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return pd.DataFrame()   
    
    dfs = pd.read_html(StringIO(response.text))
    print(len(dfs))
        
    try:
        # dfs[1] 
        df_bs = dfs[1]
        df_bs = df_bs.reset_index(drop=True)
        
        df_bs = df_bs.iloc[:, :-2]
        prev_year = str(int(year) - 1)

        if quarter == '01':
            month_date = '03-31'
        elif quarter == '02':
            month_date = '06-30'
        elif quarter == '03':
            month_date = '09-30'
        elif quarter == '04':
            month_date = '12-31'

        if quarter in ('01', '02', '03' ):
            try:
                df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)', 
                                f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)']
            except:
                df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)', 
                        f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)', f'{prev_year}-01-10 金額', f'{prev_year}-01-10 (%)']
                print(f'two columns more')
        else:
            try:
                df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)']
            except:
                df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)',
                        f'{prev_year}-01-10 金額', f'{prev_year}-01-10 (%)']
                print(f'two columns more')

        df_bs.set_index('會計項目', inplace=True)
        
        return df_bs
    
    
    except (ValueError, IndexError):
        try:
            print(f' Trying alternative source (dfs[2])...') # 若抓取失敗，改使用 dfs[2]
            df_bs = dfs[2]
            df_bs = df_bs.reset_index(drop=True)

            df_bs = df_bs.iloc[:, :-2]
            prev_year = str(int(year) - 1)

            if quarter == '01':
                month_date = '03-31'
            elif quarter == '02':
                month_date = '06-30'
            elif quarter == '03':
                month_date = '09-30'
            elif quarter == '04':
                month_date = '12-31'

            if quarter in ('01', '02', '03' ):
                try:
                    df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)', 
                                    f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)']
                except:
                    df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)', 
                            f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)', f'{prev_year}-01-10 金額', f'{prev_year}-01-10 (%)']
                    print(f'two columns more')
            else:
                try:
                    df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)']
                except:
                    df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)',
                            f'{prev_year}-01-10 金額', f'{prev_year}-01-10 (%)']
                    print(f'two columns more')
            
            
            df_bs.set_index('會計項目', inplace=True)
            
            return df_bs
    
        except:
            print(f'Payload for financial industry...') # 若抓取失敗，可能是金融保險業，payload 不一樣

            # 要更改的 payload 數據
            payload = {
            'encodeURIComponent': '1',
            'id': '',
            'key': '',
            'TYPEK': 'sii',
            'step': '2',
            'year': year,
            'season': quarter,
            'co_id': stock_code,
            'firstin': '1',
            }

            response = requests.post(url, data=payload, headers=headers)
            
            if response.status_code != 200:
                print(f'Error: {response.status_code}')
                return pd.DataFrame()   

            # dfs[1] 
            dfs = pd.read_html(StringIO(response.text))
            df_bs = dfs[1]
            df_bs = df_bs.reset_index(drop=True)
            
            df_bs = df_bs.iloc[:, :-2]
            prev_year = str(int(year) - 1)

            if quarter == '01':
                month_date = '03-31'
            elif quarter == '02':
                month_date = '06-30'
            elif quarter == '03':
                month_date = '09-30'
            elif quarter == '04':
                month_date = '12-31'

            if quarter in ('01', '02', '03' ):
                try:
                    df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)', 
                                    f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)']
                except:
                    df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)', 
                            f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)', f'{prev_year}-01-10 金額', f'{prev_year}-01-10 (%)']
                    print(f'two columns more')
            else:
                try:
                    df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)']
                except:
                    df_bs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-12-31 金額', f'{prev_year}-12-31 (%)',
                            f'{prev_year}-01-10 金額', f'{prev_year}-01-10 (%)']
                    print(f'two columns more')

            df_bs.set_index('會計項目', inplace=True)
            
            return df_bs
        
  
            
# 
# stock_code = '2889'
# year = '111'
# quarter = '04'
# df = get_bs_data(stock_code, year, quarter)
# df







#%%

# 綜合損益表
# 優化＿2
# random header
# 有的季度會有備註，最上面會多一個表格，需要改抓def[2]
# 有的公司上市前，會傳Q2(上半年) Q4(下半年)
# 金融保險業較特殊，會需要改payload


def get_is_data(stock_code, year, quarter):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t164sb04'
    

    ua = UserAgent()
    user_agent = ua.random


    headers = {
        'User-Agent': user_agent,
    }

    # payload data
    payload = {
        'encodeURIComponent': '1',
        'step': '1',
        'firstin': '1',
        'off': '1',
        'keyword4': '',
        'code1': '',
        'TYPEK2': '',
        'checkbtn': '',
        'queryName': 'co_id',
        'inpuType': 'co_id',
        'TYPEK': 'all',
        'isnew': 'false',
        'co_id': stock_code,  
        'year': year,    
        'season': quarter   
    }


    with requests.Session() as session:
        response = session.post(url, data=payload, headers=headers)
        
    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return pd.DataFrame()  

    # parse HTML table
    dfs = pd.read_html(StringIO(response.text))
    
    try:
        # dfs[1] 
        df_is = dfs[1]
    
        # df_is.columns = df_is.columns.droplevel(level=[0, 1])
        df_is = df_is.reset_index(drop=True)
        df_is = df_is.iloc[:, :-1]
        prev_year = str(int(year) - 1)

        if quarter == '01':
            month_date = '01-01 ~ 03-31'
        elif quarter == '02':
            quarter_pl = 'Q2'
            month_date = '01-01 ~ 06-30'
        elif quarter == '03':
            quarter_pl = 'Q3'
            month_date = '01-01 ~ 09-30'
        elif quarter == '04':
            year = year
            prev_year = str(int(year) - 1)

        if quarter == '01':
            df_is.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)']

        elif quarter in ('02', '03' ):
            try:
                df_is.columns = ['會計項目', f'{year}-{quarter_pl} 金額', f'{year}-{quarter_pl} (%)', f'{prev_year}-{quarter_pl} 金額', f'{prev_year}-{quarter_pl} (%)',
                            f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)']
            except:
                df_is.columns = ['會計項目', f'{year} 上半年度 金額', f'{year} 上半年度 (%)', f'{prev_year} 下半年度 金額', f'{prev_year} 下半年度 (%)']
        else:
            df_is.columns = ['會計項目', f'{year}年度 金額', f'{year}年度 (%)', f'{prev_year}年度 金額', f'{prev_year}年度 (%)']
            
        df_is = df_is.set_index('會計項目')    

        return df_is
    
    except (ValueError, IndexError):
        try:
            print(f' Trying alternative source (dfs[2])...') # 若抓取失敗，改使用 dfs[2]
            df_is = dfs[2]
        
            # df_is.columns = df_is.columns.droplevel(level=[0, 1])
            df_is = df_is.reset_index(drop=True)
            df_is = df_is.iloc[:, :-1]
            prev_year = str(int(year) - 1)

            if quarter == '01':
                month_date = '01-01 ~ 03-31'
            elif quarter == '02':
                quarter_pl = 'Q2'
                month_date = '01-01 ~ 06-30'
            elif quarter == '03':
                quarter_pl = 'Q3'
                month_date = '01-01 ~ 09-30'
            elif quarter == '04':
                year = year
                prev_year = str(int(year) - 1)


            if quarter == '01':
                df_is.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)']

            elif quarter in ('02', '03' ):
                try:
                    df_is.columns = ['會計項目', f'{year}-{quarter_pl} 金額', f'{year}-{quarter_pl} (%)', f'{prev_year}-{quarter_pl} 金額', f'{prev_year}-{quarter_pl} (%)',
                                f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)']
                except:
                    df_is.columns = ['會計項目', f'{year} 上半年度 金額', f'{year} 上半年度 (%)', f'{prev_year} 下半年度 金額', f'{prev_year} 下半年度 (%)']
            else:
                df_is.columns = ['會計項目', f'{year}年度 金額', f'{year}年度 (%)', f'{prev_year}年度 金額', f'{prev_year}年度 (%)']
                
            df_is = df_is.set_index('會計項目')

            return df_is

        except:
            print(f'Payload for financial industry...') # 若抓取失敗，可能是金融保險業，payload 不一樣
            
            # 要更改的 payload 數據
            payload = {
            'encodeURIComponent': '1',
            'id': '',
            'key': '',
            'TYPEK': 'sii',
            'step': '2',
            'year': year,
            'season': quarter,
            'co_id': stock_code,
            'firstin': '1',
            }

            response = requests.post(url, data=payload, headers=headers)

            # if response.status_code == 200:
            #     next
            # else:
            #     print(f'Error: {response.status_code}')
            
            if response.status_code != 200:
                print(f'Error: {response.status_code}')
                return pd.DataFrame()   
            
            dfs = pd.read_html(StringIO(response.text))
            # dfs[1] 
            df_is = dfs[1]
        
            # df_is.columns = df_is.columns.droplevel(level=[0, 1])
            df_is = df_is.reset_index(drop=True)
            df_is = df_is.iloc[:, :-1]
            prev_year = str(int(year) - 1)

            if quarter == '01':
                month_date = '01-01 ~ 03-31'
            elif quarter == '02':
                quarter_pl = 'Q2'
                month_date = '01-01 ~ 06-30'
            elif quarter == '03':
                quarter_pl = 'Q3'
                month_date = '01-01 ~ 09-30'
            elif quarter == '04':
                year = year
                prev_year = str(int(year) - 1)

            if quarter == '01':
                df_is.columns = ['會計項目', f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)']

            elif quarter in ('02', '03' ):
                try:
                    df_is.columns = ['會計項目', f'{year}-{quarter_pl} 金額', f'{year}-{quarter_pl} (%)', f'{prev_year}-{quarter_pl} 金額', f'{prev_year}-{quarter_pl} (%)',
                                f'{year}-{month_date} 金額', f'{year}-{month_date} (%)', f'{prev_year}-{month_date} 金額', f'{prev_year}-{month_date} (%)']
                except:
                    df_is.columns = ['會計項目', f'{year} 上半年度 金額', f'{year} 上半年度 (%)', f'{prev_year} 下半年度 金額', f'{prev_year} 下半年度 (%)']
            else:
                df_is.columns = ['會計項目', f'{year}年度 金額', f'{year}年度 (%)', f'{prev_year}年度 金額', f'{prev_year}年度 (%)']
                
            df_is = df_is.set_index('會計項目')    

            return df_is
            
            
            
            
# 
# stock_code = '2801'
# year = '111'
# quarter = '02'
# get_is_data(stock_code, year, quarter)





#%%
# 現金流量表
# 包成def
# random header
# 有的季度會有備註，最上面會多一個表格，需要改抓def[2]
# 金融保險業較特殊，會需要改payload


def get_cfs_data(stock_code, year, quarter):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t164sb05'

    ua = UserAgent()
    user_agent = ua.random

    # headers 數據
    headers = {
        'User-Agent': user_agent,
    }
    
    # payload data
    payload = {
        'encodeURIComponent': '1',
        'step': '1',
        'firstin': '1',
        'off': '1',
        'keyword4': '',
        'code1': '',
        'TYPEK2': '',
        'checkbtn': '',
        'queryName': 'co_id',
        'inpuType': 'co_id',
        'TYPEK': 'all',
        'isnew': 'false',
        'co_id': stock_code,  
        'year': year,    
        'season': quarter   
    }

    response = requests.post(url, data=payload, headers=headers)

    # if response.status_code == 200:
    #     next
    # else:
    #     print(f'Error: {response.status_code}')
    #     return None

    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return pd.DataFrame() 
    
    dfs = pd.read_html(StringIO(response.text))
    
    try:
        # dfs[1] 
        df_cfs = dfs[1]

        # df_cfs.columns = df_cfs.columns.droplevel(level=[0, 1])
        df_cfs = df_cfs.reset_index(drop=True)
        df_cfs = df_cfs.iloc[:, :-4]
        prev_year = str(int(year) - 1)

        if quarter == '01':
            month_date = '01-01 ~ 03-31'
        elif quarter == '02':
            month_date = '01-01 ~ 06-30'
        elif quarter == '03':
            month_date = '01-01 ~ 09-30'
        elif quarter == '04':
            year = year
            prev_year = str(int(year) - 1)

        if quarter == '01':
            df_cfs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{prev_year}-{month_date} 金額']
        elif quarter in ('02', '03' ):
            df_cfs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{prev_year}-{month_date} 金額']
        else:
            df_cfs.columns = ['會計項目', f'{year}年度 金額', f'{prev_year}年度 金額']
        
        df_cfs.set_index('會計項目', inplace=True)
        
        return df_cfs
    
    except (ValueError, IndexError):
        try:
            print(f'Trying alternative source (dfs[2])...')  # 若抓取失敗，改使用 dfs[2]
            df_cfs = dfs[2]
    
            # df_cfs.columns = df_cfs.columns.droplevel(level=[0, 1])
            df_cfs = df_cfs.reset_index(drop=True)
            df_cfs = df_cfs.iloc[:, :-4]
            prev_year = str(int(year) - 1)

            if quarter == '01':
                month_date = '01-01 ~ 03-31'
            elif quarter == '02':
                month_date = '01-01 ~ 06-30'
            elif quarter == '03':
                month_date = '01-01 ~ 09-30'
            elif quarter == '04':
                year = year
                prev_year = str(int(year) - 1)

            if quarter == '01':
                df_cfs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{prev_year}-{month_date} 金額']
            elif quarter in ('02', '03' ):
                df_cfs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{prev_year}-{month_date} 金額']
            else:
                df_cfs.columns = ['會計項目', f'{year}年度 金額', f'{prev_year}年度 金額']
            
            df_cfs.set_index('會計項目', inplace=True)
            
            return df_cfs
        
        except:
            print(f'Payload for financial industry...') # 若抓取失敗，可能是金融保險業，payload 不一樣
            
            # 要更改的 payload 數據
            payload = {
            'encodeURIComponent': '1',
            'id': '',
            'key': '',
            'TYPEK': 'sii',
            'step': '2',
            'year': year,
            'season': quarter,
            'co_id': stock_code,
            'firstin': '1',
            }

            response = requests.post(url, data=payload, headers=headers)

            if response.status_code != 200:
                print(f'Error: {response.status_code}')
                return pd.DataFrame()   
            
            dfs = pd.read_html(StringIO(response.text))
            
            # dfs[1] 
            df_cfs = dfs[1]

            # df_cfs.columns = df_cfs.columns.droplevel(level=[0, 1])
            df_cfs = df_cfs.reset_index(drop=True)
            df_cfs = df_cfs.iloc[:, :-4]
            prev_year = str(int(year) - 1)

            if quarter == '01':
                month_date = '01-01 ~ 03-31'
            elif quarter == '02':
                month_date = '01-01 ~ 06-30'
            elif quarter == '03':
                month_date = '01-01 ~ 09-30'
            elif quarter == '04':
                year = year
                prev_year = str(int(year) - 1)

            if quarter == '01':
                df_cfs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{prev_year}-{month_date} 金額']
            elif quarter in ('02', '03' ):
                df_cfs.columns = ['會計項目', f'{year}-{month_date} 金額', f'{prev_year}-{month_date} 金額']
            else:
                df_cfs.columns = ['會計項目', f'{year}年度 金額', f'{prev_year}年度 金額']
            
            df_cfs.set_index('會計項目', inplace=True)
            
            return df_cfs
                
                
            
#
# stock_code = '1213'
# year = '107'
# quarter = '04'
# df_is = get_cfs_data(stock_code, year, quarter)
# df_is



#%%
# 權益變動表
# 包成def
# random header

# import requests
# import pandas as pd 
# from io import StringIO
# from fake_useragent import UserAgent


# def get_sce_data(stock_code, year, quarter):
#     url = 'https://mops.twse.com.tw/mops/web/ajax_t164sb06'

#     # 生成隨機的使用者代理
#     ua = UserAgent()
#     user_agent = ua.random

#     # headers 數據
#     headers = {
#         'User-Agent': user_agent,
#     }
    
#     # 构建 payload 数据
#     payload = {
#         'encodeURIComponent': '1',
#         'step': '1',
#         'firstin': '1',
#         'off': '1',
#         'keyword4': '',
#         'code1': '',
#         'TYPEK2': '',
#         'checkbtn': '',
#         'queryName': 'co_id',
#         'inpuType': 'co_id',
#         'TYPEK': 'all',
#         'isnew': 'false',
#         'co_id': stock_code,  
#         'year': year,    
#         'season': quarter   
#     }

#     response = requests.post(url, data=payload, headers=headers)

#     if response.status_code == 200:
#         next
#     else:
#         print(f'Error: {response.status_code}')
#         return None

#     # 解析 HTML 
#     dfs = pd.read_html(StringIO(response.text))
    
#     result_dataframe = pd.DataFrame()
#     for d in range(1, 3):  
#         df = dfs[d]

#         # 清洗和格式化 DataFrame
#         df = df.iloc[:, :-17]
#         df.columns = df.columns.droplevel(level=1)
#         df.columns = df.iloc[0]
#         df = df.reset_index(drop=True)
#         df = df[1:]
        
#         prev_year = str(int(year) - 1)
#         if quarter == '01':
#             s_quarter = ' Q1'
#         elif quarter == '02':
#             s_quarter = ' 上半年度'
#         elif quarter == '03':
#             s_quarter = ' 前三季'
#         elif quarter == '04':
#             s_quarter = '年度'
            
#         if d == 1:
#             df['time_period'] = f'{year}{s_quarter}'
#         elif d == 2:
#             df['time_period'] = f'{prev_year}{s_quarter}'
#         # df['time_period'] = f'{year}{s_quarter}' if df.index[0] == 0 else f'{prev_year}{s_quarter}'
        
#         result_dataframe = pd.concat([result_dataframe, df], ignore_index=True)
    
#     result_dataframe = result_dataframe.reset_index(drop=True)
#     result_dataframe.set_index('會計項目', inplace=True)
    
#     return result_dataframe 




#%%
# 三表一起查
#  預設五年，kind 全印，單選一支標的


def store_3_financial_report_to_sqlite(stock_code, start_date=None, end_date=None):

    # 
    db_path = rf'G:\我的雲端硬碟\000-AI\py\18-STOCK\tw_financial_reports\store_3_financial_report_{stock_code}.db'
    
    # if os.path.exists(db_path):
    #     os.remove(db_path)
        
        
    if start_date is None:
        start_date = (datetime.date.today() - datetime.timedelta(days=365*5.5)).strftime('%Y%m%d')

    if end_date is None:
        end_date = datetime.date.today().strftime('%Y%m%d')
        
    current_year = int(start_date[:4]) - 1911
    current_month = int(start_date[4:6])
    
    end_year = int(end_date[:4]) - 1911
    end_month = int(end_date[4:6])

    fail_count = 0 
    
    #
    conn2 = sqlite3.connect(db_path)
    cursor = conn2.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    while current_year < end_year or (current_year == end_year and current_month <= end_month):
        if current_month <= 3:
            quarter = '01'
        elif current_month > 3 and current_month <= 6:
            quarter = '02'
        elif current_month > 6 and current_month <= 9:
            quarter = '03'
        else:
            quarter = '04'
            
        random_message = random.choice([
            "正在抓取資料，請有耐心~",
            "快好了，再等等...",
            "要抓五年的資料，不是這麼快的!",
            "有耐心者成大事!",
            "你這麼有耐心，果然是美女",
            "沒耐心怎麼賺得到波段?",
            "這比等大樂透開獎快吧?",
            "有耐心才不會投機，靠運氣來的錢，會靠實力虧光",
            "沒耐心就像打開冰箱找東西，找不到的時候只會更生氣",
            "這不是買麥當勞，有時候得來速還比我慢",
            "你這麼有耐心，簡直是等待的高手，會不會有點太強了？",
            "等待中...不是等紅燈，是等待財富的綠燈",
            "這不是煮泡麵，需要一點時間的",
            "放輕鬆，不是等開會，是等待你的資產翻倍~",
            "快好了，再等等，就像等愛情一樣，還是你都等不到?",
            "抓五年資料，不是瞬間魔法，是耐力的魔法！",
            "有耐心就能成大事，連電視劇都說的好像很容易一樣",
            "這不是捉寶可夢，是你捉取財富的好機會",
            "這不是等公車，是等待爆富的時刻~",
            "沒耐心就像打開冰箱找東西，找不到的時候只會更生氣",
            "等待中...這不是等紅燈，是等待財富的綠燈",
            "就像等待網頁加載一樣，耐心等待，才能看到精彩內容",
            "就像等待手搖飲料一樣，加點料就能更好喝，但我比較喜歡奶蓋",
            "股票市場沒有捷徑，只有等待的路，你走得下去嗎？",
            "這不是等待演唱會開場，是等待你的資產翻倍",
            "就像在找藏寶圖，一定會找到寶藏的",
            "像等待online game的大獎，堅持下去，你就會抽到大獎",
            "等一下，這比你對刮刮樂快"
        ])
        print(random_message)
                
        try:
            bs_data = get_bs_data(stock_code, current_year, quarter)
            is_data = get_is_data(stock_code, current_year, quarter)
            cfs_data = get_cfs_data(stock_code, current_year, quarter)
            # sce_data = get_sce_data(stock_code, current_year, quarter)
            # fail_count = 0
            
            #   
            if quarter =='01':
                quarter_without_0 = '1'
            elif quarter =='02':
                quarter_without_0 = '2'
            elif quarter =='03':
                quarter_without_0 = '3'
            elif quarter =='04':
                quarter_without_0 = '4'
                
            
            table_name = f"{stock_code}_{current_year}Q{quarter_without_0}"
            
            
            # 寫入 bs 資料
            if (table_name+'_bs') in tables:
                print(f"表格 {table_name}_bs 已存在，跳過寫入操作")
            else:
                bs_data.to_sql(table_name + '_bs', conn2, if_exists='replace')
                print(f"成功抓取: {table_name}_bs")
                
            
            # 寫入 cfs 資料
            if (table_name+'_cfs') in tables:
                print(f"表格 {table_name}_cfs 已存在，跳過寫入操作")
            else:
                cfs_data.to_sql(table_name + '_cfs', conn2, if_exists='replace')
                print(f"成功抓取: {table_name}_cfs")
                
            
            # 寫入 is 資料
            if (table_name+'_is') in tables:
                print(f"表格 {table_name}_is 已存在，跳過寫入操作")
            else:
                is_data.to_sql(table_name + '_is', conn2, if_exists='replace')
                print(f"成功抓取: {table_name}_is")
                
            conn2.commit()
            
            # # 寫入 bs 資料   
            # bs_data.to_sql(table_name + '_bs', conn2, if_exists='append')
            # print(f"成功抓取: {table_name}_bs")
            
            # # 寫入 is 資料
            # is_data.to_sql(table_name + '_is', conn2, if_exists='append')
            # print(f"成功抓取: {table_name}_is")

            # # 寫入 cfs 資料
            # cfs_data.to_sql(table_name + '_cfs', conn2, if_exists='append')
            # print(f"成功抓取: {table_name}_cfs")

            # 寫入 sce 資料
            # sce_data.to_sql(table_name + '_sce', conn2, if_exists='append')
            # print(f"成功儲存為: {table_name}_sce")
            
         
            
        except Exception as e:
            fail_count += 1   
            print(f'Error fetching data for {stock_code} {current_year} year Q{quarter} - {str(e)}')
            if fail_count >= 100:  
                print("連續失敗一百次，中斷循環")
                break
        
        time.sleep(5 + random.uniform(0, 5))
        
        current_month += 3
        
        if current_month > 12:
            current_year += 1
            current_month = 1

    current_year += 1
    
    # 關閉資料庫連線
    conn2.close()
    
    
    
    

#%%
# 同性質產業
# 下載github db 再讀取

import tempfile

def download_and_save_industry_db(stock_code):

    url = f'https://github.com/06Cata/tw_financial_reports1/raw/main/industry.db'
    response = requests.get(url)

    # 將數據保存到臨時文件中
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(response.content)
    temp_file_path = temp_file.name
    
    return temp_file_path



#%%
# 同性質產業

def get_stock_code_industry(stock_code):

    # 下載並保存數據庫文件
    temp_file_path = download_and_save_industry_db(stock_code)

    conn = sqlite3.connect(temp_file_path)
    cursor = conn.cursor()

    # 提取公司名稱
    cursor.execute(f"SELECT 公司名稱 FROM industry_num WHERE 公司代號={stock_code};")
    result = cursor.fetchone()
    if result:
        stock_name = result[0]
        
    # 提取公司產業
    cursor.execute(f"SELECT 上市櫃 FROM industry_num WHERE 公司代號={stock_code};")
    result2 = cursor.fetchone()
    if result2:
        stock_size = result2[0]
    
    # 提取公司產業別
    cursor.execute(f"SELECT 備註 FROM industry_num WHERE 公司代號={stock_code};")
    result3 = cursor.fetchone()
    if result3:
        stock_industry = result3[0]

        # 使用提取的產業別，get相關產業所有資料
        cursor.execute(f"SELECT 公司代號, 公司名稱, 上市櫃 FROM industry_num WHERE 備註='{stock_industry}';")
        related_data = cursor.fetchall()



    # # 提取公司名稱、公司規模、公司產業別及相關產業所有資料
    # cursor.execute(f"""
    #     SELECT i1.公司代號, i1.公司名稱, i1.上市櫃, i1.備註, i2.公司代號, i2.公司名稱, i2.上市櫃 
    #     FROM industry_num AS i1 
    #     JOIN industry_num AS i2 ON i1.備註 = i2.備註 
    #     WHERE i1.公司代號={stock_code};
    # """)
    # results = cursor.fetchall()

    # # 關閉游標和數據庫連接
    # cursor.close()
    # conn.close()

    # if results:
    #     stock_code = results[0][0]
    #     stock_name = results[0][1]
    #     stock_size = results[0][2]
    #     stock_industry = results[0][3]
    #     related_data = [(result[4], result[5], result[6]) for result in results]
    # else:
    #     stock_name = None
    #     stock_size = None
    #     stock_industry = None
    #     related_data = None
    
    

    #     if related_data:
    #         print("同產業公司：")
    #         for data in related_data:
    #             print(data)
    #     else:
    #         print("找不到同產業公司")

    # else:
    #     print(f"找不到公司代號 {stock_code} 的相關數據。")

    # 關閉游標和數據庫連接
    cursor.close()
    conn.close()
    
    
    return stock_code, stock_name, stock_size, stock_industry, related_data





#%%
# 下載github db 再讀取，兩個資料庫

def download_and_save_db(stock_code, url1, url2, url3):
    try:
        # 嘗試下載第一個 URL 的數據庫文件
        response = requests.get(url1)
        response.raise_for_status()
        print(f'使用的是URL1 "{url1}" - tw_financial_reports1')
        
    except requests.exceptions.RequestException:
        try:
            # 如果第一個 URL 失敗，嘗試下載第二個 URL 的數據庫文件
            response = requests.get(url2)
            response.raise_for_status()
            print(f'使用的是URL2 "{url2}" - tw_financial_reports2')
            
        except requests.exceptions.RequestException:
            # 如果第二個 URL 也失敗，嘗試下載第三個 URL 的數據庫文件
            response = requests.get(url3)
            response.raise_for_status()
            print(f'使用的是URL3 "{url3}" - tw_financial_reports3')
            

    # 將數據保存到臨時文件中
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(response.content)
    temp_file_path = temp_file.name
    
    return temp_file_path


   
   
    
#%%
# 下載github db 再讀取，兩個資料庫
# 字典 迴圈讀
# 用前五年
# 動態生成變數名稱並不是一個推薦的做法，而是使用字典可以更容易管理和訪問相關的數據
# 包成def

def get_tables_of_dbtablename(stock_code):
    fail_count = 0 
    
    year_prev5 = int(datetime.datetime.now().year) - 1911 - 5
    year_prev4 = int(datetime.datetime.now().year) - 1911 - 4
    year_prev3 = int(datetime.datetime.now().year) - 1911 - 3
    year_prev2 = int(datetime.datetime.now().year) - 1911 - 2
    year_prev1 = int(datetime.datetime.now().year) - 1911 - 1
    year_prev0 = int(datetime.datetime.now().year) - 1911 - 0

    years_prev = [year_prev5, year_prev4, year_prev3, year_prev2, year_prev1, year_prev0]

    # 創建字典來存儲表名
    tables = {}
    for p in years_prev:
        for n in range(1, 5):
            tables[f'year_{p}Q{n}_bs'] = f'{stock_code}_{p}Q{n}_bs'
            tables[f'year_{p}Q{n}_is'] = f'{stock_code}_{p}Q{n}_is'
            tables[f'year_{p}Q{n}_cfs'] = f'{stock_code}_{p}Q{n}_cfs'
            # tables[f'year_{p}Q{n}_sce'] = f'{stock_code}_{p}Q{n}_sce'

    # 嘗試使用第一個 URL 下載數據庫文件，若失敗則使用第二個 URL...
    url1 = f'https://github.com/06Cata/tw_financial_reports1/raw/main/store_3_financial_report_{stock_code}.db'
    url2 = f'https://github.com/06Cata/tw_financial_reports2/raw/main/store_3_financial_report_{stock_code}.db'
    url3 = f'https://github.com/06Cata/tw_financial_reports3/raw/main/store_3_financial_report_{stock_code}.db'
    temp_file_path = download_and_save_db(stock_code, url1, url2, url3)

    # 連接到 SQLite 資料庫
    conn = sqlite3.connect(temp_file_path)
    
    dfs = {}
    for key, value in tables.items():
        try:
            dfs[key] = pd.read_sql(f'SELECT * FROM [{value}]', conn)
            dfs[key].set_index('會計項目', inplace=True)  # 設置索引
            print(f'Successifully get data from {value}')
            fail_count = 0 
        except Exception as e:
            print(f'Error reading table {value}: {str(e)}')
            fail_count += 1   
            if fail_count >= 100:  
                print("連續失敗一百次，中斷循環")
                break

    # 
    suss_tables = list(dfs.keys())
    
    conn.close()
    
    # 刪除臨時文件
    os.remove(temp_file_path)
    
    return dfs, suss_tables

# 
# stock_code = '5904'
# dfs, suss_tables = get_tables_of_dbtablename(stock_code)

# suss_tables



        

#%%
# 繪圖

# 001 包成def
# 001: 資產負債比率 Debt to Asset Ratio
# 銀行業ok

def plotly_debt_to_asset_ratio(dfs):

    data_dtar = []

    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                        '負債總額': 0,
                        '資產總額': 0,
                        '資產負債比%': 0,
                    }
            
            try:
                # 計算負債總額佔資產總額的百分比
                row_data['負債總額'] = value.at['負債總額', value.columns[0]] if '負債總額' in value.index else value.at['負債總計', value.columns[0]]
                row_data['資產總額'] = value.at['資產總額', value.columns[0]] if '資產總額' in value.index else value.at['資產總計', value.columns[0]]
                row_data['資產負債比%'] = round(row_data['負債總額']/row_data['資產總額']*100, 2)
        
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
            
            data_dtar.append(row_data)
                
    result_df_dtar = pd.DataFrame(data_dtar)
    result_df_dtar['近四季平均資產負債比%'] = round(result_df_dtar['資產負債比%'].rolling(window=4).mean(), 2)


    
    # 
    result_df_dtar['年份'] = result_df_dtar['年份-季度'].str[:3]
    result_df_dtar['季度'] = result_df_dtar['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_dtar['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_dtar[result_df_dtar['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_dtar[(result_df_dtar['年份'] == year) & (result_df_dtar['季度'] == '1')].empty and
                result_df_dtar[(result_df_dtar['年份'] == year) & (result_df_dtar['季度'] == '2')].empty and
                result_df_dtar[(result_df_dtar['年份'] == year) & (result_df_dtar['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_dtar[result_df_dtar['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_dtar[(result_df_dtar['年份'] == year) & (result_df_dtar['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_dtar[(result_df_dtar['年份'] == year) & (result_df_dtar['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_dtar[result_df_dtar['年份'] == year]])

        elif count == 2:
            if (result_df_dtar[(result_df_dtar['年份'] == year) & (result_df_dtar['季度'] == '3')].empty and
                result_df_dtar[(result_df_dtar['年份'] == year) & (result_df_dtar['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_dtar[result_df_dtar['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_dtar[(result_df_dtar['年份'] == year) & (result_df_dtar['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_dtar[(result_df_dtar['年份'] == year) & (result_df_dtar['季度'] == '4')]])

        elif count == 1:
            if not result_df_dtar[(result_df_dtar['年份'] == year) & (result_df_dtar['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_dtar[result_df_dtar['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)
    
    
    
    # 
    # 四季

    selected_rows['資產負債比%_調整'] = selected_rows['資產負債比%']


    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '資產負債比%_調整']  = np.nan
            selected_rows.loc[i, '資產負債比%_調整']  = np.nan

    selected_rows['近四季平均資產負債比%_調整'] = round(selected_rows['資產負債比%_調整'].rolling(window=4).mean(), 2)
    
    
    
    # 
    fig = go.Figure()

    selected_rows['is_above_60'] = selected_rows['資產負債比%'] > 60

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['資產負債比%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(
            color=['red' if above_60 else 'mediumturquoise' for above_60 in selected_rows['is_above_60']],
            size=8,
        ),
        text=selected_rows['資產負債比%'].astype(str)+'%',  
        textposition='top center',  
    ))

    #
    min1 = selected_rows['資產負債比%'].min()
    max1 = selected_rows['資產負債比%'].max()
    y_range = [min1-5, max1+5]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1


    fig.update_layout(
        title=f'前{year_difference}年各季度資產負債比率',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='資產負債比%', range=y_range),
        legend=dict(title='資產負債比%',
                    x=1.0,
                    y=1.4,
                    traceorder='normal',
                    orientation='v'), 
            width = 900,
            height = 400
        )


    # fig.show()


    # 
    fig2 = go.Figure()

    selected_rows['is_above_60'] = selected_rows['近四季平均資產負債比%_調整'] > 60

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均資產負債比%_調整'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(
            color=['red' if above_60 else 'mediumturquoise' for above_60 in selected_rows['is_above_60']],
            size=8,
        ),
        text=selected_rows['近四季平均資產負債比%_調整'].astype(str)+'%',  
        textposition='top center',  
    ))

    #
    min1 = selected_rows['近四季平均資產負債比%_調整'].min()
    max1 = selected_rows['近四季平均資產負債比%_調整'].max()
    y_range = [min1-5, max1+5]

    fig2.update_layout(
        title=f'近四季平均資產負債比率',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='近四季平均資產負債比%', range=y_range),
        legend=dict(title='近四季平均資產負債比%',
                    x=1.0,
                    y=1.4,
                    traceorder='normal',
                    orientation='v'), 
            width = 900,
            height = 400
        )


    # fig2.show()


    
    average_debt_to_asset_ratio = round(selected_rows['近四季平均資產負債比%_調整'].iloc[-1], 2)
    return fig, fig2, average_debt_to_asset_ratio




#%%
# 002 包成def
# 長期資金佔不動產、廠房及設備比率 Ratio of liabilities to assets
# 銀行業不看

def plotly_ratio_of_liabilities_to_assets(dfs):

    data_rolta = []

    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                        '權益總額': 0,
                        '非流動負債合計': 0,
                        '不動產、廠房及設備': 0,
                        '長期資金佔不動產、廠房及設備比率(倍)': 0,
                    }
            
            try:
                #  
                row_data['權益總額'] = value.loc['權益總額', value.columns[0]] 
                row_data['非流動負債合計'] = value.loc['非流動負債合計', value.columns[0]] 
                row_data['不動產、廠房及設備'] = value.loc['不動產、廠房及設備', value.columns[0]] 
                row_data['長期資金佔不動產、廠房及設備比率(倍)'] = round((row_data['權益總額'] + row_data['非流動負債合計'] ) / row_data['不動產、廠房及設備'], 3)
            
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            data_rolta.append(row_data)
            
    result_df_rolta = pd.DataFrame(data_rolta)
 


    # 
    result_df_rolta['年份'] = result_df_rolta['年份-季度'].str[:3]
    result_df_rolta['季度'] = result_df_rolta['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_rolta['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_rolta[result_df_rolta['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_rolta[(result_df_rolta['年份'] == year) & (result_df_rolta['季度'] == '1')].empty and
                result_df_rolta[(result_df_rolta['年份'] == year) & (result_df_rolta['季度'] == '2')].empty and
                result_df_rolta[(result_df_rolta['年份'] == year) & (result_df_rolta['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_rolta[result_df_rolta['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_rolta[(result_df_rolta['年份'] == year) & (result_df_rolta['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_rolta[(result_df_rolta['年份'] == year) & (result_df_rolta['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_rolta[result_df_rolta['年份'] == year]])

        elif count == 2:
            if (result_df_rolta[(result_df_rolta['年份'] == year) & (result_df_rolta['季度'] == '3')].empty and
                result_df_rolta[(result_df_rolta['年份'] == year) & (result_df_rolta['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_rolta[result_df_rolta['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_rolta[(result_df_rolta['年份'] == year) & (result_df_rolta['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_rolta[(result_df_rolta['年份'] == year) & (result_df_rolta['季度'] == '4')]])

        elif count == 1:
            if not result_df_rolta[(result_df_rolta['年份'] == year) & (result_df_rolta['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_rolta[result_df_rolta['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)


    # 
    # 四季

    selected_rows['長期資金佔不動產、廠房及設備比率(倍)_調整'] = selected_rows['長期資金佔不動產、廠房及設備比率(倍)']


    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '長期資金佔不動產、廠房及設備比率(倍)_調整']  = np.nan
            selected_rows.loc[i, '長期資金佔不動產、廠房及設備比率(倍)_調整']  = np.nan

    selected_rows['近四季平均長期資金佔不動產、廠房及設備比率(倍)_調整'] = round(selected_rows['長期資金佔不動產、廠房及設備比率(倍)_調整'].rolling(window=4).mean(), 2)


    # 
    fig = go.Figure()

    selected_rows['is_below_1'] = selected_rows['長期資金佔不動產、廠房及設備比率(倍)'] < 1

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['長期資金佔不動產、廠房及設備比率(倍)'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(
            color=['red' if below_1 else 'mediumturquoise' for below_1 in selected_rows['is_below_1']],
            size=8,
        ),
        text=selected_rows['長期資金佔不動產、廠房及設備比率(倍)'].astype(str),   
        textposition='top center',  
    ))


    #
    min1 = selected_rows['長期資金佔不動產、廠房及設備比率(倍)'].min()
    max1 = selected_rows['長期資金佔不動產、廠房及設備比率(倍)'].max()
    y_range = [min1-1, max1+1]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
        
    fig.update_layout(
        title=f'前{year_difference}年各季度長期資金佔不動產、廠房及設備比率(倍)',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='長期資金佔不動產、廠房及設備比率(倍)', range=y_range),
        legend=dict(title='',
                    x=1.0,
                    y=1.4,
                    traceorder='normal',
                    orientation='v'), 
            width = 900,
            height = 400
        )


    # fig.show()




    # 
    fig2 = go.Figure()

    selected_rows['is_below_1'] = selected_rows['近四季平均長期資金佔不動產、廠房及設備比率(倍)_調整'] < 1

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均長期資金佔不動產、廠房及設備比率(倍)_調整'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(
            color=['red' if below_1 else 'mediumturquoise' for below_1 in selected_rows['is_below_1']],
            size=8,
        ),
        text=selected_rows['近四季平均長期資金佔不動產、廠房及設備比率(倍)_調整'].astype(str),   
        textposition='top center',  
    ))


    #
    min1 = selected_rows['近四季平均長期資金佔不動產、廠房及設備比率(倍)_調整'].min()
    max1 = selected_rows['近四季平均長期資金佔不動產、廠房及設備比率(倍)_調整'].max()
    y_range = [min1-1, max1+1]
        
    fig2.update_layout(
        title=f'近四季平均長期資金佔不動產、廠房及設備比率(倍)',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='長期資金佔不動產、廠房及設備比率(倍)', range=y_range),
        legend=dict(title='',
                    x=1.0,
                    y=1.4,
                    traceorder='normal',
                    orientation='v'), 
            width = 900,
            height = 400
        )


    # fig2.show()

    
    average_ratio_of_liabilities_to_assets = round(selected_rows['近四季平均長期資金佔不動產、廠房及設備比率(倍)_調整'].iloc[-1], 3)
    return fig, fig2, average_ratio_of_liabilities_to_assets






#%%
# 002-2 包成def
# 現金與約當現金(流動資產)、不動產廠房及設備(非流動資產)、流動負債合計、非流動負債合計、長期資金(非流動負債)趨勢
# 銀行業不看

def plotly_business(dfs):

    data_business = []

    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                        '現金及約當現金': 0,
                        '流動負債合計': 0,
                        '非流動負債合計': 0,
                        '不動產、廠房及設備': 0,
                        '長期借款': 0,
                    }
            try:
                row_data['現金及約當現金'] = value.loc['現金及約當現金', value.columns[0]]            
                row_data['流動負債合計'] = value.loc['流動負債合計', value.columns[0]] 
                row_data['非流動負債合計'] = value.loc['非流動負債合計', value.columns[0]] 
                
                try:
                    row_data['不動產、廠房及設備']  = value.loc['不動產、廠房及設備', value.columns[0]]
                except KeyError:
                    pass
                try:
                    row_data['長期借款']  = value.loc['長期借款', value.columns[0]]
                except KeyError:
                    pass
            
                
            except KeyError as e:
                print(f'在 {key} 找不到: {str(e)}，將相應的資料設為NaN')
            
            data_business.append(row_data)

    result_df_business = pd.DataFrame(data_business)
    
    
    # 
    result_df_business['年份'] = result_df_business['年份-季度'].str[:3]
    result_df_business['季度'] = result_df_business['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_business['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_business[result_df_business['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_business[(result_df_business['年份'] == year) & (result_df_business['季度'] == '1')].empty and
                result_df_business[(result_df_business['年份'] == year) & (result_df_business['季度'] == '2')].empty and
                result_df_business[(result_df_business['年份'] == year) & (result_df_business['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_business[result_df_business['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_business[(result_df_business['年份'] == year) & (result_df_business['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_business[(result_df_business['年份'] == year) & (result_df_business['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_business[result_df_business['年份'] == year]])

        elif count == 2:
            if (result_df_business[(result_df_business['年份'] == year) & (result_df_business['季度'] == '3')].empty and
                result_df_business[(result_df_business['年份'] == year) & (result_df_business['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_business[result_df_business['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_business[(result_df_business['年份'] == year) & (result_df_business['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_business[(result_df_business['年份'] == year) & (result_df_business['季度'] == '4')]])

        elif count == 1:
            if not result_df_business[(result_df_business['年份'] == year) & (result_df_business['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_business[result_df_business['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)


    # 
    # 四季

    selected_rows['現金及約當現金_調整'] = selected_rows['現金及約當現金']
    selected_rows['流動負債合計_調整'] = selected_rows['流動負債合計']
    selected_rows['非流動負債合計_調整'] = selected_rows['非流動負債合計']
    selected_rows['不動產、廠房及設備_調整'] = selected_rows['不動產、廠房及設備']
    selected_rows['長期借款_調整'] = selected_rows['長期借款']



    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '現金及約當現金_調整']  = np.nan
            selected_rows.loc[i, '現金及約當現金_調整']  = np.nan
            selected_rows.loc[i-1, '流動負債合計_調整']  = np.nan
            selected_rows.loc[i, '流動負債合計_調整']  = np.nan
            selected_rows.loc[i-1, '非流動負債合計_調整']  = np.nan
            selected_rows.loc[i, '非流動負債合計_調整']  = np.nan
            selected_rows.loc[i-1, '不動產、廠房及設備_調整']  = np.nan
            selected_rows.loc[i, '不動產、廠房及設備_調整']  = np.nan
            selected_rows.loc[i-1, '長期借款_調整']  = np.nan
            selected_rows.loc[i, '長期借款_調整']  = np.nan
        

    # 
    selected_rows['近四季平均現金及約當現金_調整']= selected_rows['現金及約當現金_調整'].rolling(window=4).mean()
    selected_rows['近四季平均流動負債合計_調整']= selected_rows['流動負債合計_調整'].rolling(window=4).mean()
    selected_rows['近四季平均非流動負債合計_調整']= selected_rows['非流動負債合計_調整'].rolling(window=4).mean()
    selected_rows['近四季平均不動產、廠房及設備_調整']= selected_rows['不動產、廠房及設備_調整'].rolling(window=4).mean()
    selected_rows['近四季平均長期借款_調整']= selected_rows['長期借款_調整'].rolling(window=4).mean()


    # 
    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['現金及約當現金'],
        mode='lines+markers+text',
        line=dict(color='green', width=2),
        textposition='top center',
        name='現金及約當現金'
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['不動產、廠房及設備'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y2',   
        textposition='top center',
        name='不動產、廠房及設備'
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['長期借款'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y3',   
        textposition='top center',
        name='長期借款'
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['流動負債合計'],
        mode='lines+markers+text',
        line=dict(color='orange', width=2),
        yaxis='y4',   
        textposition='top center',
        name='流動負債合計'
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['非流動負債合計'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.2),
        yaxis='y5',   
        textposition='top center',
        name='非流動負債合計'
    ))

    # 更新佈局設置

    max1 = selected_rows['現金及約當現金'].max()
    max2 = selected_rows['不動產、廠房及設備'].max()
    max3 = selected_rows['長期借款'].max()
    max4 = selected_rows['流動負債合計'].max()
    max5 = selected_rows['非流動負債合計'].max()

    min1 = selected_rows['現金及約當現金'].min()
    min2 = selected_rows['不動產、廠房及設備'].min()
    min3 = selected_rows['長期借款'].min()
    min4 = selected_rows['流動負債合計'].min()
    min5 = selected_rows['非流動負債合計'].min()

    y_range = [min(min1,min2,min3,min4,min5)-50000,max(max1,max2,max3,max4,max5)+ 50000]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
    year_difference 

    fig.update_layout(
        title=f'前{year_difference}年各季度現金與約當現金(流動資產)、不動產廠房及設備(非流動資產)、流動負債合計、<br>\
非流動負債合計、長期借款趨勢',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='', range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        yaxis3=dict(title='', overlaying='y', side='right', range=y_range),
        yaxis4=dict(title='', overlaying='y', side='right', range=y_range),
        yaxis5=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=1000,
        height=480,
    )

    # fig.show()

    # 
    fig2 = go.Figure()


    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均現金及約當現金_調整'],
        mode='lines+markers+text',
        line=dict(color='green', width=2),
        textposition='top center',
        name='現金及約當現金'
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均不動產、廠房及設備_調整'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y2',   
        textposition='top center',
        name='不動產、廠房及設備'
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均長期借款_調整'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y3',   
        textposition='top center',
        name='長期借款'
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均流動負債合計_調整'],
        mode='lines+markers+text',
        line=dict(color='orange', width=2),
        yaxis='y4',   
        textposition='top center',
        name='流動負債合計'
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均非流動負債合計_調整'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2),
        yaxis='y5',   
        textposition='top center',
        name='非流動負債合計'
    ))

    # 更新佈局設置

    max11 = selected_rows['近四季平均現金及約當現金_調整'].max()
    max22 = selected_rows['近四季平均流動負債合計_調整'].max()
    max33 = selected_rows['近四季平均非流動負債合計_調整'].max()
    max44 = selected_rows['近四季平均不動產、廠房及設備_調整'].max()
    max55 = selected_rows['近四季平均長期借款_調整'].max()

    min11 = selected_rows['近四季平均現金及約當現金_調整'].min()
    min22 = selected_rows['近四季平均流動負債合計_調整'].min()
    min33 = selected_rows['近四季平均非流動負債合計_調整'].min()
    min44 = selected_rows['近四季平均不動產、廠房及設備_調整'].min()
    min55 = selected_rows['近四季平均長期借款_調整'].min()

    y_range22 = [min(min11,min22,min33,min44,min55)-50000,max(max11,max22,max33,max44,max55)+ 50000]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
    year_difference 

    fig2.update_layout(
        title=f'近四季平均現金與約當現金(流動資產)、不動產廠房及設備(非流動資產)、流動負債合計、<br>\
非流動負債合計、長期借款趨勢',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='', range=y_range22),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range22),
        yaxis3=dict(title='', overlaying='y', side='right', range=y_range22),
        yaxis4=dict(title='', overlaying='y', side='right', range=y_range22),
        yaxis5=dict(title='', overlaying='y', side='right', range=y_range22),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=1000,
        height=480,
    )

    # fig2.show()
    return fig, fig2



    
    

#%%
# 003 包成def
# 總負債/股東權益比率 Total Debt/Equity Ratio、財務槓桿
# 銀行業ok

def plotly_total_debt_equity_ratio(dfs):

    data_tder = []

    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                        '負債及權益總計': 0,
                        '權益總額': 0,
                    }
            
            try:
                # 總負債/股東權益比率
                row_data['負債及權益總計'] = value.loc['負債及權益總計', value.columns[0]]
                row_data['權益總額'] = value.at['權益總額', value.columns[0]] if '權益總額' in value.index else value.at['權益總計', value.columns[0]]
                
                
                row_data['總負債/股東權益比%'] = round(row_data['負債及權益總計']/row_data['權益總額']*100, 3)
                row_data['財務槓桿(倍)'] = round(row_data['負債及權益總計']/row_data['權益總額'], 3)

            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            data_tder.append(row_data)

                
    result_df_tder = pd.DataFrame(data_tder)
    result_df_tder['近四季平均財務槓桿(倍)'] = round(result_df_tder['財務槓桿(倍)'].rolling(window=4).mean(), 3)

    
    # 
    result_df_tder['年份'] = result_df_tder['年份-季度'].str[:3]
    result_df_tder['季度'] = result_df_tder['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_tder['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_tder[result_df_tder['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_tder[(result_df_tder['年份'] == year) & (result_df_tder['季度'] == '1')].empty and
                result_df_tder[(result_df_tder['年份'] == year) & (result_df_tder['季度'] == '2')].empty and
                result_df_tder[(result_df_tder['年份'] == year) & (result_df_tder['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_tder[result_df_tder['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_tder[(result_df_tder['年份'] == year) & (result_df_tder['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_tder[(result_df_tder['年份'] == year) & (result_df_tder['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_tder[result_df_tder['年份'] == year]])

        elif count == 2:
            if (result_df_tder[(result_df_tder['年份'] == year) & (result_df_tder['季度'] == '3')].empty and
                result_df_tder[(result_df_tder['年份'] == year) & (result_df_tder['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_tder[result_df_tder['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_tder[(result_df_tder['年份'] == year) & (result_df_tder['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_tder[(result_df_tder['年份'] == year) & (result_df_tder['季度'] == '4')]])

        elif count == 1:
            if not result_df_tder[(result_df_tder['年份'] == year) & (result_df_tder['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_tder[result_df_tder['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)

    # 
    
    selected_rows['財務槓桿(倍)_調整'] = selected_rows['財務槓桿(倍)']


    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '財務槓桿(倍)_調整']  = np.nan
            selected_rows.loc[i, '財務槓桿(倍)_調整']  = np.nan
            
    selected_rows['近四季平均財務槓桿(倍)'] = round(selected_rows['財務槓桿(倍)_調整'].rolling(window=4).mean(), 3)

    

    # 
    fig = go.Figure()

    selected_rows['is_above_3'] = selected_rows['財務槓桿(倍)'] > 3
    
    
    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['財務槓桿(倍)'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(
            color=['red' if x else 'mediumturquoise' for x in selected_rows['is_above_3']],
            size=8,
        ),
        text=selected_rows['財務槓桿(倍)'],   
        textposition='top center',  
    ))


    # roe高，要看一下槓桿是否過高(股東權益過低)
    min1 = selected_rows['財務槓桿(倍)'].min()
    max1 = selected_rows['財務槓桿(倍)'].max()
    y_range = [min1-0.25, max1+0.25]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
        
    example = 2
    fig.update_layout(
        title=f'前{year_difference}年各季度總負債/股東權益比<br>\
與同業比，通常2倍上下為合理。範例: {example}，等於財務槓桿為{example}倍',        
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='財務槓桿(倍)', range=y_range),
        legend=dict(title='財務槓桿(倍)',
                    x=1.0,
                    y=1.4,
                    traceorder='normal',
                    orientation='v'), 
            width = 900,
            height = 400
        )


    # fig.show()


    # 
    fig2 = go.Figure()

    selected_rows['is_above_3'] = selected_rows['近四季平均財務槓桿(倍)'] > 3
    
    
    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均財務槓桿(倍)'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(
            color=['red' if x else 'mediumturquoise' for x in selected_rows['is_above_3']],
            size=8,
        ),
        text=selected_rows['近四季平均財務槓桿(倍)'],   
        textposition='top center',  
    ))


    # roe高，要看一下槓桿是否過高(股東權益過低)
    min1 = selected_rows['近四季平均財務槓桿(倍)'].min()
    max1 = selected_rows['近四季平均財務槓桿(倍)'].max()
    y_range = [min1-0.25, max1+0.25]
        
    example = 2
    fig2.update_layout(
        title=f'近四季平均總負債/股東權益比',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='近四季平均財務槓桿(倍)', range=y_range),
        legend=dict(title='近四季平均財務槓桿(倍)',
                    x=1.0,
                    y=1.4,
                    traceorder='normal',
                    orientation='v'), 
            width = 900,
            height = 400
        )

    # fig2.show()


    # 
    average_total_debt_equity_ratio = round(selected_rows['近四季平均財務槓桿(倍)'].iloc[-1], 3)
    return fig, fig2, average_total_debt_equity_ratio




#%%
# 004 包成def
# 股東權益: 股本、保留盈餘、資本公積
# 銀行業ok、有些沒有保留盈餘、資本公積ok 

def plotly_shareholders_equity(dfs):

    data_se = []

    for key, value in dfs.items():
        if key.endswith('_bs'):
            row_data = {'年份-季度': key[5:10], 
                        '股本合計':0,
                        '保留盈餘合計': 0,
                        '資本公積合計': 0
                    }
            
            try:  
                # 
                # row_data['股本合計'] = value.at['股本合計', value.columns[0]] if '股本合計' in value.index else value.at['股本', value.columns[0]]
                # row_data['保留盈餘合計']= value.at['保留盈餘合計', value.columns[0]] if '保留盈餘合計' in value.index else value.at['保留盈餘', value.columns[0]]
                # row_data['資本公積合計'] = (
                #                             value.at['資本公積合計', value.columns[0]]
                #                             if '資本公積合計' in value.index
                #                             else (
                #                                 value.at['資本公積', value.columns[0]]
                #                                 if '資本公積' in value.index
                #                                 else 0
                #                             )
                #                             )

                row_data['股本合計'] = value.at['股本合計', value.columns[0]] if '股本合計' in value.index else value.at['股本', value.columns[0]] if '股本' in value.index else 0
                row_data['保留盈餘合計'] = value.at['保留盈餘合計', value.columns[0]] if '保留盈餘合計' in value.index else value.at['保留盈餘', value.columns[0]] if '保留盈餘' in value.index else 0
                row_data['資本公積合計'] = value.at['資本公積合計', value.columns[0]] if '資本公積合計' in value.index else value.at['資本公積', value.columns[0]] if '資本公積' in value.index else 0
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            data_se.append(row_data)
                
    result_df_se = pd.DataFrame(data_se)

    
    # 
    result_df_se['年份'] = result_df_se['年份-季度'].str[:3]
    result_df_se['季度'] = result_df_se['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_se['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_se[result_df_se['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_se[(result_df_se['年份'] == year) & (result_df_se['季度'] == '1')].empty and
                result_df_se[(result_df_se['年份'] == year) & (result_df_se['季度'] == '2')].empty and
                result_df_se[(result_df_se['年份'] == year) & (result_df_se['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_se[result_df_se['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_se[(result_df_se['年份'] == year) & (result_df_se['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_se[(result_df_se['年份'] == year) & (result_df_se['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_se[result_df_se['年份'] == year]])

        elif count == 2:
            if (result_df_se[(result_df_se['年份'] == year) & (result_df_se['季度'] == '3')].empty and
                result_df_se[(result_df_se['年份'] == year) & (result_df_se['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_se[result_df_se['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_se[(result_df_se['年份'] == year) & (result_df_se['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_se[(result_df_se['年份'] == year) & (result_df_se['季度'] == '4')]])

        elif count == 1:
            if not result_df_se[(result_df_se['年份'] == year) & (result_df_se['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_se[result_df_se['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)

 
    # 

    selected_rows['股本合計_調整'] = selected_rows['股本合計']
    selected_rows['保留盈餘合計_調整'] = selected_rows['保留盈餘合計']
    selected_rows['資本公積合計_調整'] = selected_rows['資本公積合計']


    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '股本合計_調整']  = np.nan
            selected_rows.loc[i, '股本合計_調整']  = np.nan
            selected_rows.loc[i-1, '保留盈餘合計_調整']  = np.nan
            selected_rows.loc[i, '保留盈餘合計_調整']  = np.nan
            selected_rows.loc[i-1, '資本公積合計_調整']  = np.nan
            selected_rows.loc[i, '資本公積合計_調整']  = np.nan
            
    selected_rows['近四季平均股本']= selected_rows['股本合計_調整'].rolling(window=4).mean()
    selected_rows['近四季平均保留盈餘']= selected_rows['保留盈餘合計_調整'].rolling(window=4).mean()
    selected_rows['近四季平均資本公積']= selected_rows['資本公積合計_調整'].rolling(window=4).mean()

    

    # 
    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['股本合計'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2),
        # text=result_df['股本合計'],
        textposition='top center',
        name='股本合計'
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['保留盈餘合計'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y2',   
        # text=result_df['保留盈餘合計'],
        textposition='top center',
        name='保留盈餘合計'
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['資本公積合計'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y3',   
        # text=result_df['資本公積合計'],
        textposition='top center',
        name='資本公積合計'
    ))


    # 更新佈局設置

    max1 = selected_rows['股本合計'].max()
    max2 = selected_rows['保留盈餘合計'].max()
    max3 = selected_rows['資本公積合計'].max()

    min1 = selected_rows['股本合計'].min()
    min2 = selected_rows['保留盈餘合計'].min()
    min3 = selected_rows['資本公積合計'].min()
    y_range = [min(min1,min2,min3)-50000,max(max1,max2,max3)+ 50000]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
        
    fig.update_layout(
        title=f'前{year_difference}年各季度股東權益: 股本、保留盈餘、資本公積',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='', range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        yaxis3=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig.show()
    
    
    
    # 
    fig2 = go.Figure()


    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均股本'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.2),
        # text=result_df['股本'],
        textposition='top center',
        name='近四季平均股本'
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均保留盈餘'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y2',   
        # text=result_df['保留盈餘'],
        textposition='top center',
        name='近四季平均保留盈餘'
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均資本公積'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y3',   
        # text=result_df['資本公積'],
        textposition='top center',
        name='近四季平均資本公積'
    ))


    # 更新佈局設置

    max11 = selected_rows['近四季平均股本'].max()
    max22 = selected_rows['近四季平均保留盈餘'].max()
    max33 = selected_rows['近四季平均資本公積'].max()

    min11 = selected_rows['近四季平均股本'].min()
    min22 = selected_rows['近四季平均保留盈餘'].min()
    min33 = selected_rows['近四季平均資本公積'].min()
    y_range22 = [min(min11,min22,min33)-500000,max(max11,max22,max33)+ 500000]

    fig2.update_layout(
        title=f'近四季平均股東權益: 股本、保留盈餘、資本公積',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='', range=y_range22),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range22),
        yaxis3=dict(title='', overlaying='y', side='right', range=y_range22),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig2.show()


    return fig, fig2





#%%
# 005 包成def
# ROE
# 銀行業ok


def plotly_roe(dfs):

    data_roe = []

    # ROE
    # 迴圈遍歷所有的 dfs
    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                        '權益總額': 0,
                        '本期淨利（淨損）': 0,
                    }
            try:
                # 確保是資產負債表(_bs)的資料
                row_data['權益總額'] = value.at['權益總額', value.columns[0]] if '權益總額' in value.index else value.at['權益總計', value.columns[0]]
                
                # 尋找對應的損益表(_is)資料
                cfs_key = key.replace('_bs', '_is')
                if cfs_key in dfs:
                    row_data['本期淨利（淨損）'] = dfs[cfs_key].loc['本期淨利（淨損）', dfs[cfs_key].columns[0]] if '本期淨利（淨損）' in dfs[cfs_key].index else dfs[cfs_key].loc['本期稅後淨利（淨損）', dfs[cfs_key].columns[0]]

                else:
                    raise ValueError(f'找不到對應的損益表 ({cfs_key}) 資料')

               
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
            

            data_roe.append(row_data)

    # 將資料轉成 DataFrame
    result_df_roe = pd.DataFrame(data_roe)



    #
    result_df_roe['年份'] = result_df_roe['年份-季度'].str[:3]
    result_df_roe['季度'] = result_df_roe['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_roe['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_roe[result_df_roe['年份'] == year]])
                
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_roe[(result_df_roe['年份'] == year) & (result_df_roe['季度'] == '1')].empty and
                result_df_roe[(result_df_roe['年份'] == year) & (result_df_roe['季度'] == '2')].empty and
                result_df_roe[(result_df_roe['年份'] == year) & (result_df_roe['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_roe[result_df_roe['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_roe[(result_df_roe['年份'] == year) & (result_df_roe['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_roe[(result_df_roe['年份'] == year) & (result_df_roe['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_roe[result_df_roe['年份'] == year]])


        elif count == 2:
            if (result_df_roe[(result_df_roe['年份'] == year) & (result_df_roe['季度'] == '3')].empty and
                result_df_roe[(result_df_roe['年份'] == year) & (result_df_roe['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_roe[result_df_roe['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_roe[(result_df_roe['年份'] == year) & (result_df_roe['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_roe[(result_df_roe['年份'] == year) & (result_df_roe['季度'] == '4')]])

                
        elif count == 1:
            if not result_df_roe[(result_df_roe['年份'] == year) & (result_df_roe['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_roe[result_df_roe['年份'] == year]])


    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)

    
    
    # 
    # 單季


    selected_rows['本期淨利（淨損）_調整'] = selected_rows['本期淨利（淨損）']

    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '本期淨利（淨損）_調整'] -= selected_rows.loc[i-3:i-1, '本期淨利（淨損）'].sum()
            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '本期淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i, '本期淨利（淨損）_調整']  = np.nan
        


        
    selected_rows['ROE%'] = round((selected_rows['本期淨利（淨損）_調整']/ ((selected_rows['權益總額'] + selected_rows['權益總額'].shift(1))/2)*100),2)

    
    # 
    # 單季table
    

    selected_rows_t = selected_rows.transpose()
    
    # # 選擇 "年份-季度" 和 "ROE%" 這兩列
    selected_columns = ['年份-季度', 'ROE%']
    selected_rows_t = selected_rows_t[selected_rows_t.index.isin(selected_columns)]
    selected_rows_t.columns = selected_rows_t.iloc[0]
        
        
    # 
    # 提取 DataFrame 中的資料
    table_data = selected_rows_t.loc[['ROE%'], :]
    table_data = table_data.dropna(axis=1)

    try:
        table_data = table_data.iloc[:,-8:]
    except:
        pass

    # 創建表格
    fig = ff.create_table(table_data, height_constant=30)

    # 
    fig.update_layout(
        title='單季ROE%',
        width=900,
        height=200,
    )

    # fig.show()
    
    
    # 
    # 四季

    selected_rows_t_4q = selected_rows

    selected_rows_t_4q['四季累積淨利（淨損）_調整'] = selected_rows_t_4q['本期淨利（淨損）_調整'].rolling(window=4).sum() 
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i-1, '四季累積淨利（淨損）_調整']  = selected_rows_t_4q.loc[i-1, '本期淨利（淨損）']
            selected_rows_t_4q.loc[i, '四季累積淨利（淨損）_調整']  = selected_rows_t_4q.loc[i, '本期淨利（淨損）']


    selected_rows_t_4q['與前四季差異ROE%'] = round((selected_rows_t_4q['四季累積淨利（淨損）_調整']/ ((selected_rows_t_4q['權益總額'] + selected_rows_t_4q['權益總額'].shift(4))/2)*100),2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '與前四季差異ROE%'] = round(selected_rows_t_4q.loc[i, '本期淨利（淨損）'] / ((selected_rows_t_4q.loc[i, '權益總額'] + selected_rows_t_4q.loc[i-1, '權益總額']) / 2) * 100, 2)


    selected_rows_t_4q['近四季累計ROE%'] = round(selected_rows_t_4q['ROE%'].rolling(window=4).sum() ,2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累計ROE%'] = round(selected_rows_t_4q.loc[i, '本期淨利（淨損）'] / ((selected_rows_t_4q.loc[i, '權益總額'] + selected_rows_t_4q.loc[i-1, '權益總額']) / 2) * 100, 2)

        
        
    # 
    fig2 = go.Figure()

    selected_rows_t_4q['is_below_10'] = selected_rows_t_4q ['近四季累計ROE%'] < 10

    fig2.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季累計ROE%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(
        color=['red' if below_10 else 'mediumturquoise' for below_10 in selected_rows_t_4q['is_below_10']],
        size=8,
        ),
        text=selected_rows_t_4q['近四季累計ROE%'].astype(str)+"%", 
        textposition='top center',  
    ))

    #
    min1 = selected_rows_t_4q['近四季累計ROE%'].min()
    max1 = selected_rows_t_4q['近四季累計ROE%'].max()
    y_range = [min1-3, max1+3]


    fig2.update_layout(
        title=f'近四季累計ROE趨勢',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='與前四季差異ROE%', range=y_range),
        legend=dict(title='與前四季差異ROE%',
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'), 
        width = 900,
        height = 400
    )


    # fig.show()
    
    
    average_roe = round(selected_rows_t_4q['近四季累計ROE%'].iloc[-1], 2)
    return fig, fig2, average_roe
    
    

#%%
# 006 包成def
# roa
# 銀行業ok

def plotly_roa(dfs):

    data_roa = []

    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                            '資產總額': 0,
                            '本期淨利（淨損）': 0,
                        }
            try:
                # 確保是資產負債表(_bs)的資料
                row_data['資產總額'] = value.at['資產總額', value.columns[0]] if '資產總額' in value.index else value.at['資產總計', value.columns[0]]

                # 尋找對應的損益表(_cfs)資料
                cfs_key = key.replace('_bs', '_is')
                if cfs_key in dfs:
                    row_data['本期淨利（淨損）'] = dfs[cfs_key].loc['本期淨利（淨損）', dfs[cfs_key].columns[0]] if '本期淨利（淨損）' in dfs[cfs_key].index else dfs[cfs_key].loc['本期稅後淨利（淨損）', dfs[cfs_key].columns[0]]
                else:
                    raise ValueError(f'找不到對應的損益表 ({cfs_key}) 資料')
                
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            data_roa.append(row_data)

    # 將資料轉成 DataFrame
    result_df_roa = pd.DataFrame(data_roa)
    
    

    # 
    result_df_roa['年份'] = result_df_roa['年份-季度'].str[:3]
    result_df_roa['季度'] = result_df_roa['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_roa['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_roa[result_df_roa['年份'] == year]])
                
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_roa[(result_df_roa['年份'] == year) & (result_df_roa['季度'] == '1')].empty and
                result_df_roa[(result_df_roa['年份'] == year) & (result_df_roa['季度'] == '2')].empty and
                result_df_roa[(result_df_roa['年份'] == year) & (result_df_roa['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_roa[result_df_roa['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_roa[(result_df_roa['年份'] == year) & (result_df_roa['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_roa[(result_df_roa['年份'] == year) & (result_df_roa['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_roa[result_df_roa['年份'] == year]])


        elif count == 2:
            if (result_df_roa[(result_df_roa['年份'] == year) & (result_df_roa['季度'] == '3')].empty and
                result_df_roa[(result_df_roa['年份'] == year) & (result_df_roa['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_roa[result_df_roa['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_roa[(result_df_roa['年份'] == year) & (result_df_roa['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_roa[(result_df_roa['年份'] == year) & (result_df_roa['季度'] == '4')]])

                
        elif count == 1:
            if not result_df_roa[(result_df_roa['年份'] == year) & (result_df_roa['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_roa[result_df_roa['年份'] == year]])


    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)



    # 
    # 單季

    selected_rows['本期淨利（淨損）_調整'] = selected_rows['本期淨利（淨損）']

    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '本期淨利（淨損）_調整'] -= selected_rows.loc[i-3:i-1, '本期淨利（淨損）'].sum()
            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '本期淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i, '本期淨利（淨損）_調整']  = np.nan
        
    selected_rows['ROA%'] = round((selected_rows['本期淨利（淨損）_調整']/ ((selected_rows['資產總額'] + selected_rows['資產總額'].shift(1))/2)*100),2)


    #
    # 單季table
    import plotly.figure_factory as ff

    selected_rows_t = selected_rows.transpose()

    # # 選擇 "年份-季度" 和 "ROE%" 這兩列
    selected_columns = ['年份-季度', 'ROA%']
    selected_rows_t = selected_rows_t[selected_rows_t.index.isin(selected_columns)]
    selected_rows_t.columns = selected_rows_t.iloc[0]
    
    
    # 
    # 提取 DataFrame 中的資料
    table_data = selected_rows_t.loc[['ROA%'], :]
    table_data = table_data.dropna(axis=1)

    try:
        table_data = table_data.iloc[:,-8:]
    except:
        pass


    # 創建表格
    fig = ff.create_table(table_data, height_constant=30)

    # 
    fig.update_layout(
        title='單季ROA%',
        width=900,
        height=200,
    )

    # fig.show()
    
    
    
    # 
    # 四季
    selected_rows_t_4q = selected_rows

    selected_rows_t_4q['四季累積淨利（淨損）_調整'] = selected_rows_t_4q['本期淨利（淨損）_調整'].rolling(window=4).sum() 
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i-1, '四季累積淨利（淨損）_調整']  = selected_rows_t_4q.loc[i-1, '本期淨利（淨損）']
            selected_rows_t_4q.loc[i, '四季累積淨利（淨損）_調整']  = selected_rows_t_4q.loc[i, '本期淨利（淨損）']


    selected_rows_t_4q['與前四季差異ROA%'] = round((selected_rows_t_4q['四季累積淨利（淨損）_調整']/ ((selected_rows_t_4q['資產總額'] + selected_rows_t_4q['資產總額'].shift(4))/2)*100),2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '與前四季差異ROA%'] = round(selected_rows_t_4q.loc[i, '本期淨利（淨損）'] / ((selected_rows_t_4q.loc[i, '資產總額'] + selected_rows_t_4q.loc[i-1, '資產總額']) / 2) * 100, 2)


    selected_rows_t_4q['近四季累計ROA%'] = round(selected_rows_t_4q['ROA%'].rolling(window=4).sum() ,2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累計ROA%'] = round(selected_rows_t_4q.loc[i, '本期淨利（淨損）'] / ((selected_rows_t_4q.loc[i, '資產總額'] + selected_rows_t_4q.loc[i-1, '資產總額']) / 2) * 100, 2)



    # 
    fig2 = go.Figure()
    selected_rows_t_4q['is_below_6'] = selected_rows_t_4q['近四季累計ROA%'] < 6

    fig2.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季累計ROA%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(
        color=['red' if below_6 else 'mediumturquoise' for below_6 in selected_rows_t_4q['is_below_6']],
        size=8,
        ),
        text=selected_rows_t_4q['近四季累計ROA%'].astype(str)+"%",  
        textposition='top center',  
    ))

    #
    min1 = selected_rows_t_4q['近四季累計ROA%'].min()
    max1 = selected_rows_t_4q['近四季累計ROA%'].max()
    y_range = [min1-3, max1+3]

    fig2.update_layout(
        title=f'近四季累計ROA趨勢，未加利息及扣稅',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='近四季累計ROA%', range=y_range),
        legend=dict(title='近四季累計ROA%',
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'), 
        width = 900,
        height = 400
    )


    # fig2.show()

        
    average_roa = round(selected_rows_t_4q['近四季累計ROA%'].iloc[-1], 2)
    return fig, fig2, average_roa






#%%
# 007 包成def
# 應收帳款、存貨周轉、應付帳款、總資產周轉、現金佔比

def plotly_days_sales_outstanding(dfs):

    data_dso = []

    # 迴圈遍歷所有的 dfs
    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                        '現金及約當現金': 0,
                        '存貨': 0,
                        '現金及約當現金%': 0,
                        '存貨%': 0,
                        # 
                        '應收帳款淨額': 0,
                        '應收票據淨額': 0,
                        '其他應收款淨額': 0,
                        # 
                        '應付帳款': 0,
                        '應付票據': 0,
                        '其他應付款': 0,
                        '資產總額': 0,
                        '營業成本合計': 0,
                        '營業收入合計': 0,
                        '營業費用合計': 0,
                    }
            
            try:
                # 確保是資產負債表(_bs)的資料
                try:
                    row_data['現金及約當現金'] = value.loc['現金及約當現金', value.columns[0]]
                except KeyError:
                    pass
                
                try:
                    row_data['存貨'] = value.loc['存貨', value.columns[0]]
                except KeyError:
                    pass
                try:
                    row_data['應收帳款淨額']  = value.loc['應收帳款淨額', value.columns[0]]
                except KeyError:
                    pass
                
                try:
                    row_data['應收票據淨額']  = value.loc['應收票據淨額', value.columns[0]]
                except KeyError:
                    pass
                
                try:
                    row_data['其他應收款淨額']  = value.loc['其他應收款淨額', value.columns[0]]
                except KeyError:
                    pass
                
                try:
                    row_data['應付帳款']  = value.loc['應付帳款', value.columns[0]]
                except KeyError:
                    pass
                
                try:
                    row_data['應付票據']  = value.loc['應付票據', value.columns[0]]
                except KeyError:
                    pass
                
                try:
                    row_data['其他應付款']  = value.loc['其他應付款', value.columns[0]]
                except KeyError:
                    pass

                    
                row_data['資產總額']  = value.loc['資產總額', value.columns[0]]
                
                row_data['現金及約當現金%'] = round(row_data['現金及約當現金'] / row_data['資產總額'] * 100, 2)
                row_data['存貨%'] = round(row_data['存貨'] / row_data['資產總額'] *100, 2)
            
                
                # 尋找對應的損益表(_is)資料
                cfs_key = key.replace('_bs', '_is')
                if cfs_key in dfs:
                    row_data['營業成本合計'] = dfs[cfs_key].loc['營業成本合計', dfs[cfs_key].columns[0]]
                    row_data['營業收入合計'] = dfs[cfs_key].loc['營業收入合計', dfs[cfs_key].columns[0]]
                    row_data['營業費用合計'] = dfs[cfs_key].loc['營業費用合計', dfs[cfs_key].columns[0]]
                else:
                    raise ValueError(f'找不到對應的損益表 ({cfs_key}) 資料')

            
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            #  
            data_dso.append(row_data)

    # 將資料轉成 DataFrame
    result_df_dso = pd.DataFrame(data_dso)


    #
    result_df_dso['年份'] = result_df_dso['年份-季度'].str[:3]
    result_df_dso['季度'] = result_df_dso['年份-季度'].str[-1:]

    result_df_dso['應收總帳款'] = result_df_dso['應收帳款淨額'] + result_df_dso['應收票據淨額'] + result_df_dso['其他應收款淨額']
    result_df_dso['應付總帳款'] = result_df_dso['應付帳款'] + result_df_dso['應付票據'] + result_df_dso['其他應付款']


    # 計算每個年份出現的次數
    year_counts = result_df_dso['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_dso[result_df_dso['年份'] == year]])
                
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_dso[(result_df_dso['年份'] == year) & (result_df_dso['季度'] == '1')].empty and
                result_df_dso[(result_df_dso['年份'] == year) & (result_df_dso['季度'] == '2')].empty and
                result_df_dso[(result_df_dso['年份'] == year) & (result_df_dso['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_dso[result_df_dso['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_dso[(result_df_dso['年份'] == year) & (result_df_dso['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_dso[(result_df_dso['年份'] == year) & (result_df_dso['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_dso[result_df_dso['年份'] == year]])


        elif count == 2:
            if (result_df_dso[(result_df_dso['年份'] == year) & (result_df_dso['季度'] == '3')].empty and
                result_df_dso[(result_df_dso['年份'] == year) & (result_df_dso['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_dso[result_df_dso['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_dso[(result_df_dso['年份'] == year) & (result_df_dso['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_dso[(result_df_dso['年份'] == year) & (result_df_dso['季度'] == '4')]])

                
        elif count == 1:
            if not result_df_dso[(result_df_dso['年份'] == year) & (result_df_dso['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_dso[result_df_dso['年份'] == year]])


    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)



    # 
    # 單季

    selected_rows['營業成本合計_調整'] = selected_rows['營業成本合計']
    selected_rows['營業收入合計_調整'] = selected_rows['營業收入合計']
    selected_rows['營業費用合計_調整'] = selected_rows['營業費用合計']

    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '營業成本合計_調整'] -= selected_rows.loc[i-3:i-1, '營業成本合計'].sum()
            selected_rows.loc[i, '營業收入合計_調整'] -= selected_rows.loc[i-3:i-1, '營業收入合計'].sum()
            selected_rows.loc[i, '營業費用合計_調整'] -= selected_rows.loc[i-3:i-1, '營業費用合計'].sum()
            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '營業成本合計_調整']  = np.nan
            selected_rows.loc[i, '營業成本合計_調整']  = np.nan
            selected_rows.loc[i-1, '營業收入合計_調整']  = np.nan
            selected_rows.loc[i, '營業收入合計_調整']  = np.nan
            selected_rows.loc[i-1, '營業費用合計_調整']  = np.nan
            selected_rows.loc[i, '營業費用合計_調整']  = np.nan
        

    selected_rows['存貨周轉(次)'] = round(selected_rows['營業成本合計_調整'] /  ((selected_rows['存貨'] + selected_rows['存貨'].shift(1)) / 2) ,2)
    selected_rows['存貨周轉天數'] =  round( (365/4) /  selected_rows['存貨周轉(次)'], 2)

    selected_rows['存貨周轉(次)'].replace([np.inf, -np.inf], np.nan, inplace=True)

    # if selected_rows['存貨周轉(次)'].isnull().any() or (selected_rows['存貨周轉(次)'] == 0).all():
    #     selected_rows['存貨周轉(次)'] = float('nan')

    # if selected_rows['存貨周轉天數'].isnull().any() or (selected_rows['存貨周轉天數'] == 0).all():
    #     selected_rows['存貨周轉天數'] = float('nan')


    selected_rows['應收帳款周轉(次)'] = round(selected_rows['營業收入合計_調整'] / ((selected_rows['應收帳款淨額'] + selected_rows['應收帳款淨額'].shift(1)) / 2) ,2)
    selected_rows['應收帳款周轉天數'] = round( (365/4) / selected_rows['應收帳款周轉(次)'], 2)  

    selected_rows['應付帳款周轉(次)'] = round(selected_rows['營業成本合計_調整'] / ((selected_rows['應付帳款'] + selected_rows['應付帳款'].shift(1)) / 2) ,2)
    selected_rows['應付帳款周轉天數'] = round( (365/4) / selected_rows['應付帳款周轉(次)'], 2)  

    selected_rows['總資產周轉(次)'] = round(selected_rows['營業收入合計_調整'] / ((selected_rows['資產總額'] + selected_rows['資產總額'].shift(1)) / 2), 2)

    
    
    # 
    # 單季 table

    selected_rows_t = selected_rows.transpose()

    # # 選擇 "年份-季度" ...
    selected_columns = ['年份-季度','存貨周轉(次)', '應收帳款周轉(次)', '應付帳款周轉(次)','總資產周轉(次)']
    selected_rows_t = selected_rows_t[selected_rows_t.index.isin(selected_columns)]
    selected_rows_t.columns = selected_rows_t.iloc[0]

    try:
        selected_rows_t = selected_rows_t.iloc[:,-12:] 
    except:
        pass

    selected_rows_t.index = ['年份-季度','存貨週轉', '應收週轉', '應付週轉','總資產週轉']

     
    
        

    # 

    # 提取 DataFrame 中的資料
    table_data = selected_rows_t.loc[['總資產週轉','存貨週轉','應收週轉','應付週轉'], :].reset_index()
    
    table_data = table_data.fillna('NaN')
    # table_data = table_data[table_data != 'NaN']
    # table_data = table_data.dropna(axis=1)
    # table_data = table_data.dropna(axis=0)

    # 創建表格
    fig = ff.create_table(table_data, height_constant=30)

    # 
    fig.update_layout(
        title='單季營運週轉',
        width=900,
        height=200,
    )

    # fig.show()
    
    
    # 
    # 四季

    selected_rows_t_4q = selected_rows

    # 
    # result_df_dso_4q['四季營業成本合計_調整'] = result_df_dso_4q['營業成本合計_調整'].rolling(window=4).sum() 
    # result_df_dso_4q['與前四季差異存貨'] =   (result_df_dso_4q['存貨'] + result_df_dso['存貨'].shift(4)) / 2

    # result_df_dso_4q['與前四季差異存貨周轉(次)'] = round(result_df_dso_4q['四季營業成本合計_調整'] /  result_df_dso_4q['與前四季差異存貨'] , 2)
    # result_df_dso_4q['與前四季差異存貨天數'] =  round( 365 / result_df_dso_4q['與前四季差異存貨周轉(次)'] , 2)

    selected_rows_t_4q['近四季累積存貨周轉(次)'] = round(selected_rows_t_4q['存貨周轉(次)'].rolling(window=4).sum(), 2)
    selected_rows_t_4q['近四季存貨天數'] = round(365 / selected_rows_t_4q['近四季累積存貨周轉(次)'] , 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累積存貨周轉(次)'] = round(selected_rows_t_4q.loc[i, '營業成本合計'] / ((selected_rows_t_4q.loc[i, '存貨'] + selected_rows_t_4q.loc[i-1, '存貨']) / 2) , 2)
            selected_rows_t_4q['近四季存貨天數'] = round(365 / selected_rows_t_4q['近四季累積存貨周轉(次)'] , 2)



    # 
    # result_df_dso_4q['四季營業收入合計_調整'] = result_df_dso_4q['營業收入合計_調整'].rolling(window=4).sum() 
    # result_df_dso_4q['與前四季差異應收帳款'] =   (result_df_dso_4q['應收總帳款'] + result_df_dso['應收總帳款'].shift(4)) / 2

    # result_df_dso_4q['與前四季差異應收帳款周轉(次)'] = round(result_df_dso_4q['四季營業收入合計_調整'] /  result_df_dso_4q['與前四季差異應收帳款'] , 2)
    # result_df_dso_4q['與前四季差異應收帳款天數'] = round(365 / result_df_dso_4q['與前四季差異應收帳款周轉(次)'], 2)

    selected_rows_t_4q['近四季累積應收帳款周轉(次)'] = round(selected_rows_t_4q['應收帳款周轉(次)'].rolling(window=4).sum(), 2)
    selected_rows_t_4q['近四季應收帳款天數'] = round(365 / selected_rows_t_4q['近四季累積應收帳款周轉(次)'] , 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累積應收帳款周轉(次)'] = round(selected_rows_t_4q.loc[i, '營業收入合計'] / ((selected_rows_t_4q.loc[i, '應收帳款淨額'] + selected_rows_t_4q.loc[i-1, '應收帳款淨額']) / 2) , 2)
            selected_rows_t_4q['近四季應收帳款天數'] = round(365 / selected_rows_t_4q['近四季累積應收帳款周轉(次)'] , 2)


    #
    # result_df_dso_4q['與前四季差異應付帳款'] =   (result_df_dso_4q['應付總帳款'] + result_df_dso['應付總帳款'].shift(4)) / 2

    # result_df_dso_4q['與前四季差異應付帳款周轉(次)'] = round(result_df_dso_4q['四季營業成本合計_調整'] /  result_df_dso_4q['與前四季差異應付帳款'] , 2)
    # result_df_dso_4q['與前四季差異應付帳款天數'] = round(365 / result_df_dso_4q['與前四季差異應付帳款周轉(次)'], 2)

    selected_rows_t_4q['近四季累積應付帳款周轉(次)'] = round(selected_rows_t_4q['應付帳款周轉(次)'].rolling(window=4).sum(), 2)
    selected_rows_t_4q['近四季應付帳款天數'] = round(365 / selected_rows_t_4q['近四季累積應付帳款周轉(次)'] , 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累積應付帳款周轉(次)'] = round(selected_rows_t_4q.loc[i, '營業成本合計'] / ((selected_rows_t_4q.loc[i, '應付帳款'] + selected_rows_t_4q.loc[i-1, '應付帳款']) / 2) , 2)
            selected_rows_t_4q['近四季應付帳款天數'] = round(365 / selected_rows_t_4q['近四季累積應付帳款周轉(次)'] , 2)


    # 資產周轉率 = 總營業收入(Total Revenue) ÷ (期初資產+期末資產)/2
    # result_df_dso_4q['與前四季差異資產總額'] =   (result_df_dso_4q['資產總額'] + result_df_dso['資產總額'].shift(4)) / 2

    # result_df_dso_4q['與前四季差異總資產周轉(次)'] =  round(result_df_dso_4q['四季營業收入合計_調整'] /  result_df_dso_4q['與前四季差異資產總額'] , 2)

    selected_rows_t_4q['近四季累積總資產周轉(次)'] =  round(selected_rows_t_4q['總資產周轉(次)'].rolling(window=4).sum(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累積總資產周轉(次)'] = round(selected_rows_t_4q.loc[i, '營業收入合計'] / ((selected_rows_t_4q.loc[i, '資產總額'] + selected_rows_t_4q.loc[i-1, '資產總額']) / 2) , 2)


 
    # 
    fig2 = go.Figure()

    # 添加總資產年周轉(次)的長條圖
    fig2.add_trace(go.Bar(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季累積總資產周轉(次)'],
        text=selected_rows_t_4q['近四季累積總資產周轉(次)'],   
        marker_color=['red' if x <= 1 else 'mediumturquoise' for x in selected_rows_t_4q['近四季累積總資產周轉(次)']],  
        name='總資產周轉(次)', 
        width=0.6, 
    ))


    # 更新佈局設置

    # max1 = selected_rows_t_4q['近四季累積總資產周轉(次)'].max()
    # min1 = selected_rows_t_4q['近四季累積總資產周轉(次)'].min()
    # y_range = [min1, max1+0.2]

    fig2.update_layout(
        title=f'<span style="white-space: nowrap; width: 500px;">近四季累積總資產周轉(次)<br>\
總資產周轉>1次，才有賺；若<1，多數是資本密集行業，要注意總資產中的現金佔比是否足夠，<br>\
或是應收帳款天數較短(<14天)、存貨天數較短(<60天)',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='總資產周轉(次)'),  # , range=y_range
        legend=dict(
            x=1,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400
    )

    # fig2.show()
    
    
    
    # 
    fig22 = go.Figure()


    # 添加存貨年周轉(次)的折線圖
    if not selected_rows_t_4q['近四季累積存貨周轉(次)'].isnull().all():
        fig22.add_trace(go.Scatter(
            x=selected_rows_t_4q['年份-季度'],
            y=selected_rows_t_4q['近四季累積存貨周轉(次)'],
            mode='lines+markers+text',
            line=dict(color='red', width=2),
            text=selected_rows_t_4q['近四季累積存貨周轉(次)'],
            textposition='top center',
            name='存貨周轉(次)',
        ))


    # 添加應收帳款年周轉(次)的折線圖
    if not selected_rows_t_4q['近四季累積應收帳款周轉(次)'].isnull().all():
        fig22.add_trace(go.Scatter(
            x=selected_rows_t_4q['年份-季度'],
            y=selected_rows_t_4q['近四季累積應收帳款周轉(次)'],
            mode='lines+markers+text',
            line=dict(color='blue', width=2),
            text=selected_rows_t_4q['近四季累積應收帳款周轉(次)'],
            textposition='top center',
            name='應收帳款周轉(次)',
        ))


    # 添加應付帳款年周轉(次)的折線圖
    if not selected_rows_t_4q['近四季累積應付帳款周轉(次)'].isnull().all():
        fig22.add_trace(go.Scatter(
            x=selected_rows_t_4q['年份-季度'],
            y=selected_rows_t_4q['近四季累積應付帳款周轉(次)'],
            mode='lines+markers+text',
            line=dict(color='mediumturquoise', width=2.2),
            text=selected_rows_t_4q['近四季累積應付帳款周轉(次)'],
            textposition='top center',
            name='應付帳款周轉(次)',
        ))

    # y軸範圍
    y_range2 = [np.nanmin(selected_rows_t_4q[['近四季累積存貨周轉(次)', '近四季累積應收帳款周轉(次)', '近四季累積應付帳款周轉(次)']]), 
                np.nanmax(selected_rows_t_4q[['近四季累積存貨周轉(次)', '近四季累積應收帳款周轉(次)', '近四季累積應付帳款周轉(次)']])]

    # # y軸範圍
    # y2_max = int(selected_rows_t_4q['近四季累積存貨周轉(次)'].max()) 
    # y3_max = int(selected_rows_t_4q['近四季累積應收帳款周轉(次)'].max()) 
    # y4_max = int(selected_rows_t_4q['近四季累積應付帳款周轉(次)'].max()) 
    # y_range2 = [min(y2_max, y3_max, y4_max)-10, max(y2_max, y3_max, y4_max)+10]

    day1 = selected_rows_t_4q.tail(1)['近四季累積存貨周轉(次)'].iloc[0]
    day2 = selected_rows_t_4q.tail(1)['近四季累積應收帳款周轉(次)'].iloc[0]
    day3 = selected_rows_t_4q.tail(1)['近四季累積應付帳款周轉(次)'].iloc[0]

    # 更新佈局設置
    # 半年存活天數要加進去!
    fig22.update_layout(
        title=f'<span style="white-space: nowrap; width: 500px;">近四季累積存貨、應收、應付帳款周轉(次)<br>\
最新一期存貨為{day1}次、應收帳款為{day2}次、應付帳款為{day3}次',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='周轉(次)', range=y_range2),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range2),
        legend=dict(
            x=1,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400
    )

    # fig22.show()


    # 
    fig3 = go.Figure()


    # 添加存貨年周轉(次)的折線圖
    if not selected_rows_t_4q['近四季存貨天數'].isnull().all():
        fig3.add_trace(go.Scatter(
            x=selected_rows_t_4q['年份-季度'],
            y=selected_rows_t_4q['近四季存貨天數'],
            mode='lines+markers+text',
            line=dict(color='red', width=2),
            text=selected_rows_t_4q['近四季存貨天數'],  
            textposition='top center',  
            name='存貨天數',
        ))

    # 添加應收帳款年周轉(次)的折線圖
    if not selected_rows_t_4q['近四季應收帳款天數'].isnull().all():
        fig3.add_trace(go.Scatter(
            x=selected_rows_t_4q['年份-季度'],
            y=selected_rows_t_4q['近四季應收帳款天數'],
            mode='lines+markers+text',
            line=dict(color='blue', width=2),
            text=selected_rows_t_4q['近四季應收帳款天數'],    
            name='應收帳款天數',
        ))


    # 添加應付帳款年周轉(次)的折線圖
    if not selected_rows_t_4q['近四季應付帳款天數'].isnull().all():
        fig3.add_trace(go.Scatter(
            x=selected_rows_t_4q['年份-季度'],
            y=selected_rows_t_4q['近四季應付帳款天數'],
            mode='lines+markers+text',
            line=dict(color='mediumturquoise', width=2.2),
            text=selected_rows_t_4q['近四季應付帳款天數'],  
            textposition='top center',
            name='應付帳款天數',
        ))

    # # y軸範圍
    # y2_max = int(selected_rows_t_4q['近四季存貨天數'].max()) 
    # y3_max = int(selected_rows_t_4q['近四季應收帳款天數'].max()) 
    # y4_max = int(selected_rows_t_4q['近四季應付帳款天數'].max()) 


    # y_range2 = [min(y2_max, y3_max, y4_max)-100, max(y2_max, y3_max, y4_max)+100]

    # y軸範圍
    y_range22 = [np.nanmin(selected_rows_t_4q[['近四季存貨天數', '近四季應收帳款天數', '近四季應付帳款天數']]), 
                np.nanmax(selected_rows_t_4q[['近四季存貨天數', '近四季應收帳款天數', '近四季應付帳款天數']])]

    money_p = selected_rows_t_4q.tail(1)['現金及約當現金%'].iloc[0]
    goods_p = selected_rows_t_4q.tail(1)['存貨%'].iloc[0]
    survive_m = round(selected_rows_t_4q.tail(1)['現金及約當現金'].iloc[0] / selected_rows_t_4q.tail(1)['營業費用合計_調整'].iloc[0] * 3, 2)

    day1 = selected_rows_t_4q.tail(1)['近四季存貨天數'].iloc[0]
    day2 = selected_rows_t_4q.tail(1)['近四季應收帳款天數'].iloc[0]
    day12 = round(day1 + day2, 2)
    day122 = round(day12 / 30.5, 2)
    day3 = selected_rows_t_4q.tail(1)['近四季應付帳款天數'].iloc[0]

    # 更新佈局設置
    # 半年存活天數要加進去!
    fig3.update_layout(
        title=f'<span style="white-space: nowrap; width: 500px;">近四季存貨、應收、應付帳款天數<br>\
最新一期現金佔比為{money_p}%、存貨佔比為{goods_p}%、現金與約當現金*3={survive_m}個月、存貨為{day1}天、應收帳款為{day2}天<br>\
做生意完整週期為{day12}天={day122}個月</span>',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='天數', range = y_range22),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range22),
        legend=dict(
            x=1,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400
    )

    # fig3.show()



    
    # 
    # 現金週轉天數(有現金壓力的天數) = 存貨+應收帳款-應付帳款
    # 現金週轉天數，平穩或緩慢下降，現金壓力變小


    selected_rows_t_4q_2 = selected_rows_t_4q
    selected_rows_t_4q_2['現金周轉天數'] = round(selected_rows_t_4q_2['近四季存貨天數'] + selected_rows_t_4q_2['近四季應收帳款天數'] - selected_rows_t_4q_2['近四季應付帳款天數'], 2)



    # 
    fig4 = go.Figure()


    fig4.add_trace(go.Scatter(
        x=selected_rows_t_4q_2['年份-季度'],
        y=selected_rows_t_4q_2['現金周轉天數'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=3),
        marker=dict(size=8),
        text=selected_rows_t_4q_2['現金周轉天數'],   
        textposition='top center',  
    ))

    #
    min1 = selected_rows_t_4q_2['現金周轉天數'].min()
    max1 = selected_rows_t_4q_2['現金周轉天數'].max()
    y_range = [min1-30, max1+30]
        
    fig4.update_layout(
        title=f'近四季現金周轉天數<br>\
現金週轉天數(存貨+應收帳款-應付帳款)，要平穩或緩慢下降，現金壓力變小',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='現金周轉天數', range =y_range),
        legend=dict(title='現金周轉天數'), 
        width=900,
        height=300,
    )

    # fig4.show()


    return fig, fig2, fig22, fig3, fig4





#%%
# 007-2包成def

def plotly_fake(dfs):

    data_fake = []

    # 迴圈遍歷所有的 dfs
    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                        '應收帳款淨額': 0,
                        '存貨': 0,
                        '資產總額': 0,
                        '應收帳款%': 0,
                        '存貨%': 0,
                        '現金及約當現金': 0,
                        '營業收入合計': 0,
                        '本期淨利（淨損）': 0
                    }
            
            try:
                # 確保是資產負債表(_bs)的資料
                try:
                    row_data['應收帳款淨額'] = value.loc['應收帳款淨額', value.columns[0]]
                except KeyError:
                    pass  
                
                try:
                    row_data['存貨'] = value.loc['存貨', value.columns[0]]
                except KeyError:
                    pass     
                    
                try:
                    row_data['資產總額'] = value.loc['資產總額', value.columns[0]]
                except KeyError:
                    pass     
                    
                try:
                    row_data['現金及約當現金'] = value.loc['現金及約當現金', value.columns[0]]
                except KeyError:
                    pass 
            
                
                row_data['應收帳款%'] = round(row_data['應收帳款淨額']/row_data['資產總額'] *100, 2)
                
                row_data['存貨%'] = round(row_data['存貨']/row_data['資產總額'] *100, 2)
                
                
                # 尋找對應的損益表(_is)資料
                cfs_key = key.replace('_bs', '_is')
                if cfs_key in dfs:
                    row_data['營業收入合計'] = dfs[cfs_key].loc['營業收入合計', dfs[cfs_key].columns[0]]
                    row_data['本期淨利（淨損）'] = dfs[cfs_key].loc['本期淨利（淨損）', dfs[cfs_key].columns[0]]
                    
                else:
                    raise ValueError(f'找不到對應的損益表 ({cfs_key}) 資料')

            
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            data_fake.append(row_data)


    # 將資料轉成 DataFrame
    result_df_fake = pd.DataFrame(data_fake)


    # 
    result_df_fake['年份'] = result_df_fake['年份-季度'].str[:3]
    result_df_fake['季度'] = result_df_fake['年份-季度'].str[-1:]


    # 計算每個年份出現的次數
    year_counts = result_df_fake['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_fake[result_df_fake['年份'] == year]])
                
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_fake[(result_df_fake['年份'] == year) & (result_df_fake['季度'] == '1')].empty and
                result_df_fake[(result_df_fake['年份'] == year) & (result_df_fake['季度'] == '2')].empty and
                result_df_fake[(result_df_fake['年份'] == year) & (result_df_fake['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_fake[result_df_fake['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_fake[(result_df_fake['年份'] == year) & (result_df_fake['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_fake[(result_df_fake['年份'] == year) & (result_df_fake['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_fake[result_df_fake['年份'] == year]])


        elif count == 2:
            if (result_df_fake[(result_df_fake['年份'] == year) & (result_df_fake['季度'] == '3')].empty and
                result_df_fake[(result_df_fake['年份'] == year) & (result_df_fake['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_fake[result_df_fake['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_fake[(result_df_fake['年份'] == year) & (result_df_fake['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_fake[(result_df_fake['年份'] == year) & (result_df_fake['季度'] == '4')]])

                
        elif count == 1:
            if not result_df_fake[(result_df_fake['年份'] == year) & (result_df_fake['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_fake[result_df_fake['年份'] == year]])


    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)


    # 
    selected_rows['營業收入合計_調整'] = selected_rows['營業收入合計']
    selected_rows['本期淨利（淨損）_調整'] = selected_rows['本期淨利（淨損）']

    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '營業收入合計_調整'] -= selected_rows.loc[i-3:i-1, '營業收入合計'].sum()
            selected_rows.loc[i, '本期淨利（淨損）_調整'] -= selected_rows.loc[i-3:i-1, '本期淨利（淨損）'].sum()

            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '營業收入合計_調整']  = np.nan
            selected_rows.loc[i, '營業收入合計_調整']  = np.nan
            selected_rows.loc[i-1, '本期淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i, '本期淨利（淨損）_調整']  = np.nan



    # 
    selected_rows_t_4q = selected_rows

    selected_rows_t_4q['近四季累積營業收入合計_調整'] = selected_rows_t_4q['營業收入合計_調整'].rolling(window=4).sum()
    selected_rows_t_4q['近四季累積本期淨利（淨損）_調整'] = selected_rows_t_4q['本期淨利（淨損）_調整'].rolling(window=4).sum()

    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累積營業收入合計_調整'] = selected_rows_t_4q.loc[i,'營業收入合計'] 
            selected_rows_t_4q.loc[i-1, '近四季累積營業收入合計_調整'] = selected_rows_t_4q.loc[i-1,'營業收入合計'] 
            selected_rows_t_4q.loc[i, '近四季累積本期淨利（淨損）_調整'] = selected_rows_t_4q.loc[i,'本期淨利（淨損）'] 
            selected_rows_t_4q.loc[i-1, '近四季累積本期淨利（淨損）_調整'] = selected_rows_t_4q.loc[i-1,'本期淨利（淨損）'] 


    selected_rows_t_4q['近四季平均應收帳款%'] = round(selected_rows_t_4q['應收帳款%'].rolling(window=4).mean(),2)
    selected_rows_t_4q['近四季平均存貨%'] = round(selected_rows_t_4q['存貨%'].rolling(window=4).mean(),2)



    # 
    fig = go.Figure()


    #  
    fig.add_trace(go.Bar(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均應收帳款%'],
        marker=dict(color='rgb(50, 225, 210)'), 
        name='近四季平均應收帳款%', 
        width=0.45, 
    ))

    # 
    fig.add_trace(go.Bar(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均存貨%'],
        marker=dict(color='#e78ac3'),
        name='近四季平均存貨%', 
        width=0.45, 
    ))


    #  
    fig.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季累積營業收入合計_調整'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        # text=selected_rows_t_4q['近四季累積營業收入合計_調整'],  
        textposition='top center',  
        yaxis='y3',  
        name='近四季累積營業收入',
    ))

    #  
    fig.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季累積本期淨利（淨損）_調整'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        # text=selected_rows_t_4q['近四季累積本期淨利（淨損）_調整'],  
        textposition='top center',
        yaxis='y4',  
        name='近四季累積淨利（淨損）',
    ))





    # 更新佈局設置
    min01 = selected_rows_t_4q['近四季平均應收帳款%'].min()
    min02 = selected_rows_t_4q['近四季平均存貨%'].min()
    max01 = selected_rows_t_4q['近四季平均應收帳款%'].max()
    max02 = selected_rows_t_4q['近四季平均存貨%'].max()
    y0_range = [min(min01,min02), max(max01,max02)+6]


    min1 = selected_rows_t_4q['近四季累積營業收入合計_調整'].min()
    min2 = selected_rows_t_4q['近四季累積本期淨利（淨損）_調整'].min()
    max1 = selected_rows_t_4q['近四季累積營業收入合計_調整'].max()
    max2 = selected_rows_t_4q['近四季累積本期淨利（淨損）_調整'].max()
    y_range = [min(min1,min2)-1000000, max(max1,max2)+1000000]

    fig.update_layout(
        title=f'假設有間假公司財報，觀察應收帳款天數、應收帳款佔總資產比率、存貨天數、存貨佔總資產比率，<br>\
是否急遽增加，營業收入、淨利成長，但現金與約當現金沒成長',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='',range=y0_range),
        yaxis2=dict(title='', overlaying='y', side='right',range=y0_range),
        yaxis3=dict(title='近四季累積營業收入、淨利', overlaying='y', side='right',range=y_range),
        yaxis4=dict(title='', overlaying='y', side='right',range=y_range), 
        legend=dict(
            x=1,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400
    )

    # fig.show()
    
    
    
    # 
    fig2 = go.Figure()


    #  
    fig2.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['現金及約當現金'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        # text=selected_rows_t_4q['現金及約當現金'],  
        textposition='top center',    
        name='現金及約當現金',
    ))



    # 更新佈局設置
    min01 = selected_rows_t_4q['現金及約當現金'].min()
    max01 = selected_rows_t_4q['現金及約當現金'].max()
    y0_range = [min(min01,min02)-10000, max(max01,max02)+100000]


    fig2.update_layout(
        title=f'現金與約當現金',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='現金與約當現金',range=y0_range),
        legend=dict(
            x=1,
            y=1.5,
            traceorder='normal',
            orientation='v'
        ),
        width=750,
        height=300
    )

    # fig2.show()

    return fig, fig2







# 008 包成def
# 不動產、廠房及設備週轉率 Fixed Asset Turnover Ratio
# 銀行業ok (改成利息收入/平均不動產、廠房及設備淨額)、沒有不動產就不顯示

def plotly_fixed_asset_turnover_ratio(dfs):

    data_fatr = []

    # 迴圈遍歷所有的 dfs
    for key, value in dfs.items():
        if key.endswith('_bs'):
            row_data = {'年份-季度': key[5:10], 
                            '不動產、廠房及設備': 0,
                            '營業收入合計': 0,
                        }
            
            try:
                # 確保是資產負債表(_bs)的資料
                row_data['不動產、廠房及設備'] = value.at['不動產、廠房及設備', value.columns[0]] if '不動產、廠房及設備' in value.index else value.at['不動產及設備－淨額', value.columns[0]]
                
                # 尋找對應的損益表(_is)資料
                cfs_key = key.replace('_bs', '_is')
                if cfs_key in dfs:
                    row_data['營業收入合計']  = dfs[cfs_key].loc['營業收入合計', dfs[cfs_key].columns[0]] if '營業收入合計' in dfs[cfs_key].index else dfs[cfs_key].loc['利息收入', dfs[cfs_key].columns[0]]

                else:
                    raise ValueError(f'找不到對應的損益表 ({cfs_key}) 資料')

            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            # 
            data_fatr.append(row_data)

    # 將資料轉成 DataFrame
    result_df_fatr = pd.DataFrame(data_fatr)
    
    
    # 
    result_df_fatr['年份'] = result_df_fatr['年份-季度'].str[:3]
    result_df_fatr['季度'] = result_df_fatr['年份-季度'].str[-1:]
    
    # 計算每個年份出現的次數
    year_counts = result_df_fatr['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_fatr[result_df_fatr['年份'] == year]])
                
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_fatr[(result_df_fatr['年份'] == year) & (result_df_fatr['季度'] == '1')].empty and
                result_df_fatr[(result_df_fatr['年份'] == year) & (result_df_fatr['季度'] == '2')].empty and
                result_df_fatr[(result_df_fatr['年份'] == year) & (result_df_fatr['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_fatr[result_df_fatr['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_fatr[(result_df_fatr['年份'] == year) & (result_df_fatr['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_fatr[(result_df_fatr['年份'] == year) & (result_df_fatr['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_fatr[result_df_fatr['年份'] == year]])


        elif count == 2:
            if (result_df_fatr[(result_df_fatr['年份'] == year) & (result_df_fatr['季度'] == '3')].empty and
                result_df_fatr[(result_df_fatr['年份'] == year) & (result_df_fatr['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_fatr[result_df_fatr['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_fatr[(result_df_fatr['年份'] == year) & (result_df_fatr['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_fatr[(result_df_fatr['年份'] == year) & (result_df_fatr['季度'] == '4')]])

                
        elif count == 1:
            if not result_df_fatr[(result_df_fatr['年份'] == year) & (result_df_fatr['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_fatr[result_df_fatr['年份'] == year]])


    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)



    # 
    # 
    selected_rows['營業收入合計_調整'] = selected_rows['營業收入合計']

    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '營業收入合計_調整'] -= selected_rows.loc[i-3:i-1, '營業收入合計'].sum()

            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '營業收入合計_調整']  = np.nan
            selected_rows.loc[i, '營業收入合計_調整']  = np.nan

        

    # 
    selected_rows['不動產、廠房及設備週轉(次)'] = round(selected_rows['營業收入合計_調整'] / ((selected_rows['不動產、廠房及設備'] + selected_rows['不動產、廠房及設備'].shift(1))/2),2)


    # 
    selected_rows_t_4q = selected_rows

    selected_rows_t_4q['近四季累積營業收入合計_調整'] = selected_rows_t_4q['營業收入合計_調整'].rolling(window=4).sum()

    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累積營業收入合計_調整'] = selected_rows_t_4q.loc[i,'營業收入合計'] 
            selected_rows_t_4q.loc[i-1, '近四季累積營業收入合計_調整'] = selected_rows_t_4q.loc[i-1,'營業收入合計'] 


    selected_rows_t_4q['近四季累積不動產、廠房及設備週轉(次)'] = selected_rows_t_4q['不動產、廠房及設備週轉(次)'].rolling(window=4).sum()

    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累積不動產、廠房及設備週轉(次)'] = round(selected_rows_t_4q.loc[i, '營業收入合計'] / ((selected_rows_t_4q.loc[i, '不動產、廠房及設備'] + selected_rows_t_4q.loc[i-1,'不動產、廠房及設備'])/2), 2)  

    selected_rows_t_4q['近四季累積不動產、廠房及設備週轉(次)'] = round(selected_rows_t_4q['近四季累積不動產、廠房及設備週轉(次)'],2)
    
    
    # 
    fig01 = go.Figure()


    fig01.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['不動產、廠房及設備週轉(次)'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(size=8),
        text=selected_rows['不動產、廠房及設備週轉(次)'],   
        textposition='top center',  
    ))

    #
    min1 = selected_rows['不動產、廠房及設備週轉(次)'].min()
    max1 = selected_rows['不動產、廠房及設備週轉(次)'].max()
    y_range = [min1-1, max1+1]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1

    fig01.update_layout(
        title=f'前{year_difference}年各季度不動產、廠房及設備週轉(次)',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='不動產、廠房及設備週轉(次)', range=y_range),
        legend=dict(title='不動產、廠房及設備週轉(次)',
                    x=1.0,
                    y=1.4,
                    traceorder='normal',
                    orientation='v'), 
            width = 900,
            height = 400
        )

    # fig01.show()
        
    
    # 
    fig02 = go.Figure()


    fig02.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季累積不動產、廠房及設備週轉(次)'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=3),
        marker=dict(size=8),
        text=selected_rows_t_4q['近四季累積不動產、廠房及設備週轉(次)'],   
        textposition='top center',  
    ))

    #
    min1 = selected_rows_t_4q['近四季累積不動產、廠房及設備週轉(次)'].min()
    max1 = selected_rows_t_4q['近四季累積不動產、廠房及設備週轉(次)'].max()
    y_range = [min1-1, max1+1]

    fig02.update_layout(
        title=f'近四季累積不動產、廠房及設備週轉(次)',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='不動產、廠房及設備週轉(次)', range=y_range),
        legend=dict(title='不動產、廠房及設備週轉(次)',
                    x=1.0,
                    y=1.4,
                    traceorder='normal',
                    orientation='v'), 
            width = 900,
            height = 400
        )

    # fig2.show()

    if not selected_rows_t_4q['不動產、廠房及設備'].iloc[-1] == 0:
        return fig01, fig02
    else:
        pass



 

    
#%%
# 009 包成def
# 償債能力 debt-paying ability 
# 流動比率 current ratio = 流動資產 / 流動負債 
# 速動比率 quick ratio= （流動資產 - 存貨 - 預付費用）/ 流動負債 
# 利息保障倍數 = 所得稅及利息費用前純益 /  本期利息支出

def plotly_debt_paying_ability(dfs):

    data_dpa = []

    # 迴圈遍歷所有的 dfs
    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                            '流動資產合計': 0,
                            '流動負債合計': 0,
                            '存貨': 0,
                            '預付款項': 0,
                        }
            
            try:
                # 確保是資產負債表(_bs)的資料
                row_data['流動資產合計'] = value.loc['流動資產合計', value.columns[0]]
                row_data['流動負債合計'] = value.loc['流動負債合計', value.columns[0]]
                
                try:
                    row_data['存貨']  = value.loc['應收帳款淨額', value.columns[0]]
                except KeyError:
                    pass
                    
                try:
                    row_data['預付款項']  = value.loc['預付款項', value.columns[0]]
                except KeyError:
                    pass
                
                row_data['流動比率'] = round(row_data['流動資產合計'] / row_data['流動負債合計'], 2)
                row_data['速動比率'] = round((row_data['流動資產合計'] - row_data['存貨'] - row_data['預付款項']) / row_data['流動負債合計'], 2)
    
                
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            data_dpa.append(row_data)

    # 將資料轉成 DataFrame
    result_df_dpa = pd.DataFrame(data_dpa)
    
    
    # 
    result_df_dpa['年份'] = result_df_dpa['年份-季度'].str[:3]
    result_df_dpa['季度'] = result_df_dpa['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_dpa['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_dpa[result_df_dpa['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_dpa[(result_df_dpa['年份'] == year) & (result_df_dpa['季度'] == '1')].empty and
                result_df_dpa[(result_df_dpa['年份'] == year) & (result_df_dpa['季度'] == '2')].empty and
                result_df_dpa[(result_df_dpa['年份'] == year) & (result_df_dpa['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_dpa[result_df_dpa['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_dpa[(result_df_dpa['年份'] == year) & (result_df_dpa['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_dpa[(result_df_dpa['年份'] == year) & (result_df_dpa['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_dpa[result_df_dpa['年份'] == year]])

        elif count == 2:
            if (result_df_dpa[(result_df_dpa['年份'] == year) & (result_df_dpa['季度'] == '3')].empty and
                result_df_dpa[(result_df_dpa['年份'] == year) & (result_df_dpa['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_dpa[result_df_dpa['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_dpa[(result_df_dpa['年份'] == year) & (result_df_dpa['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_dpa[(result_df_dpa['年份'] == year) & (result_df_dpa['季度'] == '4')]])

        elif count == 1:
            if not result_df_dpa[(result_df_dpa['年份'] == year) & (result_df_dpa['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_dpa[result_df_dpa['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)


    # 
    selected_rows['流動比率_調整'] = selected_rows['流動比率']
    selected_rows['速動比率_調整'] = selected_rows['速動比率']

    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '流動比率_調整'] = selected_rows.loc[i,'流動比率']
            selected_rows.loc[i, '速動比率_調整'] = selected_rows.loc[i,'速動比率']

            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '流動比率_調整']  = np.nan
            selected_rows.loc[i, '流動比率_調整']  = np.nan
            selected_rows.loc[i-1, '速動比率_調整']  = np.nan
            selected_rows.loc[i, '速動比率_調整']  = np.nan

    selected_rows['近四季平均流動比率'] = round(selected_rows['流動比率_調整'].rolling(window=4).mean() ,3)
    selected_rows['近四季平均速動比率'] = round(selected_rows['速動比率_調整'].rolling(window=4).mean(), 3) 


    # 
    fig = go.Figure()

    selected_rows['is_below_1'] = selected_rows['流動比率'] < 1
    selected_rows['is_below_11'] = selected_rows['速動比率'] < 1

    # 
    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['流動比率'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.2),
        marker_color=['red' if below_1 else 'mediumturquoise' for below_1 in selected_rows['is_below_1']],
        text=selected_rows['流動比率'],
        textposition='top center',
        name='流動比率',
        showlegend=False  # 隱藏 trace 的 legend
    ))

    # 
    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['速動比率'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        marker_color=['red' if below_11 else 'blue' for below_11 in selected_rows['is_below_11']],
        text=selected_rows['速動比率'],
        textposition='top center',
        yaxis='y2',
        name='速動比率',
        showlegend=False  # 隱藏 trace 的 legend
    ))

    min1=selected_rows['流動比率'].min()
    min2=selected_rows['速動比率'].min()
    max1=selected_rows['流動比率'].max()
    max2=selected_rows['速動比率'].max()
    y_range = [min(min1,min2)-1, max(max1,max2)+1]


    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
        
    fig.update_layout(
        title=f'前{year_difference}年各季度償債能力: 流動比率、速動比率',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='流動比率', range=y_range),
        yaxis2=dict(title='速動比率', overlaying='y', side='right', range=y_range),
        legend=dict(
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v',
        ),
        width=1000,
        height=400
    )

    # 自定的 legend
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=10, color='mediumturquoise'),
        legendgroup='group1',
        name='流動比率'
    ))

    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=10, color='blue'),
        legendgroup='group2',
        name='速動比率'
    ))

    # fig.show()



    # 
    fig2 = go.Figure()

    selected_rows['is_below_1'] = selected_rows['流動比率'] < 1
    selected_rows['is_below_11'] = selected_rows['速動比率'] < 1

    # 
    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均流動比率'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.2),
        marker_color=['red' if below_1 else 'mediumturquoise' for below_1 in selected_rows['is_below_1']],
        text=selected_rows['近四季平均流動比率'],
        textposition='top center',
        name='流動比率',
        showlegend=False  # 隱藏 trace 的 legend
    ))

    # 
    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均速動比率'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        marker_color=['red' if below_11 else 'blue' for below_11 in selected_rows['is_below_11']],
        text=selected_rows['近四季平均速動比率'],
        textposition='top center',
        yaxis='y2',
        name='速動比率',
        showlegend=False  # 隱藏 trace 的 legend
    ))

    min1=selected_rows['近四季平均流動比率'].min()
    min2=selected_rows['近四季平均流動比率'].min()
    max1=selected_rows['近四季平均速動比率'].max()
    max2=selected_rows['近四季平均速動比率'].max()
    y_range = [min(min1,min2)-1, max(max1,max2)+1]


    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
        
    fig2.update_layout(
        title=f'近四季平均流動比率、速動比率',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='流動比率', range=y_range),
        yaxis2=dict(title='速動比率', overlaying='y', side='right', range=y_range),
        legend=dict(
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v',
        ),
        width=1000,
        height=400
    )

    # 自定 legend
    fig2.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=10, color='mediumturquoise'),
        legendgroup='group1',
        name='流動比率'
    ))

    fig2.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=10, color='blue'),
        legendgroup='group2',
        name='速動比率'
    ))

    # fig2.show()

  
    
    average_current_ratio = round(selected_rows['近四季平均流動比率'].iloc[-1], 2)
    average_quick_ratio = round(selected_rows['近四季平均速動比率'].iloc[-1], 2)
    return fig, fig2, average_current_ratio, average_quick_ratio 


    
    

#%%
# 010 包成def
# 賦稅優勢
# 銀行業ok、有些繼續營業單位稅前損益要改 

def plotly_tax(dfs):

    data_tax = []

    # 
    for key, value in dfs.items():
        if key.endswith('_is'):
            row_data = {'年份-季度': key[5:10], 
                                '稅前淨利（淨損）': 0,
                                '本期淨利（淨損）': 0
                            }
            
            try:
                # 
                row_data['稅前淨利（淨損）'] = (
                                value.at['稅前淨利（淨損）', value.columns[0]]
                                if '稅前淨利（淨損）' in value.index
                                else (
                                    value.at['繼續營業單位稅前損益', value.columns[0]]
                                    if '繼續營業單位稅前損益' in value.index
                                    else (
                                        value.at['繼續營業單位稅前淨利（淨損）', value.columns[0]]
                                        if '繼續營業單位稅前淨利（淨損）' in value.index
                                        else (
                                            value.at['繼續營業單位稅前純益（純損）', value.columns[0]]
                                            if '繼續營業單位稅前純益（純損）' in value.index
                                            else 0
                                        )
                                    )
                                )
                            )

                row_data['本期淨利（淨損）']  = value.at['本期淨利（淨損）', value.columns[0]] if '本期淨利（淨損）' in value.index else value.at['本期稅後淨利（淨損）', value.columns[0]]

            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            # 
            data_tax.append(row_data)

    # 
    result_df_tax = pd.DataFrame(data_tax)
    
    
    
    # 
    result_df_tax['年份'] = result_df_tax['年份-季度'].str[:3]
    result_df_tax['季度'] = result_df_tax['年份-季度'].str[-1:]


    # 計算每個年份出現的次數
    year_counts = result_df_tax['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_tax[result_df_tax['年份'] == year]])
                
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_tax[(result_df_tax['年份'] == year) & (result_df_tax['季度'] == '1')].empty and
                result_df_tax[(result_df_tax['年份'] == year) & (result_df_tax['季度'] == '2')].empty and
                result_df_tax[(result_df_tax['年份'] == year) & (result_df_tax['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_tax[result_df_tax['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_tax[(result_df_tax['年份'] == year) & (result_df_tax['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_tax[(result_df_tax['年份'] == year) & (result_df_tax['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_tax[result_df_tax['年份'] == year]])


        elif count == 2:
            if (result_df_tax[(result_df_tax['年份'] == year) & (result_df_tax['季度'] == '3')].empty and
                result_df_tax[(result_df_tax['年份'] == year) & (result_df_tax['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_tax[result_df_tax['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_tax[(result_df_tax['年份'] == year) & (result_df_tax['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_tax[(result_df_tax['年份'] == year) & (result_df_tax['季度'] == '4')]])

                
        elif count == 1:
            if not result_df_tax[(result_df_tax['年份'] == year) & (result_df_tax['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_tax[result_df_tax['年份'] == year]])


    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)


    
    # 單季

    selected_rows['稅前淨利（淨損）_調整'] = selected_rows['稅前淨利（淨損）']
    selected_rows['本期淨利（淨損）_調整'] = selected_rows['本期淨利（淨損）']

    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '稅前淨利（淨損）_調整'] -= selected_rows.loc[i-3:i-1, '稅前淨利（淨損）'].sum()
            selected_rows.loc[i, '本期淨利（淨損）_調整'] -= selected_rows.loc[i-3:i-1, '本期淨利（淨損）'].sum()

            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '稅前淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i, '稅前淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i-1, '本期淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i, '本期淨利（淨損）_調整']  = np.nan


    # 
    selected_rows['賦稅優勢'] = round(selected_rows['本期淨利（淨損）_調整'] / selected_rows['稅前淨利（淨損）_調整'], 2)


    # 
    selected_rows_t_4q = selected_rows.copy()

    selected_rows_t_4q['近四季平均賦稅優勢'] = round(selected_rows_t_4q['賦稅優勢'].rolling(window=4).mean(), 2)

    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季平均賦稅優勢'] = round(selected_rows_t_4q.loc[i, '本期淨利（淨損）'] / selected_rows_t_4q.loc[i, '稅前淨利（淨損）'], 2)
            selected_rows_t_4q.loc[i-1, '近四季平均賦稅優勢'] = round(selected_rows_t_4q.loc[i-1, '本期淨利（淨損）'] / selected_rows_t_4q.loc[i-1, '稅前淨利（淨損）'], 2)


    # 
    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['賦稅優勢'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        text=selected_rows_t_4q['賦稅優勢'],
        textposition='top center',
        name='賦稅優勢',
    ))

    # 
    last_year = int(selected_rows_t_4q['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows_t_4q['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1

    min1 = selected_rows_t_4q['賦稅優勢'].min()
    max1 = selected_rows_t_4q['賦稅優勢'].max()
    y_range = [min1-0.1, max1+0.1]

    fig.update_layout(
        title=f'前{year_difference}各季度賦稅優勢<br>\
與同業比，越高越好',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='賦稅優勢', range=y_range),
        legend=dict(
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'), 
        width = 900,
        height = 400
    )



    # fig.show()
    
    
    # 
    fig2 = go.Figure()


    fig2.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均賦稅優勢'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        text=selected_rows_t_4q['近四季平均賦稅優勢'],
        textposition='top center',
        name='近四季平均賦稅優勢',
    ))

    # 
    min1 = selected_rows_t_4q['近四季平均賦稅優勢'].min()
    max1 = selected_rows_t_4q['近四季平均賦稅優勢'].max()
    y_range = [min1-0.1, max1+0.1]

    fig2.update_layout(
        title=f'近四季平均賦稅優勢',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='賦稅優勢', range=y_range),
        legend=dict(
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'), 
        width = 900,
        height = 400
    )



    # fig2.show()

    return fig, fig2
    



#%%
# 001 包成def
# ocf icf fcf

def plotly_ocf_icf_fcf(dfs):

    data_ocf = []

    for key, value in dfs.items():
        if key.endswith('_cfs'):
            
            row_data = {'年份-季度': key[5:10], 
                                    '營業活動之淨現金流入（流出）': 0,
                                    '投資活動之淨現金流入（流出）': 0,
                                    '籌資活動之淨現金流入（流出）': 0
                                }
            try:
                # 好公司投資活動應該是負的，專注於投資本業持續投資；
                # 如果是正的，賣祖產換現金
                
                # 籌資活動如果是正的，對外找錢成功，可能是透過銀行貸款、公司債、股東增資...；
                # 如果是負的，可能是還銀行錢、贖回公司債、減資、分紅...
                
                row_data['營業活動之淨現金流入（流出）'] = value.loc['營業活動之淨現金流入（流出）', value.columns[0]] 
                row_data['投資活動之淨現金流入（流出）']  = value.loc['投資活動之淨現金流入（流出）', value.columns[0]] 
                row_data['籌資活動之淨現金流入（流出）']  = value.loc['籌資活動之淨現金流入（流出）', value.columns[0]] 
                
                
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
            
        
            data_ocf.append(row_data)
            
    result_df_ocf = pd.DataFrame(data_ocf)
    
    
    # 
    result_df_ocf['年份'] = result_df_ocf['年份-季度'].str[:3]
    result_df_ocf['季度'] = result_df_ocf['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_ocf['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_ocf[result_df_ocf['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if not (result_df_ocf[(result_df_ocf['年份'] == year) & (result_df_ocf['季度'] == '1')].empty and
                result_df_ocf[(result_df_ocf['年份'] == year) & (result_df_ocf['季度'] == '2')].empty and
                result_df_ocf[(result_df_ocf['年份'] == year) & (result_df_ocf['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_ocf[result_df_ocf['年份'] == year]])
        

        elif count == 2:
            if (result_df_ocf[(result_df_ocf['年份'] == year) & (result_df_ocf['季度'] == '3')].empty and
                result_df_ocf[(result_df_ocf['年份'] == year) & (result_df_ocf['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_ocf[result_df_ocf['年份'] == year]])
                

        elif count == 1:
            if not result_df_ocf[(result_df_ocf['年份'] == year) & (result_df_ocf['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_ocf[result_df_ocf['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)



    # 
    # 創建新的調整欄位
    # selected_rows['營業活動之淨現金流入（流出）_調整'] = 0.0
    # selected_rows['投資活動之淨現金流入（流出）_調整'] = 0.0
    # selected_rows['籌資活動之淨現金流入（流出）_調整'] = 0.0
    selected_rows['營業活動之淨現金流入（流出）_調整'] = selected_rows['營業活動之淨現金流入（流出）']
    selected_rows['投資活動之淨現金流入（流出）_調整'] = selected_rows['投資活動之淨現金流入（流出）']
    selected_rows['籌資活動之淨現金流入（流出）_調整'] = selected_rows['籌資活動之淨現金流入（流出）']

    # 根據季度進行調整
    for i in range(1, len(selected_rows)):
        quarter = int(selected_rows.loc[i, '季度'])
        
        if quarter == 1:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] 
            selected_rows.loc[i, '投資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '投資活動之淨現金流入（流出）'] 
            selected_rows.loc[i, '籌資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '籌資活動之淨現金流入（流出）'] 
        
        elif quarter == 2:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
            selected_rows.loc[i, '投資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '投資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '投資活動之淨現金流入（流出）']
            selected_rows.loc[i, '籌資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '籌資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '籌資活動之淨現金流入（流出）']
        
        elif quarter == 3:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
            selected_rows.loc[i, '投資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '投資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '投資活動之淨現金流入（流出）']
            selected_rows.loc[i, '籌資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '籌資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '籌資活動之淨現金流入（流出）']

        elif quarter == 4:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
            selected_rows.loc[i, '投資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '投資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '投資活動之淨現金流入（流出）']
            selected_rows.loc[i, '籌資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '籌資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '籌資活動之淨現金流入（流出）']
        
            
            
    # 重新設定索引
    selected_rows.reset_index(drop=True, inplace=True)


    selected_rows['近四季平均營業活動之淨現金流入（流出）_調整'] = selected_rows['營業活動之淨現金流入（流出）_調整'].rolling(window=4).mean()
    selected_rows['近四季平均投資活動之淨現金流入（流出）_調整'] = selected_rows['投資活動之淨現金流入（流出）_調整'].rolling(window=4).mean()
    selected_rows['近四季平均籌資活動之淨現金流入（流出）_調整'] = selected_rows['籌資活動之淨現金流入（流出）_調整'].rolling(window=4).mean()

    # 與去年同期比較
    selected_rows['營業活動之淨現金流入（流出）_調整_比較'] = round(selected_rows['營業活動之淨現金流入（流出）_調整'] / 100000 ,2)
    # selected_rows['與去年同期營業活動成長率'] = round(selected_rows['營業活動之淨現金流入（流出）_調整_比較'] / selected_rows['營業活動之淨現金流入（流出）_調整_比較'].shift(4) - 1,2)
    selected_rows['去年同期營業活動'] = round(selected_rows['營業活動之淨現金流入（流出）_調整_比較'].shift(4),2)



    # 
    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['營業活動之淨現金流入（流出）_調整'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        # text=result_df['營業活動之淨現金流入（流出）_調整'],
        textposition='top center',
        name='營業活動'
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['投資活動之淨現金流入（流出）_調整'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2),
        yaxis='y2',   
        # text=result_df['投資活動之淨現金流入（流出）_調整'],
        textposition='top center',
        name='投資活動'
    ))


    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['籌資活動之淨現金流入（流出）_調整'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y3',   
        # text=result_df['籌資活動之淨現金流入（流出）_調整'],
        textposition='top center',
        name='籌資活動'
    ))


    # 
    max1 = selected_rows['營業活動之淨現金流入（流出）_調整'].max()
    max2 = selected_rows['投資活動之淨現金流入（流出）_調整'].max()
    max3 = selected_rows['籌資活動之淨現金流入（流出）_調整'].max()

    min1 = selected_rows['營業活動之淨現金流入（流出）_調整'].min()
    min2 = selected_rows['投資活動之淨現金流入（流出）_調整'].min()
    min3 = selected_rows['籌資活動之淨現金流入（流出）_調整'].min()

    min_y = min(min1,min2,min3)
    max_y = max(max1,max2,max3)
    y_range = [min_y - 100000, max_y + 100000]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
        
    fig.update_layout(
        title=f'近{year_difference}年各季度現金流量<br>\
營業活動正的，賺錢；負的，賠錢<br>\
投資活動正的，變賣資產；負的，投資自己，持續擴張<br>\
融資活動正的，借錢；負的，還錢、減資...',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='',range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        yaxis3=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(
            title='現金流量',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=1000,
        height=400,
    )

    # fig.show()

    
    
    
    # 
    fig2 = go.Figure()


    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均營業活動之淨現金流入（流出）_調整'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        # text=result_df['近四季平均營業活動之淨現金流入（流出）_調整'],
        textposition='top center',
        name='營業活動'
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均投資活動之淨現金流入（流出）_調整'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2),
        yaxis='y2',   
        # text=result_df['近四季平均投資活動之淨現金流入（流出）_調整'],
        textposition='top center',
        name='投資活動'
    ))


    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均籌資活動之淨現金流入（流出）_調整'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y3',   
        # text=result_df['近四季平均籌資活動之淨現金流入（流出）_調整'],
        textposition='top center',
        name='籌資活動'
    ))


    # 
    max1 = selected_rows['近四季平均營業活動之淨現金流入（流出）_調整'].max()
    max2 = selected_rows['近四季平均投資活動之淨現金流入（流出）_調整'].max()
    max3 = selected_rows['近四季平均籌資活動之淨現金流入（流出）_調整'].max()

    min1 = selected_rows['近四季平均營業活動之淨現金流入（流出）_調整'].min()
    min2 = selected_rows['近四季平均投資活動之淨現金流入（流出）_調整'].min()
    min3 = selected_rows['近四季平均籌資活動之淨現金流入（流出）_調整'].min()

    min_y = min(min1,min2,min3)
    max_y = max(max1,max2,max3)
    y_range = [min_y - 100000, max_y + 100000]


    fig2.update_layout(
        title=f'近四季平均現金流量',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='',range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        yaxis3=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(
            title='現金流量',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=1000,
        height=400,
    )

    # fig2.show()



    # 
    # 去年同期

    fig3 = go.Figure()

    fig3.add_trace(go.Bar(
        x=selected_rows['年份-季度'], 
        y=selected_rows['營業活動之淨現金流入（流出）_調整_比較'], 
        text=selected_rows['營業活動之淨現金流入（流出）_調整_比較'].astype(str)+"(億)",
        name='營業活動', width=0.41, 
        marker=dict(color='mediumturquoise')))

    fig3.add_trace(go.Bar(
        x=selected_rows['年份-季度'], 
        y=selected_rows['去年同期營業活動'], 
        text=selected_rows['去年同期營業活動'].astype(str)+"(億)",
        name='去年同期營業活動', width=0.41, 
        marker=dict(color='pink')))


    # 

    max1 = selected_rows['營業活動之淨現金流入（流出）_調整_比較'].max()
    min1 = selected_rows['營業活動之淨現金流入（流出）_調整_比較'].min()

    y_range = [min1-0.2, max1+0.2]

        
    fig3.update_layout(
        title=f'營業活動現金流量比較',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='',range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right',range=y_range),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig3.show()
        
    return fig, fig2, fig3






#%%
# 001-2 包成def
# ocf ni 比較 plotly_ocf_ni


def plotly_ocf_ni(dfs):

    data_ocf_com = []

    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                                    '流動負債合計': 0,
                                    '非流動資產合計': 0,
                                    '營業活動之淨現金流入（流出）': 0,
                                    '本期淨利（淨損）': 0
                                }
            try:
                
                row_data['流動負債合計'] = value.loc['流動負債合計', value.columns[0]] 
                row_data['非流動資產合計']  = value.loc['非流動資產合計', value.columns[0]] 
                                
                # 尋找對應的損益表(_is)資料
                is_key = key.replace('_bs', '_is')
                if is_key in dfs:
                    row_data['本期淨利（淨損）'] = dfs[is_key].loc['本期淨利（淨損）', dfs[is_key].columns[0]]
                else:
                    raise ValueError(f'找不到對應的損益表 ({is_key}) 資料')
                
                # 尋找對應的損益表(_cfs)資料
                cfs_key = key.replace('_bs', '_cfs')
                if cfs_key in dfs:
                    row_data['營業活動之淨現金流入（流出）'] = dfs[cfs_key].loc['營業活動之淨現金流入（流出）', dfs[cfs_key].columns[0]]
                else:
                    raise ValueError(f'找不到對應的現金流量表 ({cfs_key}) 資料')

            
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
            
        
            data_ocf_com.append(row_data)
            
    result_df_ocf_com = pd.DataFrame(data_ocf_com)
    
    
    
    # 
    result_df_ocf_com['年份'] = result_df_ocf_com['年份-季度'].str[:3]
    result_df_ocf_com['季度'] = result_df_ocf_com['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_ocf_com['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_ocf_com[result_df_ocf_com['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都不是空的，就提取
            if not (result_df_ocf_com[(result_df_ocf_com['年份'] == year) & (result_df_ocf_com['季度'] == '1')].empty and
                result_df_ocf_com[(result_df_ocf_com['年份'] == year) & (result_df_ocf_com['季度'] == '2')].empty and
                result_df_ocf_com[(result_df_ocf_com['年份'] == year) & (result_df_ocf_com['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_ocf_com[result_df_ocf_com['年份'] == year]])
        
        elif count == 2:
            if (result_df_ocf_com[(result_df_ocf_com['年份'] == year) & (result_df_ocf_com['季度'] == '3')].empty and
                result_df_ocf_com[(result_df_ocf_com['年份'] == year) & (result_df_ocf_com['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_ocf_com[result_df_ocf_com['年份'] == year]])
                
        elif count == 1:
            if not result_df_ocf_com[(result_df_ocf_com['年份'] == year) & (result_df_ocf_com['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_ocf_com[result_df_ocf_com['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)



    # 
    # 創建新的調整欄位
 
    selected_rows['營業活動之淨現金流入（流出）_調整'] = selected_rows['營業活動之淨現金流入（流出）']
    selected_rows['本期淨利（淨損）_調整'] = selected_rows['本期淨利（淨損）']


    # 根據季度進行調整
    for i in range(1, len(selected_rows)):
        quarter = int(selected_rows.loc[i, '季度'])
        
        if quarter == 1:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] 
    
        
        elif quarter == 2:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
    
        elif quarter == 3:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
    
        elif quarter == 4:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
            selected_rows.loc[i, '本期淨利（淨損）_調整'] -= selected_rows.loc[i-3:i-1, '本期淨利（淨損）_調整'].sum()

    selected_rows['獲利含金量%'] =  round(selected_rows['營業活動之淨現金流入（流出）_調整']/selected_rows['本期淨利（淨損）_調整']*100,2)
    
    selected_rows['近四季平均本期淨利（淨損）_調整'] =  round(selected_rows['本期淨利（淨損）_調整'].rolling(window=4).mean(),2)
    selected_rows['近四季平均營業活動之淨現金流入（流出）_調整'] =  round(selected_rows['營業活動之淨現金流入（流出）_調整'].rolling(window=4).mean(),2)
    selected_rows['近四季平均獲利含金量%'] =  round(selected_rows['獲利含金量%'].rolling(window=4).mean(),2)
    
    
    # 
    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['營業活動之淨現金流入（流出）_調整'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        # text=result_df['營業活動之淨現金流入（流出）'],
        textposition='top center',
        name='營業活動'
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['流動負債合計'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.2),
        yaxis='y2',   
        # text=result_df['流動負債合計'],
        textposition='top center',
        name='流動負債合計'
    ))


    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['非流動資產合計'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y3',   
        # text=result_df['非流動資產合計'],
        textposition='top center',
        name='非流動資產合計'
    ))

    # 
    max1 = selected_rows['營業活動之淨現金流入（流出）_調整'].max()
    max2 = selected_rows['流動負債合計'].max()
    max3 = selected_rows['非流動資產合計'].max()

    min1 = selected_rows['營業活動之淨現金流入（流出）_調整'].min()
    min2 = selected_rows['流動負債合計'].min()
    min3 = selected_rows['非流動資產合計'].min()

    min_y = min(min1,min2,min3)
    max_y = max(max1,max2,max3)
    y_range = [min_y - 100000, max_y + 100000]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
        
    fig.update_layout(
        title=f'前{year_difference}年各季度營業活動現金流量OCF比較',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='',range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        yaxis3=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig.show()


    # 
    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=selected_rows['年份-季度'], 
        y=selected_rows['獲利含金量%'], 
        name='獲利含金量%', width=0.3, 
        marker=dict(color='rgb(50, 225, 210)')))

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['營業活動之淨現金流入（流出）_調整'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y2',   
        # text=result_df['營業活動之淨現金流入（流出_調整'],
        textposition='top center',
        name='營業活動'
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['本期淨利（淨損）_調整'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y3',   
        # text=result_df['近四季累積本期淨利（淨損）_調整'],
        textposition='top center',
        name='淨利'
    ))


    # 
    max0 = selected_rows['獲利含金量%'].max()
    min0 = selected_rows['獲利含金量%'].min()
    y_range0 = [min0-10, max0+20]



    max1 = selected_rows['營業活動之淨現金流入（流出）_調整'].max()
    max2 = selected_rows['本期淨利（淨損）_調整'].max()

    min1 = selected_rows['營業活動之淨現金流入（流出）_調整'].min()
    min2 = selected_rows['本期淨利（淨損）_調整'].min()

    min_y = min(min1,min2)
    max_y = max(max1,max2)
    y_range = [min_y - 10000, max_y + 10000]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1

        
    fig2.update_layout(
        title=f'前{year_difference}年各季度營業活動現金流量OCF、淨利NI比較',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='獲利含金量%', range=y_range0),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        yaxis3=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig2.show()
    
    
    
    # 
    fig3 = go.Figure()

    fig3.add_trace(go.Bar(
        x=selected_rows['年份-季度'], 
        y=selected_rows['近四季平均獲利含金量%'], 
        name='獲利含金量%', width=0.3, 
        marker=dict(color='rgb(50, 225, 210)')))

    fig3.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均營業活動之淨現金流入（流出）_調整'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y2',   
        # text=result_df['近四季平均營業活動之淨現金流入（流出_調整'],
        textposition='top center',
        name='營業活動'
    ))

    fig3.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均本期淨利（淨損）_調整'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y3',   
        # text=result_df['近四季平均本期淨利（淨損）_調整'],
        textposition='top center',
        name='淨利'
    ))


    # 
    max0 = selected_rows['近四季平均獲利含金量%'].max()
    min0 = selected_rows['近四季平均獲利含金量%'].min()
    y_range0 = [min0-10, max0+20]



    max1 = selected_rows['近四季平均營業活動之淨現金流入（流出）_調整'].max()
    max2 = selected_rows['近四季平均本期淨利（淨損）_調整'].max()

    min1 = selected_rows['近四季平均營業活動之淨現金流入（流出）_調整'].min()
    min2 = selected_rows['近四季平均本期淨利（淨損）_調整'].min()

    min_y = min(min1,min2)
    max_y = max(max1,max2)
    y_range = [min_y - 50000, max_y + 50000]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1

        
    fig3.update_layout(
        title=f'近四季平均營業活動現金流量OCF、淨利NI比較',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='獲利含金量%', range=y_range0),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        yaxis3=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig3.show()
        
    return fig, fig2, fig3





#%%
# 001-3 包成def
# 淨現金流量 net cash flow: ofc+icf+fci (直接反映一間公司錢是流出去多or流進來多)
# 自由現金流量 Free cash flow : ocf-icf (公司可以自由運用的現金
# 一間好公司自由現金流量應該要是正的，代表公司擴張，都能帶回營運的現金) 5/8要是正的
# 銀行業ok不用調

def plotly_net_free_cash_flow(dfs):

    data_cfs = []

    for key, value in dfs.items():
        if key.endswith('_cfs'):
            try:
                row_data = {'年份-季度': key[5:10], 
                                        '營業活動之淨現金流入（流出）': 0,
                                        '投資活動之淨現金流入（流出）': 0,
                                        '籌資活動之淨現金流入（流出）': 0,
                                        '淨現金流量': 0,
                                        '自由現金流量': 0
                                    }
                
                row_data['營業活動之淨現金流入（流出）'] = value.loc['營業活動之淨現金流入（流出）', value.columns[0]] 
                row_data['投資活動之淨現金流入（流出）']  = value.loc['投資活動之淨現金流入（流出）', value.columns[0]] 
                row_data['籌資活動之淨現金流入（流出）']  = value.loc['籌資活動之淨現金流入（流出）', value.columns[0]] 
                row_data['淨現金流量']  = row_data['營業活動之淨現金流入（流出）'] + row_data['投資活動之淨現金流入（流出）']  + row_data['籌資活動之淨現金流入（流出）'] 
                row_data['自由現金流量'] = row_data['營業活動之淨現金流入（流出）'] + row_data['投資活動之淨現金流入（流出）'] 

                
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
            
            data_cfs.append(row_data)
            
    result_df_cfs = pd.DataFrame(data_cfs)


    # 
    result_df_cfs['年份'] = result_df_cfs['年份-季度'].str[:3]
    result_df_cfs['季度'] = result_df_cfs['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_cfs['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_cfs[result_df_cfs['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都不是空的，就提取
            if not (result_df_cfs[(result_df_cfs['年份'] == year) & (result_df_cfs['季度'] == '1')].empty and
                result_df_cfs[(result_df_cfs['年份'] == year) & (result_df_cfs['季度'] == '2')].empty and
                result_df_cfs[(result_df_cfs['年份'] == year) & (result_df_cfs['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_cfs[result_df_cfs['年份'] == year]])
            
        elif count == 2:
            if (result_df_cfs[(result_df_cfs['年份'] == year) & (result_df_cfs['季度'] == '3')].empty and
                result_df_cfs[(result_df_cfs['年份'] == year) & (result_df_cfs['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_cfs[result_df_cfs['年份'] == year]])
                
        elif count == 1:
            if not result_df_cfs[(result_df_cfs['年份'] == year) & (result_df_cfs['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_cfs[result_df_cfs['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)


    # 
    selected_rows['營業活動之淨現金流入（流出）_調整'] = selected_rows['營業活動之淨現金流入（流出）']
    selected_rows['投資活動之淨現金流入（流出）_調整'] = selected_rows['投資活動之淨現金流入（流出）']
    selected_rows['籌資活動之淨現金流入（流出）_調整'] = selected_rows['籌資活動之淨現金流入（流出）']

    # 根據季度進行調整
    for i in range(1, len(selected_rows)):
        quarter = int(selected_rows.loc[i, '季度'])
        
        if quarter == 1:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] 
            selected_rows.loc[i, '投資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '投資活動之淨現金流入（流出）'] 
            selected_rows.loc[i, '籌資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '籌資活動之淨現金流入（流出）'] 
        
        elif quarter == 2:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
            selected_rows.loc[i, '投資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '投資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '投資活動之淨現金流入（流出）']
            selected_rows.loc[i, '籌資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '籌資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '籌資活動之淨現金流入（流出）']
        
        elif quarter == 3:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
            selected_rows.loc[i, '投資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '投資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '投資活動之淨現金流入（流出）']
            selected_rows.loc[i, '籌資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '籌資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '籌資活動之淨現金流入（流出）']

        elif quarter == 4:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
            selected_rows.loc[i, '投資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '投資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '投資活動之淨現金流入（流出）']
            selected_rows.loc[i, '籌資活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '籌資活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '籌資活動之淨現金流入（流出）']
        
    selected_rows['淨現金流量(億)']  = round((selected_rows['營業活動之淨現金流入（流出）_調整'] + selected_rows['投資活動之淨現金流入（流出）_調整']  + selected_rows['籌資活動之淨現金流入（流出）_調整']) /10000,2)
    selected_rows['自由現金流量(億)'] = round((selected_rows['營業活動之淨現金流入（流出）_調整'] + selected_rows['投資活動之淨現金流入（流出）_調整']) /10000,2)

    selected_rows['近四季平均淨現金流量(億)'] = selected_rows['淨現金流量(億)'].rolling(window=4).mean()
    selected_rows['近四季平均自由現金流量(億)'] = selected_rows['自由現金流量(億)'].rolling(window=4).mean()

    # 重新設定索引
    selected_rows.reset_index(drop=True, inplace=True)


    # 
    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['淨現金流量(億)'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.2),
        textposition='top center',
        name='淨現金流量(億)'
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['自由現金流量(億)'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y2',   
        textposition='top center',
        name='自由現金流量(億)'
    ))

    # 
    max1 = selected_rows['淨現金流量(億)'].max()
    max2 = selected_rows['自由現金流量(億)'].max()

    min1 = selected_rows['淨現金流量(億)'].min()
    min2 = selected_rows['自由現金流量(億)'].min()

    y_range = [min(min1,min2)-5,max(max1,max2)+5]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1


    last_8_rows2 = selected_rows['自由現金流量(億)'].tail(8)
    negative_count2 = last_8_rows2[last_8_rows2 < 0].count()
    positive_count2 = 8 - negative_count2

    fig.update_layout(
        title=f'前{year_difference}年各季度淨現金流量、自由現金流量(億)',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='',range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig.show()
    
    
    
    # 
    fig2 = go.Figure()


    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均淨現金流量(億)'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.2),
        textposition='top center',
        name='淨現金流量(億)'
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均自由現金流量(億)'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y2',   
        textposition='top center',
        name='自由現金流量(億)'
    ))

    # 
    max1 = selected_rows['近四季平均淨現金流量(億)'].max()
    max2 = selected_rows['近四季平均自由現金流量(億)'].max()

    min1 = selected_rows['近四季平均淨現金流量(億)'].min()
    min2 = selected_rows['近四季平均自由現金流量(億)'].min()

    y_range = [min(min1,min2)-5,max(max1,max2)+5]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1


    last_8_rows2 = selected_rows['近四季平均自由現金流量(億)'].tail(8)
    negative_count2 = last_8_rows2[last_8_rows2 < 0].count()
    positive_count2 = 8 - negative_count2

    fig2.update_layout(
        title=f'近四季平均淨現金流量、自由現金流量(億)',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='',range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig2.show()
    
    
    return fig, fig2, positive_count2 





#%%
# 002~004 包成def
# 現金流量關鍵
# 現金流量比率 = 營業活動淨現金流量 / 流動負債
# 現金流量允當比率 = 最近五年度營業活動淨現金流量 / 最近五年度（資本支出 + 存貨增加額 + 現金股利）
# 現金再投資比率 = （營業活動淨現金流量 - 現金股利） / （不動產、廠房及設備毛額 + 長期投資 + 其他非流動資產 + 營運資金）
# 銀行業不看

def plotly_cfr_3(dfs):

    data_cfr = []

    for key, value in dfs.items():
        if key.endswith('_bs'):
            try:
                row_data = {'年份-季度': key[5:10], 
                        '流動負債合計': 0,
                        '營業活動之淨現金流入（流出）': 0,
                        '發放現金股利': 0,
                        '現金流量比率%': 0
                    }
                
                # 確保是資產負債表(_bs)的資料
                row_data['流動負債合計'] = value.loc['流動負債合計', value.columns[0]]
                
                # 尋找對應的現金流量表(_cfs)資料
                cfs_key = key.replace('_bs', '_cfs')
                if cfs_key in dfs:
                    row_data['營業活動之淨現金流入（流出）']  = dfs[cfs_key].loc['營業活動之淨現金流入（流出）', dfs[cfs_key].columns[0]]
                    row_data['發放現金股利']  = dfs[cfs_key].loc['發放現金股利', dfs[cfs_key].columns[0]]

                else:
                    raise ValueError(f'找不到對應的現金流量表 ({cfs_key}) 資料')

            except Exception as e:
                print(f'計算 {key} 發生錯誤、沒有發放股利: {str(e)}')
                
            #
            row_data['現金流量比率%'] = round(row_data['營業活動之淨現金流入（流出）'] /row_data['流動負債合計']*100,2)
            data_cfr.append(row_data)

    # 將資料轉成 DataFrame
    result_df_cfr = pd.DataFrame(data_cfr)


    # 
    result_df_cfr['年份'] = result_df_cfr['年份-季度'].str[:3]
    result_df_cfr['季度'] = result_df_cfr['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_cfr['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_cfr[result_df_cfr['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都不是空的，就提取
            if not (result_df_cfr[(result_df_cfr['年份'] == year) & (result_df_cfr['季度'] == '1')].empty and
                result_df_cfr[(result_df_cfr['年份'] == year) & (result_df_cfr['季度'] == '2')].empty and
                result_df_cfr[(result_df_cfr['年份'] == year) & (result_df_cfr['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_cfr[result_df_cfr['年份'] == year]])
            
        elif count == 2:
            if (result_df_cfr[(result_df_cfr['年份'] == year) & (result_df_cfr['季度'] == '3')].empty and
                result_df_cfr[(result_df_cfr['年份'] == year) & (result_df_cfr['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_cfr[result_df_cfr['年份'] == year]])
                    
        elif count == 1:
            if not result_df_cfr[(result_df_cfr['年份'] == year) & (result_df_cfr['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_cfr[result_df_cfr['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)



    # 
    selected_rows['營業活動之淨現金流入（流出）_調整'] = selected_rows['營業活動之淨現金流入（流出）']

    # 根據季度進行調整
    for i in range(1, len(selected_rows)):
        quarter = int(selected_rows.loc[i, '季度'])
        
        if quarter == 1:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] 
        
        elif quarter == 2:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
        
        elif quarter == 3:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']
        
        elif quarter == 4:
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整'] = selected_rows.loc[i, '營業活動之淨現金流入（流出）'] - selected_rows.loc[i-1, '營業活動之淨現金流入（流出）']


    selected_rows['近四季累積營業活動之淨現金流入（流出）_調整'] = selected_rows['營業活動之淨現金流入（流出）_調整'].rolling(window=4).sum()
    selected_rows['現金流量比率%'] = round(selected_rows['近四季累積營業活動之淨現金流入（流出）_調整']/selected_rows['流動負債合計']*100 ,2)
    selected_rows['近四季平均現金流量比率%'] = round(selected_rows['現金流量比率%'].rolling(window=4).mean(),2)


    # 重新設定索引
    selected_rows.reset_index(drop=True, inplace=True)



    # 
    fig = go.Figure()

    selected_rows['is_below_100'] = selected_rows['現金流量比率%'] < 100

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['現金流量比率%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker_color=['red' if below_100 else 'mediumturquoise' for below_100 in selected_rows['is_below_100']],
        text=selected_rows['現金流量比率%'].astype(str)+'%',
        textposition='top center',
        name='現金流量比率%'
    ))


    #
    min1 = selected_rows['現金流量比率%'].min()
    max1 = selected_rows['現金流量比率%'].max()
    y_range = [min1-1,max1+1]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
        
    fig.update_layout(
        title=f'前{year_difference}年各季度現金流量比率',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='現金流量比率%',range=y_range),
        # yaxis2=dict(title='', overlaying='y', side='right', range=range),
        # yaxis3=dict(title='', overlaying='y', side='right', range=range),
        legend=dict(
            title='現金流量比率%',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig.show()


    # 
    fig2 = go.Figure()

    selected_rows['is_below_100'] = selected_rows['近四季平均現金流量比率%'] < 100

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均現金流量比率%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker_color=['red' if below_100 else 'mediumturquoise' for below_100 in selected_rows['is_below_100']],
        text=selected_rows['近四季平均現金流量比率%'].astype(str)+'%',
        textposition='top center',
        name='現金流量比率%'
    ))


    #
    min1 = selected_rows['近四季平均現金流量比率%'].min()
    max1 = selected_rows['近四季平均現金流量比率%'].max()
    y_range = [min1-1,max1+1]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
        
    fig2.update_layout(
        title=f'近四季平均現金流量比率',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='現金流量比率%',range=y_range),
        # yaxis2=dict(title='', overlaying='y', side='right', range=range),
        # yaxis3=dict(title='', overlaying='y', side='right', range=range),
        legend=dict(
            title='現金流量比率%',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig2.show()


    average_price_to_cash_flow_ratio = round(selected_rows['近四季平均現金流量比率%'].iloc[-1], 2)

    return fig, fig2, average_price_to_cash_flow_ratio





#%%
# 005 包成def 
# 現金佔比趨勢
# 現金最好佔總資產10~25%，資本密集行業最好更高
# 銀行業ok

def plotly_cashncash_equivalents(dfs):

    data_cce = []

    for key, value in dfs.items():
        if key.endswith('_bs'):
            
            row_data = {'年份-季度': key[5:10], 
                        '現金及約當現金': 0,
                        '資產總額': 0,
                        '現金佔比%': 0,
                    }
            
            try:
                # 計算負債總額佔資產總額的百分比
                row_data['現金及約當現金'] = value.loc['現金及約當現金', value.columns[0]] 
                row_data['資產總額'] = value.at['資產總額', value.columns[0]] if '資產總額' in value.index else value.at['資產總計', value.columns[0]]
                row_data['現金佔比%'] = round(row_data['現金及約當現金']/row_data['資產總額']*100 ,2) 
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
            
            data_cce.append(row_data)
                
    result_df_cce = pd.DataFrame(data_cce)


    # 
    result_df_cce['年份'] = result_df_cce['年份-季度'].str[:3]
    result_df_cce['季度'] = result_df_cce['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_cce['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_cce[result_df_cce['年份'] == year]])
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_cce[(result_df_cce['年份'] == year) & (result_df_cce['季度'] == '1')].empty and
                result_df_cce[(result_df_cce['年份'] == year) & (result_df_cce['季度'] == '2')].empty and
                result_df_cce[(result_df_cce['年份'] == year) & (result_df_cce['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_cce[result_df_cce['年份'] == year]])
                    
            # 4 不是空的，就提取
            elif not (result_df_cce[(result_df_cce['年份'] == year) & (result_df_cce['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_cce[(result_df_cce['年份'] == year) & (result_df_cce['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_cce[result_df_cce['年份'] == year]])

        elif count == 2:
            if (result_df_cce[(result_df_cce['年份'] == year) & (result_df_cce['季度'] == '3')].empty and
                result_df_cce[(result_df_cce['年份'] == year) & (result_df_cce['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_cce[result_df_cce['年份'] == year]])
                    
            # 4 不是空的，就提取
            elif not (result_df_cce[(result_df_cce['年份'] == year) & (result_df_cce['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_cce[(result_df_cce['年份'] == year) & (result_df_cce['季度'] == '4')]])

        elif count == 1:
            if result_df_cce[(result_df_cce['年份'] == year) & (result_df_cce['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_cce[result_df_cce['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)



    #   
    # 四季

    selected_rows['現金佔比%_調整'] = selected_rows['現金佔比%']


    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '現金佔比%_調整']  = np.nan
            selected_rows.loc[i, '現金佔比%_調整']  = np.nan

    selected_rows['近四季平均現金佔比%_調整'] = round(selected_rows['現金佔比%_調整'].rolling(window=4).mean(), 2)


    
    # 
    fig = go.Figure()

    selected_rows['is_above_10'] = selected_rows['現金佔比%'] < 10

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['現金佔比%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(
            color=['red' if above_10 else 'mediumturquoise' for above_10 in selected_rows['is_above_10']],
            size=8,
        ),
        text=selected_rows['現金佔比%'].astype(str)+'%',  
        textposition='top center',  
    ))

    #
    min1 = selected_rows['現金佔比%'].min()
    max1 = selected_rows['現金佔比%'].max()
    y_range = [min1-10, max1+10]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1

    fig.update_layout(
        title=f'前{year_difference}年各季度現金/總資產佔比',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='現金佔比%', range=y_range),
        legend=dict(title='現金佔比%',
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'), 
        width = 900,
        height = 400
    )



    # fig.show()


    # 
    fig2 = go.Figure()

    selected_rows['is_above_10'] = selected_rows['近四季平均現金佔比%_調整'] < 10

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均現金佔比%_調整'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker=dict(
            color=['red' if above_10 else 'mediumturquoise' for above_10 in selected_rows['is_above_10']],
            size=8,
        ),
        text=selected_rows['近四季平均現金佔比%_調整'].astype(str)+'%',  
        textposition='top center',  
    ))

    #
    min1 = selected_rows['近四季平均現金佔比%_調整'].min()
    max1 = selected_rows['近四季平均現金佔比%_調整'].max()
    y_range = [min1-10, max1+10]

    fig2.update_layout(
        title=f'近四季平均現金/總資產佔比',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='近四季平均現金佔比%', range=y_range),
        legend=dict(title='近四季平均現金佔比%',
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'), 
        width = 900,
        height = 400
    )

    # fig2.show()
    average_cashncash_equivalents = round(selected_rows['近四季平均現金佔比%_調整'].iloc[-1], 2)

    return fig, fig2, average_cashncash_equivalents







#%%
# 綜合損益表
# 001~004 包成def
# 財報三率
# 銀行業ok、有些繼續營業單位稅前損益要改、淨收益要改


def plotly_3_rate(dfs):

    data_3_rate = []

    for key, value in dfs.items():
        if key.endswith('_is'):
            row_data = {'年份-季度': key[5:10], 
                        '營業收入合計': 0,
                        '營業成本合計': 0,
                        '營業利益（損失）': 0,
                        '本期淨利（淨損）': 0,
                    }
            
            try:
                # 001: 毛利率 Gross Profit Margin (這是不是一門好生意? 和過去的自己、同業比)
                # 毛利 = 收入-成本
                # 只看產品，不看其他成本
                
                # 002: 營益率 Operating profit Margin (本業有沒有賺錢的真本事?
                # 如果分母(營業收入)很大，費用率通常會越低，公司規模越大)
                # 營業利益 = 收入-成本-營業費用(銷 管 研 折舊 分期攤銷)
                # 營業收入-營業成本= 營業費用，代表公司1元的營業收入能夠獲得多少利潤
                
                # 003: 費用率 =  毛利率-營益率，大公司大約10%，品牌公司通常>20%。看公司規模大小，先看費用率，再看營業收入
                
                # 004: 淨利率 Profit Margin，又稱「純益率」、「營業淨利率」 (有沒有賺錢?)
                # 一般指的是稅後淨利率
                
                row_data['營業收入合計'] = value.at['營業收入合計', value.columns[0]] if '營業收入合計' in value.index else value.at['淨收益', value.columns[0]] if '淨收益' in value.index else value.at['收益合計', value.columns[0]]
                row_data['營業成本合計'] = value.at['營業成本合計', value.columns[0]] if '營業成本合計' in value.index else np.nan
                row_data['營業利益（損失）'] = (
                                            value.at['營業利益（損失）', value.columns[0]]
                                            if '營業利益（損失）' in value.index
                                            else (
                                                value.at['繼續營業單位稅前損益', value.columns[0]]
                                                if '繼續營業單位稅前損益' in value.index
                                                else (
                                                    value.at['繼續營業單位稅前淨利（淨損）', value.columns[0]]
                                                    if '繼續營業單位稅前淨利（淨損）' in value.index
                                                    else value.at['營業利益', value.columns[0]]
                                                )
                                            )
                                        )
                row_data['本期淨利（淨損）'] = value.at['本期淨利（淨損）', value.columns[0]] if '本期淨利（淨損）' in value.index else value.at['本期稅後淨利（淨損）', value.columns[0]]
                
                
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
            
            data_3_rate.append(row_data)
            
                
    result_df_3_rate = pd.DataFrame(data_3_rate)
    
    
    # 
    result_df_3_rate['年份'] = result_df_3_rate['年份-季度'].str[:3]
    result_df_3_rate['季度'] = result_df_3_rate['年份-季度'].str[-1:]


    # 計算每個年份出現的次數
    year_counts = result_df_3_rate['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_3_rate[result_df_3_rate['年份'] == year]])
                
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_3_rate[(result_df_3_rate['年份'] == year) & (result_df_3_rate['季度'] == '1')].empty and
                result_df_3_rate[(result_df_3_rate['年份'] == year) & (result_df_3_rate['季度'] == '2')].empty and
                result_df_3_rate[(result_df_3_rate['年份'] == year) & (result_df_3_rate['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_3_rate[result_df_3_rate['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_3_rate[(result_df_3_rate['年份'] == year) & (result_df_3_rate['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_3_rate[(result_df_3_rate['年份'] == year) & (result_df_3_rate['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_3_rate[result_df_3_rate['年份'] == year]])


        elif count == 2:
            if (result_df_3_rate[(result_df_3_rate['年份'] == year) & (result_df_3_rate['季度'] == '3')].empty and
                result_df_3_rate[(result_df_3_rate['年份'] == year) & (result_df_3_rate['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_3_rate[result_df_3_rate['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_3_rate[(result_df_3_rate['年份'] == year) & (result_df_3_rate['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_3_rate[(result_df_3_rate['年份'] == year) & (result_df_3_rate['季度'] == '4')]])

                
        elif count == 1:
            if not result_df_3_rate[(result_df_3_rate['年份'] == year) & (result_df_3_rate['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_3_rate[result_df_3_rate['年份'] == year]])


    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)

    
    # 

    selected_rows_copy = selected_rows.copy()

    selected_rows_copy = selected_rows

    selected_rows_copy['營業收入合計_調整'] = selected_rows_copy['營業收入合計']
    selected_rows_copy['營業成本合計_調整'] = selected_rows_copy['營業成本合計']
    selected_rows_copy['營業利益（損失）_調整'] = selected_rows_copy['營業利益（損失）']
    selected_rows_copy['本期淨利（淨損）_調整'] = selected_rows_copy['本期淨利（淨損）']

    # 計算每個Q4的調整值
    total_rows = len(selected_rows_copy)

    for i in range(total_rows):
        if (selected_rows_copy.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows_copy.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows_copy.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows_copy.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows_copy.loc[i, '營業收入合計_調整'] -= selected_rows_copy.loc[i-3:i-1, '營業收入合計'].sum()
            selected_rows_copy.loc[i, '營業成本合計_調整'] -= selected_rows_copy.loc[i-3:i-1, '營業成本合計'].sum()
            selected_rows_copy.loc[i, '營業利益（損失）_調整'] -= selected_rows_copy.loc[i-3:i-1, '營業利益（損失）'].sum()
            selected_rows_copy.loc[i, '本期淨利（淨損）_調整'] -= selected_rows_copy.loc[i-3:i-1, '本期淨利（淨損）'].sum()
            
        elif (result_df_3_rate.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows_copy.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_copy.loc[i, '營業收入合計_調整'] = np.nan
            selected_rows_copy.loc[i-1, '營業收入合計_調整'] = np.nan
            selected_rows_copy.loc[i, '營業成本合計_調整'] = np.nan
            selected_rows_copy.loc[i-1, '營業成本合計_調整'] = np.nan
            selected_rows_copy.loc[i, '營業利益（損失）_調整'] = np.nan
            selected_rows_copy.loc[i-1, '營業利益（損失）_調整'] = np.nan
            selected_rows_copy.loc[i, '本期淨利（淨損）_調整'] = np.nan
            selected_rows_copy.loc[i-1, '本期淨利（淨損）_調整'] = np.nan

    # 
    selected_rows_copy['毛利率%'] = round( (selected_rows_copy['營業收入合計_調整'] - selected_rows_copy['營業成本合計_調整']) / selected_rows_copy['營業收入合計_調整'] * 100, 2) 
    selected_rows_copy['營益率%'] = round( selected_rows_copy['營業利益（損失）_調整'] / selected_rows_copy['營業收入合計_調整'] * 100, 2) 
    selected_rows_copy['費用率%'] = round(selected_rows_copy['毛利率%'] - selected_rows_copy['營益率%'] ,2 )
    selected_rows_copy['淨利率%'] = round( selected_rows_copy['本期淨利（淨損）_調整'] / selected_rows_copy['營業收入合計_調整'] * 100, 2) 


    # 
    # 單季table

    selected_rows_t = selected_rows_copy.transpose()

    # # 選擇 "年份-季度" 和 "ROE%" 這兩列
    selected_columns = ['年份-季度', '毛利率%','營益率%','費用率%','淨利率%']
    selected_rows_t = selected_rows_t[selected_rows_t.index.isin(selected_columns)]
    selected_rows_t.columns = selected_rows_t.iloc[0]
    try:
        selected_rows_t = selected_rows_t.iloc[:,-7:]
    except:
        pass

   
    
    # 
    table_data = selected_rows_t.loc[['毛利率%', '營益率%', '費用率%', '淨利率%'], :].reset_index()
    table_data = table_data.fillna('NaN')
    # table_data = table_data.dropna(axis=0)
    # table_data = table_data.dropna(axis=1)

    # 創建表格
    fig = ff.create_table(table_data, height_constant=30)

    # 
    fig.update_layout(
        title='單季財報三率',
        width=900,
        height=200,
    )

    # fig.show()
   
    
    # 
    selected_rows_t_4q = selected_rows_copy.copy()

    selected_rows_t_4q['近四季平均毛利率%'] = round(selected_rows_t_4q['毛利率%'].rolling(window=4).mean(),2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季平均毛利率%'] = round((selected_rows_t_4q.loc[i, '營業收入合計'] - selected_rows_t_4q.loc[i, '營業成本合計']) / selected_rows_t_4q.loc[i, '營業收入合計']*100 , 2)
            selected_rows_t_4q.loc[i-1, '近四季平均毛利率%'] = round((selected_rows_t_4q.loc[i-1, '營業收入合計'] - selected_rows_t_4q.loc[i-1, '營業成本合計']) / selected_rows_t_4q.loc[i-1, '營業收入合計']*100 , 2)


    selected_rows_t_4q['近四季平均營益率%'] = round(selected_rows_t_4q['營益率%'].rolling(window=4).mean(),2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季平均營益率%'] = round(selected_rows_t_4q.loc[i, '營業利益（損失）']/ selected_rows_t_4q.loc[i, '營業收入合計']*100 , 2)
            selected_rows_t_4q.loc[i-1, '近四季平均營益率%'] = round(selected_rows_t_4q.loc[i-1, '營業利益（損失）']/ selected_rows_t_4q.loc[i-1, '營業收入合計']*100 , 2)


    selected_rows_t_4q['近四季平均費用率%'] = selected_rows_t_4q['近四季平均毛利率%'] - selected_rows_t_4q['近四季平均營益率%']

    selected_rows_t_4q['近四季平均淨利率%'] = round(selected_rows_t_4q['淨利率%'].rolling(window=4).mean(),2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季平均淨利率%'] = round(selected_rows_t_4q.loc[i, '本期淨利（淨損）']/ selected_rows_t_4q.loc[i, '營業收入合計']*100 , 2)
            selected_rows_t_4q.loc[i-1, '近四季平均淨利率%'] = round(selected_rows_t_4q.loc[i-1, '本期淨利（淨損）']/ selected_rows_t_4q.loc[i-1, '營業收入合計']*100 , 2)

    
    # 
    # plotly color 
    # https://www.self-study-blog.com/dokugaku/python-plotly-color-sequence-scales/

    fig2 = go.Figure()

    y5 = selected_rows_t_4q['毛利率%'].min()
    y6 = selected_rows_t_4q['費用率%'].min()
    y7 = selected_rows_t_4q['毛利率%'].max()
    y8 = selected_rows_t_4q['費用率%'].max()
    y_range2 = [min(y5,y6)-15, max(y7,y8)+15]
    
    
    y1 = selected_rows_t_4q['營益率%'].min()
    y2 = selected_rows_t_4q['淨利率%'].min()
    y3 = selected_rows_t_4q['營益率%'].max()
    y4 = selected_rows_t_4q['淨利率%'].max()
    y_range1 = [min(y1,y2)-10, max(y3,y4)+10]



    fig2.add_trace(go.Bar(x=selected_rows_t_4q['年份-季度'], y=selected_rows_t_4q['毛利率%'], name='毛利率%', width=0.45, marker=dict(color='rgb(50, 225, 210)')))
    fig2.add_trace(go.Bar(x=selected_rows_t_4q['年份-季度'], y=selected_rows_t_4q['費用率%'], name='費用率%', width=0.45, marker=dict(color='#e78ac3')))
    fig2.add_trace(go.Scatter(x=selected_rows_t_4q['年份-季度'], y=selected_rows_t_4q['營益率%'], mode='lines', name='營益率%', yaxis='y3', marker=dict(color='blue')))
    fig2.add_trace(go.Scatter(x=selected_rows_t_4q['年份-季度'], y=selected_rows_t_4q['淨利率%'], mode='lines', name='淨利率%', yaxis='y4', marker=dict(color='red')))


    # 
    last_year = int(selected_rows_t_4q['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows_t_4q['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
        
    fig2.update_layout(
        title=f'前{year_difference}年各季度財報三率、費用率',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='毛利率%、費用率%',range=y_range2),
        yaxis2=dict(title='',range=y_range2),
        yaxis3=dict(title='淨利率%、營益率%', overlaying='y', side='right', range=y_range1),
        yaxis4=dict(title='淨利率%、營益率%', overlaying='y', side='right', range=y_range1),
        legend=dict(
                x=1.1,
                y=1.4,
                traceorder='normal',
                orientation='v'
            ),
        width=900,
        height=500,
    )

    # fig2.show()

    
    
    
    # 
    # plotly color 
    # https://www.self-study-blog.com/dokugaku/python-plotly-color-sequence-scales/


    fig3 = go.Figure()

    y55 = selected_rows_t_4q['近四季平均毛利率%'].min()
    y66 = selected_rows_t_4q['近四季平均費用率%'].min()
    y77 = selected_rows_t_4q['近四季平均毛利率%'].max()
    y88 = selected_rows_t_4q['近四季平均費用率%'].max()
    y_range22 = [min(y55,y66)-15, max(y77,y88)+15]
    
    y11 = selected_rows_t_4q['近四季平均營益率%'].min()
    y22 = selected_rows_t_4q['近四季平均淨利率%'].min()
    y33 = selected_rows_t_4q['近四季平均營益率%'].max()
    y44 = selected_rows_t_4q['近四季平均淨利率%'].max()
    y_range11 = [min(y11,y22)-10, max(y33,y44)+10]

    x1 = round(selected_rows_t_4q['近四季平均毛利率%'].iloc[-1],2)
    x2 = round(selected_rows_t_4q['近四季平均費用率%'].iloc[-1],2)
    x3 = round(selected_rows_t_4q['近四季平均營益率%'].iloc[-1],2)
    x4 = round(selected_rows_t_4q['近四季平均淨利率%'].iloc[-1],2)


    fig3.add_trace(go.Bar(x=selected_rows_t_4q['年份-季度'], y=selected_rows_t_4q['近四季平均毛利率%'], name='毛利率%', width=0.45, marker=dict(color='rgb(50, 225, 210)')))
    fig3.add_trace(go.Bar(x=selected_rows_t_4q['年份-季度'], y=selected_rows_t_4q['近四季平均費用率%'], name='費用率%', width=0.45, marker=dict(color='#e78ac3')))
    fig3.add_trace(go.Scatter(x=selected_rows_t_4q['年份-季度'], y=selected_rows_t_4q['近四季平均營益率%'], mode='lines', name='營益率%', yaxis='y3', marker=dict(color='blue')))
    fig3.add_trace(go.Scatter(x=selected_rows_t_4q['年份-季度'], y=selected_rows_t_4q['近四季平均淨利率%'], mode='lines', name='淨利率%', yaxis='y4', marker=dict(color='red')))

    fig3.update_layout(
        title=f'近四季平均財報三率、費用率，<br>近四季毛利率為{x1}%、費用率為{x2}%、營益率為{x3}%、淨利率為{x4}%',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='毛利率%、費用率%', range=y_range22),
        yaxis2=dict(title='', range=y_range22),
        yaxis3=dict(title='淨利率%、營益率%', overlaying='y', side='right', range=y_range11),
        yaxis4=dict(title='淨利率%、營益率%', overlaying='y', side='right', range=y_range11),
        legend=dict(
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'), 
        width = 900,
        height = 500
    )



    # fig3.show()

    return fig, fig2, fig3






#%%
# 004-2 包成def
# 經營安全邊際 (越高，抵抗景氣波動能力越大)
# 銀行業不看


def plotly_operating_margin_of_safety(dfs):
    
    data_omos = []

    for key, value in dfs.items():
        if key.endswith('_is'):
            row_data = {'年份-季度': key[5:10], 
                        '營業利益（損失）': 0,
                        '營業毛利（毛損）淨額': 0,
                    }           
            
            try:
                row_data['營業利益（損失）'] = value.loc['營業利益（損失）', value.columns[0]] 
                row_data['營業毛利（毛損）淨額'] = value.loc['營業毛利（毛損）淨額', value.columns[0]] 
                
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
            
            data_omos.append(row_data)
            
                
    result_df_omos = pd.DataFrame(data_omos)
 

    # 
    result_df_omos['年份'] = result_df_omos['年份-季度'].str[:3]
    result_df_omos['季度'] = result_df_omos['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_omos['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_omos[result_df_omos['年份'] == year]])
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_omos[(result_df_omos['年份'] == year) & (result_df_omos['季度'] == '1')].empty and
                result_df_omos[(result_df_omos['年份'] == year) & (result_df_omos['季度'] == '2')].empty and
                result_df_omos[(result_df_omos['年份'] == year) & (result_df_omos['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_omos[result_df_omos['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_omos[(result_df_omos['年份'] == year) & (result_df_omos['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_omos[(result_df_omos['年份'] == year) & (result_df_omos['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_omos[result_df_omos['年份'] == year]])

        elif count == 2:
            if (result_df_omos[(result_df_omos['年份'] == year) & (result_df_omos['季度'] == '3')].empty and
                result_df_omos[(result_df_omos['年份'] == year) & (result_df_omos['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_omos[result_df_omos['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_omos[(result_df_omos['年份'] == year) & (result_df_omos['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_omos[(result_df_omos['年份'] == year) & (result_df_omos['季度'] == '4')]])

        elif count == 1:
            if not result_df_omos[(result_df_omos['年份'] == year) & (result_df_omos['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_omos[result_df_omos['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)


    # 
    # 單季

    selected_rows['營業利益（損失）_調整'] = selected_rows['營業利益（損失）']
    selected_rows['營業毛利（毛損）淨額_調整'] = selected_rows['營業毛利（毛損）淨額']


    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '營業利益（損失）_調整'] -= selected_rows.loc[i-3:i-1, '營業利益（損失）'].sum()
            selected_rows.loc[i, '營業毛利（毛損）淨額_調整'] -= selected_rows.loc[i-3:i-1, '營業毛利（毛損）淨額'].sum()
            
            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '營業利益（損失）_調整']  = np.nan
            selected_rows.loc[i, '營業利益（損失）_調整']  = np.nan
            selected_rows.loc[i-1, '營業毛利（毛損）淨額_調整']  = np.nan
            selected_rows.loc[i, '營業毛利（毛損）淨額_調整']  = np.nan
            

    selected_rows['經營安全邊際%'] = round(selected_rows['營業利益（損失）_調整']/selected_rows['營業毛利（毛損）淨額_調整']*100,2)

    selected_rows['近四季平均經營安全邊際%'] = round(selected_rows['經營安全邊際%'].rolling(window=4).mean(),2)
    for i in range(1, len(selected_rows)):
            if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and 
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
                selected_rows.loc[i, '近四季平均經營安全邊際%'] = round(selected_rows.loc[i, '營業利益（損失）']/ selected_rows.loc[i, '營業毛利（毛損）淨額']*100 , 2)
                selected_rows.loc[i-1, '近四季平均經營安全邊際%'] = round(selected_rows.loc[i-1, '營業利益（損失）']/ selected_rows.loc[i-1, '營業毛利（毛損）淨額']*100 , 2)


    
    # 
    fig = go.Figure()

    selected_rows['is_below_50'] = selected_rows['經營安全邊際%'] < 50

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['經營安全邊際%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker_color=['red' if below_50 else 'mediumturquoise' for below_50 in selected_rows['is_below_50']],
        textposition='top center',
        text=selected_rows['經營安全邊際%'],
        name='經營安全邊際%'
    ))


    # 
    max1 = selected_rows['經營安全邊際%'].max()
    min1 = selected_rows['經營安全邊際%'].min()
    y_range = [min1-10,max1+10]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1

    fig.update_layout(
        title=f'前{year_difference}年各季度經營安全邊際',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='經營安全邊際%', range=y_range),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig.show()
    
    
    
    # 
    fig2 = go.Figure()

    selected_rows['is_below_50'] = selected_rows['近四季平均經營安全邊際%'] < 50

    fig2.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季平均經營安全邊際%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.5),
        marker_color=['red' if below_50 else 'mediumturquoise' for below_50 in selected_rows['is_below_50']],
        textposition='top center',
        text=selected_rows['近四季平均經營安全邊際%'],
        name='近四季平均經營安全邊際%'
    ))


    # 
    max1 = selected_rows['近四季平均經營安全邊際%'].max()
    min1 = selected_rows['近四季平均經營安全邊際%'].min()
    y_range = [min1-10,max1+10]


    fig2.update_layout(
        title=f'近四季平均經營安全邊際，>60%很不錯，越高，抵抗景氣波動能力越大',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='近四季平均經營安全邊際%', range=y_range),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400,
    )

    # fig2.show()


    average_operating_margin_of_safety = round(selected_rows['近四季平均經營安全邊際%'].iloc[-1], 2)

        
    return fig, fig2, average_operating_margin_of_safety





#%%
# 005包成def
# 營收、盈餘、營益率比較
# 銀行業ok、有些繼續營業單位稅前損益要改、淨收益要改


def plotly_year_revenue(dfs):

    data_year_revenue = []

    for key, value in dfs.items():
        if key.endswith('_is'):
            row_data = {'年份-季度': key[5:10], 
                            '營業收入合計': 0,
                            '本期淨利（淨損）': 0,
                            '營業利益（損失）': 0,
                        }
            
            try:
                #
                row_data['營業收入合計'] = value.at['營業收入合計', value.columns[0]] if '營業收入合計' in value.index else value.at['淨收益', value.columns[0]] if '淨收益' in value.index else value.at['收益合計', value.columns[0]]
                row_data['本期淨利（淨損）'] = value.at['本期淨利（淨損）', value.columns[0]] if '本期淨利（淨損）' in value.index else value.at['本期稅後淨利（淨損）', value.columns[0]]
                row_data['營業利益（損失）'] = (
                                                value.at['營業利益（損失）', value.columns[0]]
                                                if '營業利益（損失）' in value.index
                                                else (
                                                    value.at['繼續營業單位稅前損益', value.columns[0]]
                                                    if '繼續營業單位稅前損益' in value.index
                                                    else (
                                                        value.at['繼續營業單位稅前淨利（淨損）', value.columns[0]]
                                                        if '繼續營業單位稅前淨利（淨損）' in value.index
                                                        else value.at['營業利益', value.columns[0]]
                                                    )
                                                )
                                            )
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            data_year_revenue.append(row_data)
                
    result_df_year_revenue = pd.DataFrame(data_year_revenue)
    
    
    # 
    result_df_year_revenue['年份'] = result_df_year_revenue['年份-季度'].str[:3]
    result_df_year_revenue['季度'] = result_df_year_revenue['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_year_revenue['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_year_revenue[result_df_year_revenue['年份'] == year]])
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_year_revenue[(result_df_year_revenue['年份'] == year) & (result_df_year_revenue['季度'] == '1')].empty and
                result_df_year_revenue[(result_df_year_revenue['年份'] == year) & (result_df_year_revenue['季度'] == '2')].empty and
                result_df_year_revenue[(result_df_year_revenue['年份'] == year) & (result_df_year_revenue['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_year_revenue[result_df_year_revenue['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_year_revenue[(result_df_year_revenue['年份'] == year) & (result_df_year_revenue['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_year_revenue[(result_df_year_revenue['年份'] == year) & (result_df_year_revenue['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_year_revenue[result_df_year_revenue['年份'] == year]])

        elif count == 2:
            if (result_df_year_revenue[(result_df_year_revenue['年份'] == year) & (result_df_year_revenue['季度'] == '3')].empty and
                result_df_year_revenue[(result_df_year_revenue['年份'] == year) & (result_df_year_revenue['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_year_revenue[result_df_year_revenue['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_year_revenue[(result_df_year_revenue['年份'] == year) & (result_df_year_revenue['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_year_revenue[(result_df_year_revenue['年份'] == year) & (result_df_year_revenue['季度'] == '4')]])

        elif count == 1:
            if not result_df_year_revenue[(result_df_year_revenue['年份'] == year) & (result_df_year_revenue['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_year_revenue[result_df_year_revenue['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)


    #
    # 單季

    selected_rows['營業收入合計_調整'] = selected_rows['營業收入合計']
    selected_rows['本期淨利（淨損）_調整'] = selected_rows['本期淨利（淨損）']
    selected_rows['營業利益（損失）_調整'] = selected_rows['營業利益（損失）']

    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '營業收入合計_調整'] -= selected_rows.loc[i-3:i-1, '營業收入合計'].sum()
            selected_rows.loc[i, '本期淨利（淨損）_調整'] -= selected_rows.loc[i-3:i-1, '本期淨利（淨損）'].sum()
            selected_rows.loc[i, '營業利益（損失）_調整'] -= selected_rows.loc[i-3:i-1, '營業利益（損失）'].sum()
            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '營業收入合計_調整']  = np.nan
            selected_rows.loc[i, '營業收入合計_調整']  = np.nan
            selected_rows.loc[i-1, '本期淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i, '本期淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i-1, '營業利益（損失）_調整']  = np.nan
            selected_rows.loc[i, '營業利益（損失）_調整']  = np.nan
            
    selected_rows['營益率%_調整'] = round(selected_rows['營業利益（損失）_調整'] / selected_rows['營業收入合計_調整'] * 100, 2)
    

    # 
    # 四季

    selected_rows_t_4q = selected_rows

    selected_rows_t_4q['近四季累積營業收入合計_調整'] = round(selected_rows_t_4q['營業收入合計_調整'].rolling(window=4).sum(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累積營業收入合計_調整'] = round(selected_rows_t_4q.loc[i, '營業收入合計'], 2)
            selected_rows_t_4q.loc[i-1, '近四季累積營業收入合計_調整'] = round(selected_rows_t_4q.loc[i-1, '營業收入合計'], 2)
            
            
    selected_rows_t_4q['近四季累積本期淨利（淨損）_調整'] = round(selected_rows_t_4q['本期淨利（淨損）_調整'].rolling(window=4).sum(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累積本期淨利（淨損）_調整'] = round(selected_rows_t_4q.loc[i, '本期淨利（淨損）'], 2)
            selected_rows_t_4q.loc[i-1, '近四季累積本期淨利（淨損）_調整'] = round(selected_rows_t_4q.loc[i-1, '本期淨利（淨損）'], 2)


    selected_rows_t_4q['近四季累積營業利益（損失）_調整'] = round(selected_rows_t_4q['營業利益（損失）_調整'].rolling(window=4).sum(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季累積營業利益（損失）_調整'] = round(selected_rows_t_4q.loc[i, '營業利益（損失）'], 2)
            selected_rows_t_4q.loc[i-1, '近四季累積營業利益（損失）_調整'] = round(selected_rows_t_4q.loc[i-1, '營業利益（損失）'], 2)
            
    selected_rows_t_4q['近四季營益率%_調整'] = round(selected_rows_t_4q['近四季累積營業利益（損失）_調整'] / selected_rows_t_4q['近四季累積營業收入合計_調整']*100, 2)
            


    # 
    fig = go.Figure()

    fig.add_trace(go.Bar(x=selected_rows['年份-季度'], 
                        y=selected_rows['營業收入合計_調整'], 
                        name='營收', width=0.6, 
                        marker=dict(color='rgb(50, 225, 210)')))

    fig.add_trace(go.Bar(x=selected_rows['年份-季度'], 
                        y=selected_rows['本期淨利（淨損）_調整'], 
                        name='盈餘(稅後)', width=0.3, 
                        marker=dict(color='#e78ac3')))

    fig.add_trace(go.Scatter(x=selected_rows['年份-季度'], 
                            y=selected_rows['營益率%_調整'], 
                            mode='lines+markers+text', 
                            name='營益率%', 
                            yaxis='y3', marker=dict(color='blue'),
                            text=selected_rows['營益率%_調整'].astype(str) + '%',
                            textposition='top center'))

    # 
    max1 = selected_rows['營益率%_調整'].max()
    min1 = selected_rows['營益率%_調整'].min()
    y_range = [min1-5,max1+10]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1

    fig.update_layout(
        title=f'前{year_difference}年各季度季營收、盈餘、營益率比較<br>\
當營收成長時，盈餘、營益率同步成長，才是靠本業賺錢的公司，用"營益率%"觀察本業盈餘變化',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='營收'),
        yaxis2=dict(title='盈餘(稅後)'),
        yaxis3=dict(title='營益率%', overlaying='y', side='right', range=y_range),
        legend=dict(
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'),
        width=900,
        height=400,
    )


    # fig.show()
    
    
    # 
    fig2 = go.Figure()

    fig2.add_trace(go.Bar(x=selected_rows['年份-季度'], 
                        y=selected_rows['近四季累積營業收入合計_調整'], 
                        name='營收', width=0.6, 
                        marker=dict(color='rgb(50, 225, 210)')))

    fig2.add_trace(go.Bar(x=selected_rows['年份-季度'], 
                        y=selected_rows['近四季累積本期淨利（淨損）_調整'], 
                        name='盈餘(稅後)', width=0.3, 
                        marker=dict(color='#e78ac3')))

    fig2.add_trace(go.Scatter(x=selected_rows['年份-季度'], 
                            y=selected_rows['近四季營益率%_調整'], 
                            mode='lines+markers+text', name='營益率%', yaxis='y3', 
                            marker=dict(color='blue'),
                            text=selected_rows['近四季營益率%_調整'].astype(str) + '%',
                            textposition='top center'))

    max1 = selected_rows['近四季營益率%_調整'].max()
    min1 = selected_rows['近四季營益率%_調整'].min()
    y_range = [min1-5,max1+10]

    fig2.update_layout(
        title=f'近四季累積營收、盈餘、營益率比較',    
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='營收'),
        yaxis2=dict(title='盈餘(稅後)'),
        yaxis3=dict(title='營益率%', overlaying='y', side='right', range=y_range),
        legend=dict(
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'),
        width=900,
        height=400,
    )


    # fig2.show()
    
    return fig, fig2








#%%
# 005-2 包成def
# 營收成長率 Revenue Growth Rate
# 季
# ocf成長率>營收成長率、營益率成長率>營收成長率、稅後淨利成長率>營收成長率
# 存貨成長率<(營收成長率/2)
# bs -> cfs -> is
# 銀行業ok、有些繼續營業單位稅前損益要改、淨收益要改

def plotly_4q_revenue_growth_rate(dfs):
    # 穿插月報、與去年同月比較

    data_grp = []

    for key, value in dfs.items():
        row_data = {'年份-季度': key[5:10], 
                        '存貨': 0,
                        '營業活動之淨現金流入（流出）': 0,
                        '營業收入合計': 0,
                        '營業利益（損失）': 0,
                        '本期淨利（淨損）': 0,
                    }
        
        if key.endswith('_bs'):
            try:

                # 存貨
                row_data['存貨'] = value.at['存貨', value.columns[0]] if '存貨' in value.index else np.nan
                
                # ocf
                cfs_key = key.replace('_bs', '_cfs')
                if cfs_key in dfs:
                    row_data['營業活動之淨現金流入（流出）'] = dfs[cfs_key].loc['營業活動之淨現金流入（流出）', dfs[cfs_key].columns[0]]
                else:
                    raise ValueError(f'找不到對應的現金流量表 ({cfs_key}) 資料')
                
                # 
                is_key = key.replace('_bs', '_is')
                row_data['營業收入合計'] = dfs[is_key].loc['營業收入合計', dfs[is_key].columns[0]] \
                        if '營業收入合計' in dfs[is_key].index \
                        else dfs[is_key].loc['淨收益', dfs[is_key].columns[0]] \
                            if '淨收益' in dfs[is_key].index \
                            else dfs[is_key].loc['收益合計', dfs[is_key].columns[0]]

                row_data['營業利益（損失）'] = dfs[is_key].loc['營業利益（損失）', dfs[is_key].columns[0]] \
                                if '營業利益（損失）' in dfs[is_key].index \
                                else (dfs[is_key].loc['繼續營業單位稅前損益', dfs[is_key].columns[0]] 
                                    if '繼續營業單位稅前損益' in dfs[is_key].index 
                                    else dfs[is_key].loc['繼續營業單位稅前淨利（淨損）', dfs[is_key].columns[0]]
                                        if '繼續營業單位稅前淨利（淨損）' in dfs[is_key].index
                                        else dfs[is_key].loc['營業利益', dfs[is_key].columns[0]])


                row_data['本期淨利（淨損）'] = dfs[is_key].loc['本期淨利（淨損）', dfs[is_key].columns[0]] if '本期淨利（淨損）' in dfs[is_key].index else dfs[is_key].loc['本期稅後淨利（淨損）', dfs[is_key].columns[0]]
            
            
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
            
            data_grp.append(row_data)
                
    result_df_grp = pd.DataFrame(data_grp)


    # 
    result_df_grp['年份'] = result_df_grp['年份-季度'].str[:3]
    result_df_grp['季度'] = result_df_grp['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_grp['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_grp[result_df_grp['年份'] == year]])
                
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_grp[(result_df_grp['年份'] == year) & (result_df_grp['季度'] == '1')].empty and
                result_df_grp[(result_df_grp['年份'] == year) & (result_df_grp['季度'] == '2')].empty and
                result_df_grp[(result_df_grp['年份'] == year) & (result_df_grp['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_grp[result_df_grp['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_grp[(result_df_grp['年份'] == year) & (result_df_grp['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_grp[(result_df_grp['年份'] == year) & (result_df_grp['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_grp[result_df_grp['年份'] == year]])


        elif count == 2:
            if (result_df_grp[(result_df_grp['年份'] == year) & (result_df_grp['季度'] == '3')].empty and
                result_df_grp[(result_df_grp['年份'] == year) & (result_df_grp['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_grp[result_df_grp['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_grp[(result_df_grp['年份'] == year) & (result_df_grp['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_grp[(result_df_grp['年份'] == year) & (result_df_grp['季度'] == '4')]])

                
        elif count == 1:
            if not result_df_grp[(result_df_grp['年份'] == year) & (result_df_grp['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_grp[result_df_grp['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)


    # 
    selected_rows['營業收入合計_調整'] = selected_rows['營業收入合計']
    selected_rows['營業利益（損失）_調整'] = selected_rows['營業利益（損失）']
    selected_rows['本期淨利（淨損）_調整'] = selected_rows['本期淨利（淨損）']
    selected_rows['存貨_調整'] = selected_rows['存貨']
    selected_rows['營業活動之淨現金流入（流出）_調整'] = selected_rows['營業活動之淨現金流入（流出）']


    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '營業收入合計_調整'] -= selected_rows.loc[i-3:i-1, '營業收入合計'].sum()
            selected_rows.loc[i, '營業利益（損失）_調整'] -= selected_rows.loc[i-3:i-1, '營業利益（損失）'].sum()
            selected_rows.loc[i, '本期淨利（淨損）_調整'] -= selected_rows.loc[i-3:i-1, '本期淨利（淨損）'].sum()
            
            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '營業收入合計_調整']  = np.nan
            selected_rows.loc[i, '營業收入合計_調整']  = np.nan
            selected_rows.loc[i-1, '營業利益（損失）_調整']  = np.nan
            selected_rows.loc[i, '營業利益（損失）_調整']  = np.nan
            selected_rows.loc[i-1, '本期淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i, '本期淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i-1, '存貨_調整']  = np.nan
            selected_rows.loc[i, '存貨_調整']  = np.nan
            selected_rows.loc[i-1, '營業活動之淨現金流入（流出）_調整']  = np.nan
            selected_rows.loc[i, '營業活動之淨現金流入（流出）_調整']  = np.nan
        
   

    # 
    # 單季

    selected_rows['營業收入成長率%'] = round(selected_rows['營業收入合計_調整'].pct_change() * 100,2)
    selected_rows['營業利益成長率%'] = round(selected_rows['營業利益（損失）_調整'].pct_change() * 100,2)
    selected_rows['淨利成長率%'] = round(selected_rows['本期淨利（淨損）_調整'].pct_change() * 100,2)
    selected_rows['營業活動之淨現金流入（流出）成長率%'] = round(selected_rows['營業活動之淨現金流入（流出）_調整'].pct_change() * 100,2)
    selected_rows['存貨成長率%'] = round(selected_rows['存貨_調整'].pct_change() * 100,2)

        
    # 
    # 四季
    selected_rows_t_4q = selected_rows.copy()

    selected_rows_t_4q['近四季平均營業收入成長率%'] = round(selected_rows_t_4q['營業收入成長率%'].rolling(window=4).mean(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.at[i, '近四季平均營業收入成長率%'] = round((selected_rows_t_4q.at[i, '營業收入合計'] / selected_rows_t_4q.at[i-1, '營業收入合計'] - 1) * 100, 2)

    selected_rows_t_4q['近四季平均營業利益成長率%'] = round(selected_rows_t_4q['營業利益成長率%'].rolling(window=4).mean(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.at[i, '近四季平均營業利益成長率%'] = round((selected_rows_t_4q.at[i, '營業利益（損失）'] / selected_rows_t_4q.at[i-1, '營業利益（損失）'] - 1) * 100, 2)

    selected_rows_t_4q['近四季平均淨利成長率%'] = round(selected_rows['淨利成長率%'].rolling(window=4).mean(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.at[i, '近四季平均淨利成長率%'] = round((selected_rows_t_4q.at[i, '本期淨利（淨損）'] / selected_rows_t_4q.at[i-1, '本期淨利（淨損）'] - 1) * 100, 2)

    selected_rows_t_4q['近四季平均營業活動之淨現金流入（流出）成長率%'] = round(selected_rows_t_4q['營業活動之淨現金流入（流出）成長率%'].rolling(window=4).mean(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.at[i, '近四季平均營業活動之淨現金流入（流出）成長率%'] = round((selected_rows_t_4q.at[i, '營業活動之淨現金流入（流出）'] / selected_rows_t_4q.at[i-1, '營業活動之淨現金流入（流出）'] - 1) * 100, 2)

    selected_rows_t_4q['近四季平均存貨成長率%'] = round(selected_rows_t_4q['存貨成長率%'].rolling(window=4).mean(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.at[i, '近四季平均存貨成長率%'] = round((selected_rows_t_4q.at[i, '存貨'] / selected_rows_t_4q.at[i-1, '存貨'] - 1) * 100, 2)


    selected_rows_t_4q['近四季平均50%營業收入成長率%'] = round(selected_rows_t_4q['近四季平均營業收入成長率%']/2, 2)


    # 
    fig = go.Figure()



    fig.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均營業利益成長率%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.2),
        # text=result_df_grp['近四季平均營業利益成長率%'],
        textposition='top center',
        name='營業利益成長率%'
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均淨利成長率%'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y2',   
        # text=result_df_grp['近四季平均淨利成長率%'],
        textposition='top center',
        name='淨利成長率%'
    ))


    fig.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均營業收入成長率%'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y3', 
        # text=selected_rows['近四季平均營業收入成長率%'],
        textposition='top center',
        name='營業收入成長率%'
    ))

    # 
    max1= selected_rows_t_4q['近四季平均營業收入成長率%'].max()
    max2= selected_rows_t_4q['近四季平均營業利益成長率%'].max()
    max3= selected_rows_t_4q['近四季平均淨利成長率%'].max()
    min1= selected_rows_t_4q['近四季平均營業收入成長率%'].min()
    min2= selected_rows_t_4q['近四季平均營業利益成長率%'].min()
    min3= selected_rows_t_4q['近四季平均淨利成長率%'].min()

    y_range = [min(min1,min2,min3)-5, max(max1,max2,max3)+5]

    # 更新佈局設置
    fig.update_layout(
        title=f'近四季平均營業利益、淨利、營業收入成長率<br>\
營業利益、淨利成長率是否 > 營業收入成長率',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='', range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        yaxis3=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(title='成長率%',
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'), 
        width = 900,
        height = 400
    )


    # fig.show()
    
    
    # 
    fig2 = go.Figure()


    fig2.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均營業活動之淨現金流入（流出）成長率%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.2),  
        # text=result_df_grp['近四季營業活動之淨現金流入（流出）成長率%'],
        textposition='top center',
        name='ocf成長率%'
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均營業收入成長率%'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y2', 
        # text=result_df_grp['近四季營業收入成長率%'],
        textposition='top center',
        name='營業收入成長率%'
    ))



    # 
    max1= selected_rows_t_4q['近四季平均營業收入成長率%'].max()
    max2= selected_rows_t_4q['近四季平均營業活動之淨現金流入（流出）成長率%'].max()
    min1= selected_rows_t_4q['近四季平均營業收入成長率%'].min()
    min2= selected_rows_t_4q['近四季平均營業活動之淨現金流入（流出）成長率%'].min()

    y_range = [min(min1,min2)-5, max(max1,max2)+5]

    # 更新佈局設置
    fig2.update_layout(
        title=f'近四季平均ocf成長率是否 > 營收成長率',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='', range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(title='成長率%',
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'), 
        width = 900,
        height = 400
    )

    # fig2.show()
    
    
    # 
    fig33 = go.Figure()

    fig33.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均存貨成長率%'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2.2),   
        # text=result_df_grp['近四季平均營業利益成長率%'],
        textposition='top center',
        name='存貨成長率%'
    ))

    fig33.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均50%營業收入成長率%'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        yaxis='y2',
        # text=result_df_grp['近四季平均50%營業收入成長率%'],
        textposition='top center',
        name='50%營業收入成長率%'
    ))


    # 
    max1= selected_rows_t_4q['近四季平均50%營業收入成長率%'].max()
    max2= selected_rows_t_4q['近四季平均存貨成長率%'].max()
    min1= selected_rows_t_4q['近四季平均50%營業收入成長率%'].min()
    min2= selected_rows_t_4q['近四季平均存貨成長率%'].min()

    y_range = [min(min1,min2)-5, max(max1,max2)+5]

    # 更新佈局設置
    fig33.update_layout(
        title=f'近四季平均存貨成長率是否 < 50% 營收成長率',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='', range=y_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y_range),
        legend=dict(title='成長率%',
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'), 
        width = 900,
        height = 400
    )


    # fig3.show()`
    
    if selected_rows_t_4q['近四季平均存貨成長率%'].isnull().all():
        return fig, fig2
    else:
        return fig, fig2, fig33

    

    



    
#%%
# 006 包成def
# 業內、業外
# 銀行業不看

def plotly_non_operating_earnings(dfs):

    data_oi_p = []

    for key, value in dfs.items():
        if key.endswith('_is'):
            
            row_data = {'年份-季度': key[5:10], 
                        '營業利益（損失）': 0,
                        '營業外收入及支出合計': 0,
                        '稅前淨利（淨損）': 0,
                    }
            
            try:
                # 營業利益（損失） = 收入-成本-營業費用
                row_data['營業利益（損失）'] = value.loc['營業利益（損失）', value.columns[0]]
                row_data['營業外收入及支出合計'] = value.loc['營業外收入及支出合計', value.columns[0]]
                row_data['稅前淨利（淨損）'] = value.loc['稅前淨利（淨損）', value.columns[0]]
                
                
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            data_oi_p.append(row_data)
                
    result_df_oi_p = pd.DataFrame(data_oi_p)
    
    
    
    # 
    result_df_oi_p['年份'] = result_df_oi_p['年份-季度'].str[:3]
    result_df_oi_p['季度'] = result_df_oi_p['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_oi_p['年份'].value_counts()
    year_counts 

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_oi_p[result_df_oi_p['年份'] == year]])
                
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_oi_p[(result_df_oi_p['年份'] == year) & (result_df_oi_p['季度'] == '1')].empty and
                result_df_oi_p[(result_df_oi_p['年份'] == year) & (result_df_oi_p['季度'] == '2')].empty and
                result_df_oi_p[(result_df_oi_p['年份'] == year) & (result_df_oi_p['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_oi_p[result_df_oi_p['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_oi_p[(result_df_oi_p['年份'] == year) & (result_df_oi_p['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_oi_p[(result_df_oi_p['年份'] == year) & (result_df_oi_p['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_oi_p[result_df_oi_p['年份'] == year]])

        elif count == 2:
            if (result_df_oi_p[(result_df_oi_p['年份'] == year) & (result_df_oi_p['季度'] == '3')].empty and
                result_df_oi_p[(result_df_oi_p['年份'] == year) & (result_df_oi_p['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_oi_p[result_df_oi_p['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_oi_p[(result_df_oi_p['年份'] == year) & (result_df_oi_p['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_oi_p[(result_df_oi_p['年份'] == year) & (result_df_oi_p['季度'] == '4')]])

        elif count == 1:
            if not result_df_oi_p[(result_df_oi_p['年份'] == year) & (result_df_oi_p['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_oi_p[result_df_oi_p['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)
    

    # 
    selected_rows['營業利益（損失）_調整'] = selected_rows['營業利益（損失）']
    selected_rows['營業外收入及支出合計_調整'] = selected_rows['營業外收入及支出合計']
    selected_rows['稅前淨利（淨損）_調整'] = selected_rows['稅前淨利（淨損）']

    # 計算每個Q4的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            selected_rows.loc[i, '營業利益（損失）_調整'] -= selected_rows.loc[i-3:i-1, '營業利益（損失）'].sum()
            selected_rows.loc[i, '營業外收入及支出合計_調整'] -= selected_rows.loc[i-3:i-1, '營業外收入及支出合計'].sum()
            selected_rows.loc[i, '稅前淨利（淨損）_調整'] -= selected_rows.loc[i-3:i-1, '稅前淨利（淨損）'].sum()
            
        elif (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i, '營業利益（損失）_調整'] = np.nan
            selected_rows.loc[i-1, '營業利益（損失）_調整'] = np.nan
            selected_rows.loc[i, '營業外收入及支出合計_調整'] = np.nan
            selected_rows.loc[i-1, '營業外收入及支出合計_調整'] = np.nan
            selected_rows.loc[i, '稅前淨利（淨損）_調整'] = np.nan
            selected_rows.loc[i-1, '稅前淨利（淨損）_調整'] = np.nan
        
    selected_rows['本業比率%'] = round(selected_rows['營業利益（損失）_調整'] / (selected_rows['營業利益（損失）_調整'] + selected_rows['營業外收入及支出合計_調整'])*100,2)
    selected_rows['業外比率%'] = round(selected_rows['營業外收入及支出合計_調整'] / (selected_rows['營業利益（損失）_調整'] + selected_rows['營業外收入及支出合計_調整'])*100,2)
    selected_rows['業外貢獻比'] = round(selected_rows['稅前淨利（淨損）_調整'] / selected_rows['營業利益（損失）_調整'],2)


    # 
    # 四季
    selected_rows_t_4q = selected_rows.copy()

    selected_rows_t_4q['近四季平均本業比率%'] = round(selected_rows_t_4q['本業比率%'].rolling(window=4).mean(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季平均本業比率%'] = round(selected_rows_t_4q.loc[i, '營業利益（損失）'] / ( selected_rows_t_4q.loc[i, '營業利益（損失）']+ selected_rows_t_4q.loc[i, '營業外收入及支出合計']) * 100, 2)


    selected_rows_t_4q['近四季平均業外比率%'] = round(selected_rows_t_4q['業外比率%'].rolling(window=4).mean(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季平均業外比率%'] = round(selected_rows_t_4q.loc[i, '營業外收入及支出合計'] / ( selected_rows_t_4q.loc[i, '營業利益（損失）']+ selected_rows_t_4q.loc[i, '營業外收入及支出合計']) * 100, 2)


    selected_rows_t_4q['近四季平均業外貢獻比'] = round(selected_rows_t_4q['業外貢獻比'].rolling(window=4).mean(), 2)
    for i in range(1, len(selected_rows_t_4q)):
        if (selected_rows_t_4q.loc[i, '年份-季度'].endswith('Q4') and 
        selected_rows_t_4q.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows_t_4q.loc[i, '近四季平均業外貢獻比'] = round(selected_rows_t_4q.loc[i, '稅前淨利（淨損）'] / selected_rows_t_4q.loc[i, '營業利益（損失）'], 2)



    # 
    fig = go.Figure()


    fig.add_trace(go.Bar(
        x=selected_rows['年份-季度'],
        y=selected_rows['本業比率%'],
        text=selected_rows['本業比率%'].astype(str),   
        name='本業比率%',
        width=0.6,
        marker=dict(color='rgb(50, 225, 210)')
    ))

    fig.add_trace(go.Bar(
        x=selected_rows['年份-季度'],
        y=selected_rows['業外比率%'],
        text=selected_rows['業外比率%'].astype(str), 
        name='業外比率%',
        yaxis='y2',
        width=0.6,
        marker=dict(color='#e78ac3')
    ))

    fig.add_trace(go.Scatter(
        x=selected_rows['年份-季度'],
        y=selected_rows['業外貢獻比'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        yaxis='y3',
        textposition='top center',
        name='業外貢獻比'
    ))


    y_range = [selected_rows['業外貢獻比'].min()-2, selected_rows['業外貢獻比'].max()+2]

    min1 = selected_rows['本業比率%'].min()
    min2 = selected_rows['業外比率%'].min()

    max1 = selected_rows['本業比率%'].max()
    max2 = selected_rows['業外比率%'].max()

    y2_range = [min(min1,min2)-10, max(max1,max2)+10]

    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1

    fig.update_layout(
        title=f'前{year_difference}年各季度營業利益(本業)、業外稅前佔比',    
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='本業、業外比率%', range=y2_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y2_range, showticklabels=False ),
        yaxis3=dict(title='業外貢獻比', overlaying='y', side='right', range=y_range),
        legend=dict(
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'),
        width= 900,
        height= 400,
    )


    # fig.show()



    # 
    fig2 = go.Figure()


    fig2.add_trace(go.Bar(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均本業比率%'],
        text=selected_rows_t_4q['近四季平均本業比率%'].astype(str),   
        name='本業比率%',
        width=0.6,
        marker=dict(color='rgb(50, 225, 210)')
    ))

    fig2.add_trace(go.Bar(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均業外比率%'],
        text=selected_rows_t_4q['近四季平均業外比率%'].astype(str), 
        name='業外比率%',
        yaxis='y2',
        width=0.6,
        marker=dict(color='#e78ac3')
    ))

    fig2.add_trace(go.Scatter(
        x=selected_rows_t_4q['年份-季度'],
        y=selected_rows_t_4q['近四季平均業外貢獻比'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2.5),
        yaxis='y3',
        textposition='top center',
        name='業外貢獻比'
    ))


    y_range = [selected_rows_t_4q['近四季平均業外貢獻比'].min()-2, selected_rows_t_4q['近四季平均業外貢獻比'].max()+2]


    min1 = selected_rows_t_4q['近四季平均本業比率%'].min()
    min2 = selected_rows_t_4q['近四季平均業外比率%'].min()

    max1 = selected_rows_t_4q['近四季平均本業比率%'].max()
    max2 = selected_rows_t_4q['近四季平均業外比率%'].max()

    y2_range = [min(min1,min2)-10, max(max1,max2)+10]



    fig2.update_layout(
        title=f'近四季平均營業利益(本業)、業外稅前佔比',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='本業、業外比率%', range=y2_range),
        yaxis2=dict(title='', overlaying='y', side='right', range=y2_range, showticklabels=False ),
        yaxis3=dict(title='業外貢獻比', overlaying='y', side='right', range=y_range),
        legend=dict(
                x=1.0,
                y=1.4,
                traceorder='normal',
                orientation='v'),
        width= 900,
        height= 400,
    )


    # fig2.show()
    
    return fig, fig2





#%%
# eps 包成def
# 007: EPS Earning Per Share 每股盈餘
# 每股盈餘EPS = (本期稅後淨利 – 特別股股利) ÷ 加權平均流通在外的普通股股數
# 每股盈餘EPS = 稅後淨利/在外流通股數

def plotly_eps(dfs):
    
    data_eps = []
    for key, value in dfs.items():
        if key.endswith('_is'):
            row_data = {'年份-季度': key[5:10], 
                            '基本每股盈餘': 0,
                            '本期淨利（淨損）': 0,
                        }
            try:
                #
                row_data['本期淨利（淨損）'] = value.at['本期淨利（淨損）', value.columns[0]] if '本期淨利（淨損）' in value.index else value.at['本期稅後淨利（淨損）', value.columns[0]]
                row_data['基本每股盈餘'] = value.loc['基本每股盈餘', value.columns[0]].iloc[-1]
                
                
                
            
            except Exception as e:
                print(f'計算 {key} 發生錯誤: {str(e)}')
                
            data_eps.append(row_data)

    result_df_eps = pd.DataFrame(data_eps)
    
    
    
    
    # 
    result_df_eps['年份'] = result_df_eps['年份-季度'].str[:3]
    result_df_eps['季度'] = result_df_eps['年份-季度'].str[-1:]

    # 計算每個年份出現的次數
    year_counts = result_df_eps['年份'].value_counts()

    selected_rows = pd.DataFrame()

    for year, count in year_counts.items():
        if count == 4:
            selected_rows = pd.concat([selected_rows, result_df_eps[result_df_eps['年份'] == year]])
            
        elif count == 3:
            # 如果1、2、3 三個都是空的，就提取
            if (result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '1')].empty and
                result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '2')].empty and
                result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_eps[result_df_eps['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '4')]])

            # 否則全部提取
            else:
                selected_rows = pd.concat([selected_rows, result_df_eps[result_df_eps['年份'] == year]])

        elif count == 2:
            if (result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '3')].empty and
                result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '4')].empty ):
                selected_rows = pd.concat([selected_rows, result_df_eps[result_df_eps['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '4')]])

        elif count == 1:
            if not result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_eps[result_df_eps['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)



    #

    selected_rows['基本每股盈餘_調整'] = selected_rows['基本每股盈餘']

    # 計算每個季度的調整值
    total_rows = len(selected_rows)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 3 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q3') and
            i >= 2 and
            selected_rows.loc[i-2, '年份-季度'].endswith('Q2') and
            i >= 1 and
            selected_rows.loc[i-3, '年份-季度'].endswith('Q1')):
            
            selected_rows.loc[i, '基本每股盈餘_調整'] = round(selected_rows.loc[i, '基本每股盈餘'] - selected_rows.loc[i-3:i-1, '基本每股盈餘'].sum(),2)

    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '基本每股盈餘_調整']  = np.nan
            selected_rows.loc[i, '基本每股盈餘_調整']  = np.nan

    selected_rows['去年同期基本每股盈餘_調整'] = round(selected_rows['基本每股盈餘_調整'].shift(4), 2)
    selected_rows['近四季累積基本每股盈餘_調整'] = round(selected_rows['基本每股盈餘_調整'].rolling(window=4).sum(), 2)
    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
                    i >= 1 and
                    selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
                    selected_rows.loc[i-1, '近四季累積基本每股盈餘_調整']  = selected_rows.loc[i-1, '基本每股盈餘'] 
                    selected_rows.loc[i, '近四季累積基本每股盈餘_調整']  = selected_rows.loc[i, '基本每股盈餘'] 
        

    # 
    # 單季table
    import plotly.figure_factory as ff

    selected_rows_t = selected_rows.transpose()

    # 
    selected_columns = ['年份-季度', '基本每股盈餘_調整']
    selected_rows_t = selected_rows_t[selected_rows_t.index.isin(selected_columns)]
    selected_rows_t.columns = selected_rows_t.iloc[0]

  
    
    # 
    import plotly.figure_factory as ff

    # 提取 
    table_data = selected_rows_t.loc[['基本每股盈餘_調整'], :]
    table_data = table_data.fillna('NaN')


    try:
        table_data = table_data.iloc[:,-8:]
    except:
        pass

    # 創建表格
    fig = ff.create_table(table_data, height_constant=30)

    # 
    fig.update_layout(
        title='每股盈餘EPS',
        width=900,
        height=200,
    )

    # fig.show()
    
    

    
    # 
    fig2 = go.Figure()

    #  
    fig2.add_trace(go.Bar(
        x=selected_rows['年份-季度'],
        y=selected_rows['基本每股盈餘_調整'],
        text=selected_rows['基本每股盈餘_調整'],  
        marker=dict(color='mediumturquoise'),  
        name='每股盈餘', 
        width=0.41, 
    ))

    # 
    fig2.add_trace(go.Bar(
        x=selected_rows['年份-季度'],
        y=selected_rows['去年同期基本每股盈餘_調整'],
        text=selected_rows['去年同期基本每股盈餘_調整'],  
        marker=dict(color='pink'),  
        name='去年同期每股盈餘', 
        width=0.41, 
    ))


    #
    last_year = int(selected_rows['年份-季度'].iloc[-1][:3])
    first_year = int(selected_rows['年份-季度'].iloc[0][:3])
    year_difference = last_year - first_year + 1
    


    y_range = [selected_rows['基本每股盈餘_調整'].min()-0.3, selected_rows['基本每股盈餘_調整'].max()+0.3]


    fig2.update_layout(
        title=f'前{year_difference}年各季度、去年同期每股盈餘',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='每股盈餘', range=y_range), 
        yaxis2=dict(title='去年同期成長率%',overlaying='y', side='right',range=y_range), 
        legend=dict(
            x=1,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=900,
        height=400
    )

    # fig2.show()
    
    
    
    # 
    fig3 = go.Figure()

    #  
    fig3.add_trace(go.Bar(
        x=selected_rows['年份-季度'],
        y=selected_rows['近四季累積基本每股盈餘_調整'],
        text=selected_rows['近四季累積基本每股盈餘_調整'],  
        marker=dict(color='mediumturquoise'),  
        name='每股盈餘', 
        width=0.5, 
    ))


    # 更新佈局設置
    y_range = [selected_rows['近四季累積基本每股盈餘_調整'].min()-0.1, selected_rows['近四季累積基本每股盈餘_調整'].max()+0.1]

        
    fig3.update_layout(
        title=f'近四季累積基本每股盈餘_調整',
        xaxis=dict(title='年份-季度'),
        yaxis=dict(title='每股盈餘', range=y_range), 
        legend=dict(
            x=1,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=800,
        height=400
    )

    # fig3.show()
    
    
    return fig, fig2, fig3

    
        
    
    
    
#%%
# 007-2 包成de
# 月報看每月營收


def download_and_save_monthly_report_db():
    # 下載數據庫文件
    url = 'https://github.com/06Cata/tw_financial_reports3/raw/main/monthly_report.db'
    response = requests.get(url)

    # 將數據保存到臨時文件中
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(response.content)
    temp_file_path = temp_file.name
    
    return temp_file_path




#%%

def read__monthly_report_from_sqlite(stock_code):

    db_file_path = download_and_save_monthly_report_db()

    # 
    conn = sqlite3.connect(db_file_path)
    table_name = 'monthly_report_2018'
    # query = f"SELECT DISTINCT * FROM {table_name} WHERE 公司代號='{stock_code}' GROUP BY 年份, CAST(月份 AS INTEGER)"
    query = f"SELECT DISTINCT * FROM {table_name} WHERE 公司代號='{stock_code}'"
    df_monthly = pd.read_sql_query(query, conn)
    
    # 添加年月列和成長率列
    df_monthly['年月'] = df_monthly['年份'] + '-' + df_monthly['月份']
    # df_monthly['成長率%'] = round((df_monthly['當月營收'] - df_monthly['去年當月營收']) / df_monthly['去年當月營收'] *100, 2)

    # 
    conn.close()
    
    
    # 
    fig = go.Figure()

    fig.add_trace(go.Bar(x=df_monthly['年月'], 
                        y=df_monthly['當月營收'], 
                        name='當月營收', width=0.41, 
                        marker=dict(color='blue')))

    fig.add_trace(go.Bar(x=df_monthly['年月'], 
                        y=df_monthly['去年當月營收'], 
                        name='去年當月營收', width=0.41, 
                        marker=dict(color='mediumturquoise')))

    fig.add_trace(go.Scatter(
                    x=df_monthly['年月'],
                    y=df_monthly['去年同月 增減(%)'],
                    mode='lines+markers+text',
                    line=dict(color='red', width=1.8),
                    textposition='top center',
                    name='去年同月 增減(%)',
                    yaxis='y3'   
                ))


    # 
    y_range = [df_monthly['當月營收'].min()-50000, df_monthly['當月營收'].max()+50000]
    y_range2 = [df_monthly['去年同月 增減(%)'].min()-10, df_monthly['去年同月 增減(%)'].max()+10]


    last_3_rows = df_monthly['去年同月 增減(%)'].tail(3)
    negative_count = last_3_rows[last_3_rows < 0].count()


    fig.update_layout(
        title=f'當月營收、去年同月營收，近三季有{negative_count}季同月增減(%)是負的',
        xaxis=dict(title='年月'),
        yaxis=dict(title='當月營收', range=y_range),
        yaxis2=dict(title='去年當月營收', range=y_range),  
        yaxis3=dict(title='去年同月 增減(%)', overlaying='y', side='right', range=y_range2),
        legend=dict(title='',
                    x=1.0,
                    y=1.4,
                    traceorder='normal',
                    orientation='v'), 
        width=1000,
        height=400
    )

    # fig.show()
    
    return fig