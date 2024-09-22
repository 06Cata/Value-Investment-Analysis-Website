#%%
# 基本面_價值分析
#%%
import datetime 
import requests
import pandas as pd
import tempfile
import sqlite3
import os



#%%
# daily_pe_pb + daily_pe_pb_otc

def download_and_save_pe_pb_db(stock_size):
    # 下載數據庫文件
    if stock_size == '上市':
        url = 'https://github.com/06Cata/tw_financial_reports3/raw/main/daily_pe_pb.db'
        
    elif stock_size == '上櫃':
        url = 'https://github.com/06Cata/tw_financial_reports3/raw/main/daily_pe_pb_otc.db'
        
    response = requests.get(url)

    # 將數據保存到臨時文件中
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(response.content)
    temp_file_path = temp_file.name
    
    return temp_file_path


def read_pe_pb_from_sqlite(stock_code, stock_size):
    db_path = download_and_save_pe_pb_db(stock_size)
    conn = sqlite3.connect(db_path)
    table_name = 'daily_pe_pb_2019' if stock_size == '上市' else 'daily_pe_pb_otc_2019'

    query = f"SELECT DISTINCT * FROM {table_name} WHERE 證券代號='{stock_code}' ORDER BY 年, 月, 日"
    df_pe_pb = pd.read_sql_query(query, conn)
    df_pe_pb.drop(columns=['年', '月', '日','年份'], inplace=True)
    conn.close()
    
    return df_pe_pb


#%%
# daily_price + daily_price_otc

def download_daily_price_db_for_pe_pb(stock_size):
    
    if stock_size == '上市':
        url = 'https://github.com/06Cata/tw_financial_reports3/raw/main/daily_price.db'
    elif stock_size == '上櫃':
        url = 'https://github.com/06Cata/tw_financial_reports3/raw/main/daily_price_otc.db'
    
    response = requests.get(url)
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(response.content)
    temp_file_path = temp_file.name
    temp_file.close()
    return temp_file_path


def read_daily_price_from_sqlite_for_pe_pb(stock_code, stock_size):
    db_path = download_daily_price_db_for_pe_pb(stock_size)
    conn = sqlite3.connect(db_path)
    table_name = 'daily_price_2019' if stock_size == '上市' else 'daily_price_otc_2019'

    query = f"SELECT * FROM {table_name} WHERE 證券代號='{stock_code}' ORDER BY 日期 ASC"
    daily_df = pd.read_sql_query(query, conn)
    conn.close()
    os.remove(db_path)
    daily_df.drop_duplicates(subset=['證券代號', '日期'], keep='first', inplace=True)
    
    return daily_df



#%%
# merge '殖利率(%)
# merge_daily_pe_pb 

def merge_daily_pe_pb(stock_size, daily_df, df_pe_pb):
#+
    import pandas as pd

    daily_df['日期'] = pd.to_datetime(daily_df['日期'], format='%Y%m%d')
    df_pe_pb['日期'] = pd.to_datetime(df_pe_pb['日期'], format='%Y%m%d')
    df_pe_pb['股價淨值比'] = pd.to_numeric(df_pe_pb['股價淨值比'], errors='coerce')

    df_pe_pb.rename(columns={'股價淨值比': '股價淨值比'}, inplace=True)

    if stock_size == '上市':
        merged_df = pd.merge(daily_df, df_pe_pb[['日期','股價淨值比','殖利率(%)']], on='日期', how='left')
    if stock_size == '上櫃':
        merged_df = pd.merge(daily_df, df_pe_pb[['日期','股價淨值比','殖利率(%)','本益比']], on='日期', how='left')

    merged_df.rename(columns={'殖利率(%)': '殖利率%'}, inplace=True)

    # 刪除第一行中有 NaN 值的行，直到第一行沒有 NaN#-
    # Remove rows with NaN values until the first row without NaN values#+
    while merged_df.iloc[0].isnull().any():
        merged_df = merged_df.drop(merged_df.index[0], inplace=True)
    # 將 NaN 值填充為前一個有效值#-
    # Fill NaN values with the previous valid value#+
    # merged_df.fillna(method='ffill', inplace=True)
    merged_df = merged_df.ffill()
    
    
    merged_df['年'] = merged_df['日期'].dt.year 
    merged_df['年份'] = merged_df['年'] -1911
    merged_df['月'] = merged_df['日期'].dt.month
    merged_df['日'] = merged_df['日期'].dt.day

    def get_quarter(month):
        if month in [1, 2, 3]:
            return 1
        elif month in [4, 5, 6]:
            return 2
        elif month in [7, 8, 9]:
            return 3
        else:
            return 4

    merged_df['季度'] = merged_df['日期'].dt.month.apply(get_quarter)

    merged_df['年份-季度'] = merged_df['年份'].astype(str)  + 'Q' + merged_df['季度'].astype(str) 

    merged_df.drop(columns=['年', '月', '日','年份','季度'], inplace=True)
    
    merged_df['本益比'] = pd.to_numeric(merged_df['本益比'], errors='coerce')
    # 填充 NaN 值（例如使用前向填充）
    merged_df = merged_df.ffill()
    
    return merged_df




#%%
# 要代入的eps

def daily_eps(dfs):
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
            if (result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '1')].empty and
                result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '2')].empty and
                result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '3')].empty):
                selected_rows = pd.concat([selected_rows, result_df_eps[result_df_eps['年份'] == year]])
                
            # 4 不是空的，就提取
            elif not (result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '4')].empty):
                selected_rows = pd.concat([selected_rows, result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '4')]])

        elif count == 1:
            if not result_df_eps[(result_df_eps['年份'] == year) & (result_df_eps['季度'] == '1')].empty:
                selected_rows = pd.concat([selected_rows, result_df_eps[result_df_eps['年份'] == year]])

    selected_rows.sort_values(['年份', '季度'], inplace=True)
    selected_rows.reset_index(drop=True, inplace=True)

    import math
    import numpy as np

    selected_rows['基本每股盈餘_調整'] = selected_rows['基本每股盈餘']
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
            
            selected_rows.loc[i, '基本每股盈餘_調整'] = round(selected_rows.loc[i, '基本每股盈餘'] - selected_rows.loc[i-3:i-1, '基本每股盈餘'].sum(),2)
            selected_rows.loc[i, '本期淨利（淨損）_調整'] -= selected_rows.loc[i-3:i-1, '本期淨利（淨損）'].sum()
            
    for i in range(total_rows):
        if (selected_rows.loc[i, '年份-季度'].endswith('Q4') and
            i >= 1 and
            selected_rows.loc[i-1, '年份-季度'].endswith('Q4')):
            selected_rows.loc[i-1, '基本每股盈餘_調整']  = np.nan
            selected_rows.loc[i, '基本每股盈餘_調整']  = np.nan
            selected_rows.loc[i, '本期淨利（淨損）_調整']  = np.nan
            selected_rows.loc[i-1, '本期淨利（淨損）_調整']  = np.nan


    selected_rows['去年同期基本每股盈餘_調整'] = round(selected_rows['基本每股盈餘_調整'].shift(4), 2)
    selected_rows['近四季累積基本每股盈餘_調整'] = round(selected_rows['基本每股盈餘_調整'].rolling(window=4).sum(), 2)
    selected_rows['近四季累積本期淨利（淨損）_調整'] = round(selected_rows['本期淨利（淨損）_調整'].rolling(window=4).sum(), 2)

    merge_eps_df = selected_rows

    return merge_eps_df



#%%
# merge eps
# merge_daily_pe_pb_eps

def merge_daily_pe_pb_eps(merged_df, merge_eps_df):
    merged_df_2 = pd.merge(merged_df, merge_eps_df[['年份-季度', '近四季累積本期淨利（淨損）_調整','近四季累積基本每股盈餘_調整']], on='年份-季度', how='left')

    # merged_df_2['近四季累積本期淨利（淨損）_調整'].fillna(method='ffill', inplace=True)
    # merged_df_2['近四季累積基本每股盈餘_調整'].fillna(method='ffill', inplace=True)
    merged_df_2['近四季累積本期淨利（淨損）_調整'] = merged_df_2['近四季累積本期淨利（淨損）_調整'].ffill() 
    merged_df_2['近四季累積基本每股盈餘_調整'] = merged_df_2['近四季累積基本每股盈餘_調整'].ffill()


    # 
    merged_df_2['兩年前日期'] = merged_df_2['日期'] - pd.DateOffset(years=2)
    
    
    #
    import numpy as np
    merged_df_2['日期'] = pd.to_datetime(merged_df_2['日期'])

    def calculate_cheap_pe(row):
        two_years_ago_date = row['兩年前日期']
        current_date = row['日期']
        if pd.isnull(two_years_ago_date) or pd.isnull(current_date):
            return pd.NA
        
        selected_data = merged_df_2[(merged_df_2['日期'] >= two_years_ago_date) & (merged_df_2['日期'] < current_date)]
        if selected_data.empty:
            return pd.NA
        
        cheap_pe = round(selected_data['本益比'].min(), 2)
        return cheap_pe


    def calculate_low_pe(row):
        two_years_ago_date = row['兩年前日期']
        current_date = row['日期']
        if pd.isnull(two_years_ago_date) or pd.isnull(current_date):
            return pd.NA
        
        selected_data = merged_df_2[(merged_df_2['日期'] >= two_years_ago_date) & (merged_df_2['日期'] < current_date)]
        if selected_data.empty:
            return pd.NA
        
        try:
            low_pe = round((selected_data['本益比'].min()+selected_data['本益比'].median())/2,2)
        except:
            low_pe = pd.NA
        return low_pe


    def calculate_reasonable_pe(row):
        two_years_ago_date = row['兩年前日期']
        current_date = row['日期']
        if pd.isnull(two_years_ago_date) or pd.isnull(current_date):
            return pd.NA
        
        selected_data = merged_df_2[(merged_df_2['日期'] >= two_years_ago_date) & (merged_df_2['日期'] < current_date)]
        if selected_data.empty:
            return pd.NA
        try:
            resonable_pe = round(selected_data['本益比'].median(),2)
        except:
            resonable_pe = pd.NA
        return resonable_pe

    def calculate_high_pe(row):
        two_years_ago_date = row['兩年前日期']
        current_date = row['日期']
        if pd.isnull(two_years_ago_date) or pd.isnull(current_date):
            return pd.NA
        
        selected_data = merged_df_2[(merged_df_2['日期'] >= two_years_ago_date) & (merged_df_2['日期'] < current_date)]
        if selected_data.empty:
            return pd.NA
        try:
            high_pe = round((selected_data['本益比'].max()+selected_data['本益比'].median())/2,2)
        except:
            high_pe = pd.NA
        return high_pe

    def calculate_expensive_pe(row):
        two_years_ago_date = row['兩年前日期']
        current_date = row['日期']
        if pd.isnull(two_years_ago_date) or pd.isnull(current_date):
            return pd.NA
        
        selected_data = merged_df_2[(merged_df_2['日期'] >= two_years_ago_date) & (merged_df_2['日期'] < current_date)]
        if selected_data.empty:
            return pd.NA
        try:
            expensive_pe = round(selected_data['本益比'].max(),2)
        except:
            expensive_pe = pd.NA
        return expensive_pe


    # def  estimated_growth_rate(row):
    #     two_years_ago_date = row['兩年前日期']
    #     current_date = row['日期']
    #     if pd.isnull(two_years_ago_date) or pd.isnull(current_date):
    #         return pd.NA
        
    #     selected_data = merged_df_2[(merged_df_2['日期'] >= two_years_ago_date) & (merged_df_2['日期'] < current_date)]
    #     if selected_data.empty:
    #         return pd.NA
        
        
    #     first_valid_index = selected_data['近四季累積本期淨利（淨損）_調整'].first_valid_index()   
    #     if first_valid_index is None:
    #         return pd.NA
        
    #     past = selected_data['近四季累積本期淨利（淨損）_調整'].loc[first_valid_index] 
        
    #     return past



    merged_df_2['cheap_pe'] = merged_df_2.apply(calculate_cheap_pe, axis=1)
    merged_df_2['low_pe'] = merged_df_2.apply(calculate_low_pe, axis=1)
    merged_df_2['reasonable_pe'] = merged_df_2.apply(calculate_reasonable_pe, axis=1)
    merged_df_2['high_pe'] =  merged_df_2.apply(calculate_high_pe, axis=1)
    merged_df_2['expensive_pe'] =  merged_df_2.apply(calculate_expensive_pe, axis=1)
    
    merged_df_2['本益比'] = pd.to_numeric(merged_df_2['本益比'], errors='coerce')  # 將本益比轉換為數字，無效值轉為 NaN
    # 可以選擇用 0 或其他適當值填充 NaNs
    merged_df_2 = merged_df_2.fillna(0)


    # merged_df_2['近四季累積兩年前淨利'] = merged_df_2.apply(estimated_growth_rate, axis=1)

    # merged_df_2['預估成長率%'] = (merged_df_2['近四季累積本期淨利（淨損）_調整'] - merged_df_2['近四季累積兩年前淨利']) / merged_df_2['近四季累積兩年前淨利'] * 100
    # merged_df_2['預估成長率%'] = merged_df_2['預估成長率%'].fillna(0)
    # merged_df_2['預估成長率%'] = merged_df_2['預估成長率%'].round(2)
    # merged_df_2['預估成長率%'] = merged_df_2['預估成長率%'].replace(0, np.nan)


    # merged_df_2['預估每股盈餘'] = round(merged_df_2['近四季累積基本每股盈餘_調整'] * (1+(merged_df_2['預估成長率%']/100)), 2)



    # # 
    # import numpy as np

    # condition1 = merged_df_2['預估成長率%'] >= 15
    # condition2 = (5 <= merged_df_2['預估成長率%']) & (merged_df_2['預估成長率%'] < 15)
    # condition3 = (-5 <= merged_df_2['預估成長率%']) & (merged_df_2['預估成長率%'] < 5)
    # condition4 = merged_df_2['預估成長率%'] < -5

    # merged_df_2['PEG倍數'] = np.select([condition1, condition2, condition3, condition4],
    #                                 [merged_df_2['high_pe'], 
    #                                     merged_df_2['resonable_pe'], 
    #                                     merged_df_2['low_pe'], 
    #                                     merged_df_2['cheap_pe']], 
    #                                 default=np.nan)

    # merged_df_2['未來股價預測'] = merged_df_2['預估每股盈餘'] * merged_df_2['PEG倍數']
    # merged_df_2['未來股價預測'] = merged_df_2['未來股價預測'].fillna(0)   
    # merged_df_2['未來股價預測'] = round(merged_df_2['未來股價預測'], 2)
    # merged_df_2['未來股價預測'] = merged_df_2['未來股價預測'].replace(0, np.nan)

    # merged_df_2['安全邊際%'] = (merged_df_2['未來股價預測'] - merged_df_2['收盤價']) / merged_df_2['收盤價'] *100
    # merged_df_2['安全邊際%'] = merged_df_2['安全邊際%'].fillna(0)
    # merged_df_2['安全邊際%'] = round(merged_df_2['安全邊際%'], 2)
    # merged_df_2['安全邊際%'] = merged_df_2['安全邊際%'].replace(0, np.nan)


    # 
    merged_df_2['cheap_pe'] = merged_df_2['cheap_pe'].fillna(np.nan) 
    merged_df_2['cheap_price'] = np.where(
        merged_df_2['近四季累積基本每股盈餘_調整'].isna() | merged_df_2['cheap_pe'].isna(),
        np.nan,
        round(merged_df_2['cheap_pe'] * merged_df_2['近四季累積基本每股盈餘_調整'], 2)
    )

    merged_df_2['low_pe'] = merged_df_2['low_pe'].fillna(np.nan) 
    merged_df_2['low_price'] = np.where(
        merged_df_2['近四季累積基本每股盈餘_調整'].isna() | merged_df_2['low_pe'].isna(),
        np.nan,
        round(merged_df_2['low_pe'] * merged_df_2['近四季累積基本每股盈餘_調整'], 2)
    )

    merged_df_2['reasonable_pe'] = merged_df_2['reasonable_pe'].fillna(np.nan) 
    merged_df_2['reasonable_price'] = np.where(
        merged_df_2['近四季累積基本每股盈餘_調整'].isna() | merged_df_2['reasonable_pe'].isna(),
        np.nan,
        round(merged_df_2['reasonable_pe'] * merged_df_2['近四季累積基本每股盈餘_調整'], 2)
    )

    merged_df_2['high_pe'] = merged_df_2['high_pe'].fillna(np.nan) 
    merged_df_2['high_price'] = np.where(
        merged_df_2['近四季累積基本每股盈餘_調整'].isna() | merged_df_2['high_pe'].isna(),
        np.nan,
        round(merged_df_2['high_pe'] * merged_df_2['近四季累積基本每股盈餘_調整'], 2)
    )

    merged_df_2['expensive_pe'] = merged_df_2['expensive_pe'].fillna(np.nan) 
    merged_df_2['expensive_price'] = np.where(
        merged_df_2['近四季累積基本每股盈餘_調整'].isna() | merged_df_2['expensive_pe'].isna(),
        np.nan,
        round(merged_df_2['expensive_pe'] * merged_df_2['近四季累積基本每股盈餘_調整'], 2)
    )

    merged_df_2['pe'] = round(merged_df_2['收盤價'] / merged_df_2['近四季累積基本每股盈餘_調整'], 2)


    return merged_df_2



#%%
from datetime import datetime, timedelta 
def read_merged_df_2(merged_df_2, date_range):
    if date_range == '1個月':
        one_m_ago = datetime.now() - timedelta(days=31)
        date = one_m_ago.strftime('%Y%m%d')
    elif date_range == '2個月':
        two_m_ago = datetime.now() - timedelta(days=61)
        date = two_m_ago.strftime('%Y%m%d')  
    elif date_range == '3個月':
        three_m_ago = datetime.now() - timedelta(days=92)
        date = three_m_ago.strftime('%Y%m%d')  
    elif date_range == '6個月':
        six_m_ago = datetime.now() - timedelta(days=183)
        date = six_m_ago.strftime('%Y%m%d')   
    elif date_range == '1年':
        one_y_ago = datetime.now() - timedelta(days=365)
        date = one_y_ago.strftime('%Y%m%d')   
    elif date_range == '1年6個月':
        one_y_six_m_ago = datetime.now() - timedelta(days=548)
        date = one_y_six_m_ago.strftime('%Y%m%d') 
    elif date_range == '2年':
        two_y_ago = datetime.now() - timedelta(days=730)
        date = two_y_ago.strftime('%Y%m%d') 
    elif date_range == '2年6個月':
        two_y_six_m_ago = datetime.now() - timedelta(days=913)
        date = two_y_six_m_ago.strftime('%Y%m%d') 
    elif date_range == '3年':
        three_y_ago = datetime.now() - timedelta(days=1095)
        date = three_y_ago.strftime('%Y%m%d') 
        
    merged_df_2['日期'] = pd.to_datetime(merged_df_2['日期'], format='%Y%m%d')
    merged_df_2_date = merged_df_2[merged_df_2['日期'] >= date]
    merged_df_2_date  = merged_df_2_date.sort_values(by='日期')
    merged_df_2_date  = merged_df_2_date.drop_duplicates(subset=['日期'])

    
    return merged_df_2_date




#%%
# 繪圖
# 殖利率 

def plotly_yield(merged_df_2_date):
    import plotly.graph_objs as go
    fig = go.Figure()

    merged_df_2_date['日期'] = pd.to_datetime(merged_df_2_date['日期'], format='%Y%m%d')
    merged_df_2_date['殖利率%'] = pd.to_numeric(merged_df_2_date['殖利率%'])
    merged_df_2_date['pe'] = pd.to_numeric(merged_df_2_date['pe'], errors='coerce')


    # '----' -> NaN
    merged_df_2_date.replace('----', pd.NA, inplace=True)

    # 
    merged_df_2_date['收盤價'] = pd.to_numeric(merged_df_2_date['收盤價'], errors='coerce')

    # 
    merged_df_2_date.dropna(inplace=True)

    # 
    if merged_df_2_date.empty:
        print("DataFrame is empty. No data to plot.")
        return fig
    
    # 
    fig.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['收盤價'],
                            mode='lines',
                            line=dict(color='red', width=1.2),
                            name='收盤價',
                            yaxis='y'))

    # 
    fig.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['殖利率%'],
                            mode='lines', 
                            line=dict(color='blue', width=1.2),
                            name='殖利率%',
                            yaxis='y2'))


    # 
    # stock_code = merged_df_2_date['證券名稱'].iloc[0]
    # stock_name = merged_df_2_date['證券代號'].iloc[0]

    if len(merged_df_2_date) > 0:
        stock_code = merged_df_2_date['證券名稱'].iloc[0]
        stock_name = merged_df_2_date['證券代號'].iloc[0]
    else:
        stock_code = "Unknown"
        stock_name = "Unknown"

    y_range = [merged_df_2_date['收盤價'].min(), merged_df_2_date['收盤價'].max()]
    y_range2 = [merged_df_2_date['殖利率%'].min(), merged_df_2_date['殖利率%'].max()]

    y_range = [merged_df_2_date['收盤價'].min(), merged_df_2_date['收盤價'].max()]
    y_range2 = [merged_df_2_date['殖利率%'].min(), merged_df_2_date['殖利率%'].max()]


    fig.update_layout(title=f'{stock_code} {stock_name} 收盤價、殖利率',
                        xaxis=dict(title='日期', type='date', tickformat='%Y%m%d', tickangle=60),
                        yaxis=dict(title='收盤價', range=y_range),
                        yaxis2=dict(title='殖利率%', overlaying='y', side='right', range=y_range2), 
                        legend=dict(
                            title='',
                            x=1.0,
                            y=1.4,
                            traceorder='normal',
                            orientation='v'
                        ),
                        width=900,
                        height=500,
                    )

    # fig.show()
    return fig



#%%
# 股價淨值比

def plotly_pb(merged_df_2_date):
    import plotly.graph_objs as go
    fig = go.Figure()

    merged_df_2_date['日期'] = pd.to_datetime(merged_df_2_date['日期'], format='%Y%m%d')
    merged_df_2_date['股價淨值比'] = pd.to_numeric(merged_df_2_date['股價淨值比'])

    # '----' -> NaN
    merged_df_2_date.replace('----', pd.NA, inplace=True)

    # 
    merged_df_2_date['收盤價'] = pd.to_numeric(merged_df_2_date['收盤價'], errors='coerce')

    # 
    merged_df_2_date.dropna(inplace=True)

    # 
    fig.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['收盤價'],
                            mode='lines',
                            line=dict(color='red', width=1.2),
                            name='收盤價',
                            yaxis='y'))

    # 
    fig.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['股價淨值比'],
                            mode='lines', 
                            line=dict(color='blue', width=1.2),
                            name='股價淨值比',
                            yaxis='y2'))


    # 
    stock_code = merged_df_2_date['證券名稱'].iloc[0]
    stock_name = merged_df_2_date['證券代號'].iloc[0]

    y_range = [merged_df_2_date['收盤價'].min(), merged_df_2_date['收盤價'].max()]
    y_range2 = [merged_df_2_date['股價淨值比'].min(), merged_df_2_date['股價淨值比'].max()]


    fig.update_layout(title=f'{stock_code} {stock_name} 收盤價、股價淨值比',
                        xaxis=dict(title='日期', type='date', tickformat='%Y%m%d', tickangle=60),
                        yaxis=dict(title='收盤價', range=y_range),
                        yaxis2=dict(title='殖利率%', overlaying='y', side='right', range=y_range2), 
                        legend=dict(
                            title='',
                            x=1.0,
                            y=1.4,
                            traceorder='normal',
                            orientation='v'
                        ),
                        width=900,
                        height=500,
                    )

    # fig.show()
    return fig




#%%
# 本益比河流圖

def plotly_pe(merged_df_2_date):
    import plotly.graph_objs as go
    fig2 = go.Figure()

    merged_df_2_date['日期'] = pd.to_datetime(merged_df_2_date['日期'], format='%Y%m%d')

    # '----' -> NaN
    merged_df_2_date.replace('----', pd.NA, inplace=True)

    # 
    merged_df_2_date['收盤價'] = pd.to_numeric(merged_df_2_date['收盤價'], errors='coerce')

    # 
    merged_df_2_date.dropna(inplace=True)

    # 
    if merged_df_2_date.empty:
        print("DataFrame is empty. No data to plot.")
        return fig2, go.Figure()
    
    # 
    fig2.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['pe'],
                            mode='lines',
                            line=dict(color='red', width=2),
                            name='本益比(倍)',
                            yaxis='y'))

    # 
    fig2.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['expensive_pe'],
                            mode='lines', 
                            line=dict(color='violet', width=1.2),
                            name='昂貴本益比',
                            yaxis='y2'))

    # 
    fig2.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['high_pe'],
                            mode='lines', 
                            line=dict(color='hotpink', width=1.2),
                            name='偏高本益比',
                            yaxis='y3'))

    # 
    fig2.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['reasonable_pe'], 
                            mode='lines', 
                            line=dict(color='orange', width=1.2),
                            name='合理本益比',
                            yaxis='y4'))

    # 
    fig2.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['low_pe'],
                            mode='lines', 
                            line=dict(color='green', width=1.2),
                            name='偏低本益比',
                            yaxis='y5'))

    # 
    fig2.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['cheap_pe'],
                            mode='lines', 
                            line=dict(color='blue', width=1.2),
                            name='便宜本益比',
                            yaxis='y6'))


    # # 
    # stock_code = merged_df_2_date['證券名稱'].iloc[0]
    # stock_name = merged_df_2_date['證券代號'].iloc[0]
    
    if len(merged_df_2_date) > 0:
        stock_code = merged_df_2_date['證券名稱'].iloc[0]
        stock_name = merged_df_2_date['證券代號'].iloc[0]
    else:
        stock_code = "Unknown"
        stock_name = "Unknown"

    min1 = (merged_df_2_date['cheap_pe'].min()) * 0.4
    max1 = (merged_df_2_date['expensive_pe'].max()) * 0.3
    y_range = [merged_df_2_date['cheap_pe'].min()-min1, merged_df_2_date['expensive_pe'].max()+max1]

    fig2.update_layout(title=f'{stock_code} {stock_name} 本益比河流圖',
                        xaxis=dict(title='日期', type='date', tickformat='%Y%m%d', tickangle=60),
                        yaxis=dict(title='', range=y_range),
                        yaxis2=dict(title='', overlaying='y', range=y_range, showline=False), 
                        yaxis3=dict(title='', overlaying='y', range=y_range, showline=False),
                        yaxis4=dict(title='', overlaying='y', range=y_range, showline=False),
                        yaxis5=dict(title='', overlaying='y', range=y_range, showline=False),
                        yaxis6=dict(title='', overlaying='y', range=y_range, showline=False),
                        legend=dict(
                            title='',
                            x=1.0,
                            y=1.4,
                            traceorder='normal',
                            orientation='v'
                        ),
                        width=900,
                        height=600,
                    )

    # fig2.show()


    # 
    import plotly.graph_objs as go
    fig3 = go.Figure()

    merged_df_2_date['日期'] = pd.to_datetime(merged_df_2_date['日期'], format='%Y%m%d')

    # '----' -> NaN
    merged_df_2_date.replace('----', pd.NA, inplace=True)

    # 
    merged_df_2_date['收盤價'] = pd.to_numeric(merged_df_2_date['收盤價'], errors='coerce')

    # 
    merged_df_2_date.dropna(inplace=True)

    # 
    fig3.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['收盤價'],
                            mode='lines',
                            line=dict(color='red', width=2),
                            name='收盤價',
                            yaxis='y'))

    # 
    fig3.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['expensive_price'],
                            mode='lines', 
                            line=dict(color='violet', width=1.2),
                            name='昂貴價',
                            yaxis='y2'))

    # 
    fig3.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['high_price'],
                            mode='lines', 
                            line=dict(color='hotpink', width=1.2),
                            name='偏高價',
                            yaxis='y3'))

    # 
    fig3.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['reasonable_price'], 
                            mode='lines', 
                            line=dict(color='orange', width=1.2),
                            name='合理價',
                            yaxis='y4'))

    # 
    fig3.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['low_price'],
                            mode='lines', 
                            line=dict(color='green', width=1.2),
                            name='偏低價',
                            yaxis='y5'))

    # 
    fig3.add_trace(go.Scatter(x=merged_df_2_date['日期'], 
                            y=merged_df_2_date['cheap_price'],
                            mode='lines', 
                            line=dict(color='blue', width=1.2),
                            name='便宜價',
                            yaxis='y6'))

    # 
    stock_code = merged_df_2_date['證券名稱'].iloc[0]
    stock_name = merged_df_2_date['證券代號'].iloc[0]

    min1 = (merged_df_2_date['cheap_price'].min()) * 0.4
    max1 = (merged_df_2_date['expensive_price'].max()) * 0.3
    y_range = [merged_df_2_date['cheap_price'].min()-min1, merged_df_2_date['expensive_price'].max()+max1]


    # operating_safety_margin = merged_df_2['安全邊際%'].iloc[-1]

    fig3.update_layout(title=f'{stock_code} {stock_name} 收盤價、價值河流圖',
                        xaxis=dict(title='日期', type='date', tickformat='%Y%m%d', tickangle=60),
                        yaxis=dict(title='', range=y_range),
                        yaxis2=dict(title='', overlaying='y', range=y_range, showline=False), 
                        yaxis3=dict(title='', overlaying='y', range=y_range, showline=False),
                        yaxis4=dict(title='', overlaying='y', range=y_range, showline=False),
                        yaxis5=dict(title='', overlaying='y', range=y_range, showline=False),
                        yaxis6=dict(title='', overlaying='y', range=y_range, showline=False),
                        legend=dict(
                            title='',
                            x=1.0,
                            y=1.4,
                            traceorder='normal',
                            orientation='v'
                        ),
                        width=900,
                        height=600,
                    )

    # fig3.show()


    return fig2, fig3