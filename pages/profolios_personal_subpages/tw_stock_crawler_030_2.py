#%%
# 技術面比較
#%%
import requests
import sqlite3
import pandas as pd
import tempfile
import os
from datetime import datetime, timedelta 



def download_daily_price_db(stock_size):
    
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



#%%
def read_daily_price_from_sqlite_all(stock_code, stock_size):
    db_path1 = download_daily_price_db(stock_size)
    conn = sqlite3.connect(db_path1)
    table_name = 'daily_price_2019' if stock_size == '上市' else 'daily_price_otc_2019'
    
    query = f"SELECT * FROM {table_name} WHERE 證券代號={stock_code} ORDER BY 日期 ASC"
    daily_df_all = pd.read_sql_query(query, conn)
    conn.close()
    os.remove(db_path1)
    daily_df_all.drop_duplicates(subset=['證券代號', '日期'], keep='first', inplace=True)
    
    return daily_df_all



#%%

def read_daily_price_from_sqlite(daily_df_all, date_range):
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
        
    daily_df_all['日期'] = pd.to_datetime(daily_df_all['日期'], format='%Y%m%d')
    daily_df = daily_df_all[daily_df_all['日期'] >= date]
    daily_df = daily_df.sort_values(by='日期')
    daily_df = daily_df.drop_duplicates(subset=['日期'])

    
    return daily_df



#%%
# def download_daily_price_db_for_pe_pb(stock_size):
    
#     if stock_size == '上市':
#         url = 'https://github.com/06Cata/tw_financial_reports2/raw/main/daily_price.db'
#     elif stock_size == '上櫃':
#         url = 'https://github.com/06Cata/tw_financial_reports2/raw/main/daily_price_otc.db'
    
#     response = requests.get(url)
#     temp_file = tempfile.NamedTemporaryFile(delete=False)
#     temp_file.write(response.content)
#     temp_file_path = temp_file.name
#     temp_file.close()
#     return temp_file_path

# def read_daily_price_from_sqlite(stock_code, stock_size, date_range):
#     db_path = download_daily_price_db(stock_size)
#     conn = sqlite3.connect(db_path)
#     table_name = 'daily_price_2021' if stock_size == '上市' else 'daily_price_otc_2021'
    
#     if date_range == '1個月':
#         one_m_ago = datetime.now() - timedelta(days=31)
#         date = one_m_ago.strftime('%Y%m%d')
#     elif date_range == '2個月':
#         two_m_ago = datetime.now() - timedelta(days=61)
#         date = two_m_ago.strftime('%Y%m%d')  
#     elif date_range == '3個月':
#         three_m_ago = datetime.now() - timedelta(days=92)
#         date = three_m_ago.strftime('%Y%m%d')  
#     elif date_range == '6個月':
#         six_m_ago = datetime.now() - timedelta(days=183)
#         date = six_m_ago.strftime('%Y%m%d')   
#     elif date_range == '1年':
#         one_y_ago = datetime.now() - timedelta(days=365)
#         date = one_y_ago.strftime('%Y%m%d')   
#     elif date_range == '1年6個月':
#         one_y_six_m_ago = datetime.now() - timedelta(days=548)
#         date = one_y_six_m_ago.strftime('%Y%m%d') 
#     elif date_range == '2年':
#         two_y_ago = datetime.now() - timedelta(days=730)
#         date = two_y_ago.strftime('%Y%m%d') 
#     elif date_range == '2年6個月':
#         two_y_six_m_ago = datetime.now() - timedelta(days=913)
#         date = two_y_six_m_ago.strftime('%Y%m%d') 
#     elif date_range == '3年':
#         three_y_ago = datetime.now() - timedelta(days=1095)
#         date = three_y_ago.strftime('%Y%m%d') 
        
#     date_y = int(date[:4])
#     date_m = int(date[4:6])
#     date_d = int(date[6:8])
    
#     query = f"SELECT * FROM {table_name} WHERE 證券代號={stock_code} AND 日期 >= '{date_y}-{date_m}-{date_d}' ORDER BY 日期 ASC"
#     daily_df = pd.read_sql_query(query, conn)
#     conn.close()
#     os.remove(db_path)
#     daily_df.drop_duplicates(subset=['證券代號', '日期'], keep='first', inplace=True)
    
#     return daily_df


# 
# stock_code = 2330
# stock_size = '上市'
# date_range = '3年'
# daily_df = read_daily_price_from_sqlite(stock_code, stock_size, date_range)

# daily_df



#%%
# 收盤+MA

def plotly_tec_ma(daily_df):

    try:
        df_ma = daily_df.copy()

        import plotly.graph_objs as go
        fig = go.Figure()

        df_ma['日期'] = pd.to_datetime(df_ma['日期'], format='%Y%m%d')
        
        # '----' -> NaN
        df_ma.replace('----', pd.NA, inplace=True)

        # 
        df_ma['開盤價'] = pd.to_numeric(df_ma['開盤價'], errors='coerce')
        df_ma['最高價'] = pd.to_numeric(df_ma['最高價'], errors='coerce')
        df_ma['最低價'] = pd.to_numeric(df_ma['最低價'], errors='coerce')
        df_ma['收盤價'] = pd.to_numeric(df_ma['收盤價'], errors='coerce')

        # 
        df_ma.dropna(inplace=True)

        # 
        fig.add_trace(go.Scatter(x=df_ma['日期'], 
                                y=df_ma['收盤價'],
                                mode='lines',
                                line=dict(color='red', width=1.2),
                                name='收盤價',
                                yaxis='y'))

        # 
        ma = 30
        fig.add_trace(go.Scatter(x=df_ma['日期'], 
                                y=df_ma['收盤價'].rolling(window=ma, min_periods=1).mean(),
                                mode='lines', 
                                line=dict(color='blue', width=1.2),
                                name='30MA',
                                yaxis='y2'))
        
        # 
        ma2 = 60
        fig.add_trace(go.Scatter(x=df_ma['日期'], 
                                y=df_ma['收盤價'].rolling(window=ma2, min_periods=1).mean(),
                                mode='lines', 
                                line=dict(color='green', width=1.2),
                                name='60MA',
                                yaxis='y3'))
        # 
        ma3 = 120
        fig.add_trace(go.Scatter(x=df_ma['日期'], 
                                y=df_ma['收盤價'].rolling(window=ma3, min_periods=1).mean(),
                                mode='lines', 
                                line=dict(color='orange', width=1.2),
                                name='120MA',
                                yaxis='y4'))

        # 
        ma4 = 240
        fig.add_trace(go.Scatter(x=df_ma['日期'], 
                                y=df_ma['收盤價'].rolling(window=ma4, min_periods=1).mean(),
                                mode='lines', 
                                line=dict(color='hotpink', width=1.2),
                                name='240MA',
                                yaxis='y5'))


        # 
        stock_code = df_ma['證券名稱'].iloc[0]
        stock_name = df_ma['證券代號'].iloc[0]
        
        y_range = [df_ma['收盤價'].min(), df_ma['收盤價'].max()]
        
        fig.update_layout(title=f'{stock_code} {stock_name} 收盤價、MA趨勢線',
                            xaxis=dict(title='日期', type='date', tickformat='%Y%m%d', tickangle=60),
                            yaxis=dict(title='收盤價', range=y_range),
                            yaxis2=dict(title='MA', overlaying='y', side='right', range=y_range), 
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
                            width=900,
                            height=500,
                        )

        # fig.show()
    except Exception as e:
        print(f"Error generating 30MA plot: {e}")
        
    return fig
    




#%%
# 盒鬚圖 + 30MA  

def plotly_tec_box(daily_df):
    import pandas as pd
    import plotly.graph_objects as go

    df_box = daily_df.copy()

    df_box['日期'] = pd.to_datetime(df_box['日期'], format='%Y%m%d')
    
    # '----' -> NaN
    df_box.replace('----', pd.NA, inplace=True)

    # 
    df_box['開盤價'] = pd.to_numeric(df_box['開盤價'], errors='coerce')
    df_box['最高價'] = pd.to_numeric(df_box['最高價'], errors='coerce')
    df_box['最低價'] = pd.to_numeric(df_box['最低價'], errors='coerce')
    df_box['收盤價'] = pd.to_numeric(df_box['收盤價'], errors='coerce')

    # 
    df_box.dropna(inplace=True)

    # 
    fig = go.Figure(
        data=[go.Candlestick(x=df_box.index,
                            open=df_box['開盤價'],
                            high=df_box['最高價'],
                            low=df_box['最低價'],
                            close=df_box['收盤價'])]
    )

    # 
    ma = 30
    trend_line = go.Scatter(
        x=df_box.index,
        y=df_box['收盤價'].rolling(window=ma, min_periods=1).mean(),  
        mode='lines',
        name=f'{ma}日均',
        line=dict(color='blue',width=1.2)
    )
    fig.add_trace(trend_line)
    
    # 
    ma2 = 60
    trend_line = go.Scatter(
        x=df_box.index,
        y=df_box['收盤價'].rolling(window=ma2, min_periods=1).mean(),  
        mode='lines',
        name=f'{ma2}日均',
        line=dict(color='green',width=1.2)
    )
    fig.add_trace(trend_line)
    
    # 
    ma3 = 120
    trend_line = go.Scatter(
        x=df_box.index,
        y=df_box['收盤價'].rolling(window=ma3, min_periods=1).mean(),  
        mode='lines',
        name=f'{ma3}日均',
        line=dict(color='orange',width=1.2)
    )
    fig.add_trace(trend_line)
    
    # 
    ma4 = 240
    trend_line = go.Scatter(
        x=df_box.index,
        y=df_box['收盤價'].rolling(window=ma4, min_periods=1).mean(),  
        mode='lines',
        name=f'{ma4}日均',
        line=dict(color='hotpink',width=1.2)
    )
    fig.add_trace(trend_line)

    


    # 
    stock_code = df_box['證券名稱'].iloc[0] 
    stock_name = df_box['證券代號'].iloc[0] 

    fig.update_layout(title=f'{stock_code} {stock_name} 盒鬚圖、移動平均線',
                    xaxis=dict(title='日期', tickangle=60),
                    yaxis=dict(title='MA'),
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

    # fig.show()
    
    return fig





#%%
# 收盤+RSI

def plotly_tec_rsi(daily_df):
    import pandas as pd
    import numpy as np

    df_rsi = daily_df.copy()

    rsi_day=14

    df_rsi['價差'] = df_rsi['收盤價'].diff()

    df_rsi['漲'] = np.where(df_rsi['價差'] > 0, df_rsi['價差'], 0)
    df_rsi['跌'] = np.where(df_rsi['價差'] < 0, -df_rsi['價差'], 0)
    df_rsi['平均漲幅'] = df_rsi['漲'].rolling(window=rsi_day, min_periods=1).mean()
    df_rsi['平均跌幅'] = df_rsi['跌'].rolling(window=rsi_day, min_periods=1).mean()


    df_rsi['rs'] = round(df_rsi['平均漲幅'] / df_rsi['平均跌幅'], 2)   # RS值越大，漲勢越強；RS值越小，跌勢越強
    df_rsi['rsi'] = round(100 - (100 / (1 + df_rsi['rs'])), 2)

    
    # 
    import plotly.graph_objs as go
    fig = go.Figure()

    df_rsi['日期'] = pd.to_datetime(df_rsi['日期'], format='%Y%m%d')
    # '----' -> NaN
    df_rsi.replace('----', pd.NA, inplace=True)

    # 
    df_rsi['開盤價'] = pd.to_numeric(df_rsi['開盤價'], errors='coerce')
    df_rsi['最高價'] = pd.to_numeric(df_rsi['最高價'], errors='coerce')
    df_rsi['最低價'] = pd.to_numeric(df_rsi['最低價'], errors='coerce')
    df_rsi['收盤價'] = pd.to_numeric(df_rsi['收盤價'], errors='coerce')

    df_rsi.dropna(inplace=True)

    # 
    fig.add_trace(go.Scatter(x=df_rsi['日期'], 
                            y=df_rsi['收盤價'],
                            mode='lines', 
                            line=dict(color='red', width=1.2),
                            name='收盤價',
                            yaxis='y'))

    # 
    ma = 14
    fig.add_trace(go.Scatter(x=df_rsi['日期'], 
                            y=df_rsi['收盤價'].rolling(window=ma, min_periods=1).mean(),
                            mode='lines', 
                            line=dict(color='green', width=1.2),
                            name='14MA',
                            yaxis='y2'))
    
    
    # 
    fig.add_trace(go.Scatter(x=df_rsi['日期'], 
                            y=df_rsi['rsi'],
                            mode='lines', 
                            line=dict(color='blue', width=1.2),
                            name='RSI',
                            yaxis='y3'))


    
    #
    stock_code = df_rsi['證券名稱'].iloc[0]
    stock_name = df_rsi['證券代號'].iloc[0]
    
    y_range = [df_rsi['收盤價'].min(), df_rsi['收盤價'].max()]
    y_range2 = [df_rsi['rsi'].min(), df_rsi['rsi'].max()]
    
    fig.update_layout(title=f'{stock_code} {stock_name} 收盤價、RSI趨勢線',
                        xaxis=dict(title='日期', type='date', tickformat='%Y%m%d', tickangle=60),
                        yaxis=dict(title='收盤價',range=y_range),
                        yaxis2=dict(title='', overlaying='y',range=y_range, showline=False),
                        yaxis3=dict(title='RSI', overlaying='y', side='right',range=y_range2),
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
# RSV+KD

def plotly_tec_kd(daily_df):
    import numpy as np

    df_kd = daily_df.copy()

    kd_period = 14
    
    
    # '----' -> NaN
    df_kd.replace('----', pd.NA, inplace=True)

    # 將 NaN 值填充為前一個有效值
    df_kd.fillna(method='ffill', inplace=True)
    
    # 
    df_kd['開盤價'] = pd.to_numeric(df_kd['開盤價'], errors='coerce')
    df_kd['最高價'] = pd.to_numeric(df_kd['最高價'], errors='coerce')
    df_kd['最低價'] = pd.to_numeric(df_kd['最低價'], errors='coerce')
    df_kd['收盤價'] = pd.to_numeric(df_kd['收盤價'], errors='coerce')


    df_kd['rsv'] = (df_kd['收盤價'] - df_kd['最低價'].rolling(window=kd_period).min())/\
                (df_kd['最低價'].rolling(window=kd_period).max() - df_kd['最低價'].rolling(window=kd_period).min()) * 100
                
    df_kd['k'] = np.nan
    df_kd['d'] = np.nan


    # 初始值_第一天RSV
    first_rsv_index = df_kd['rsv'].first_valid_index()
    next_index = df_kd.index.get_loc(first_rsv_index) + 1
    df_kd.at[df_kd.index[next_index], 'k'] = df_kd['rsv'][first_rsv_index]
    df_kd.at[df_kd.index[next_index], 'd'] = df_kd['rsv'][first_rsv_index]


    # K 值、D 值
    for i in range(next_index + 1, len(df_kd)):
        df_kd.at[df_kd.index[i], 'k'] = df_kd.iloc[i-1]['k'] * (2/3) + df_kd.iloc[i]['rsv'] * (1/3)
        df_kd.at[df_kd.index[i], 'd'] = df_kd.iloc[i-1]['d'] * (2/3) + df_kd.iloc[i]['k'] * (1/3)

    df_kd['rsv'] = round(df_kd['rsv'], 2)
    df_kd['k'] = round(df_kd['k'],2) 
    df_kd['d'] = round(df_kd['d'],2)


    df_kd['日期'] = pd.to_datetime(df_kd['日期'], format='%Y%m%d')
    
    # 
    import plotly.graph_objs as go
    fig = go.Figure()


    # '----' -> NaN
    df_kd.replace('----', pd.NA, inplace=True)

    # 
    df_kd['開盤價'] = pd.to_numeric(df_kd['開盤價'], errors='coerce')
    df_kd['最高價'] = pd.to_numeric(df_kd['最高價'], errors='coerce')
    df_kd['最低價'] = pd.to_numeric(df_kd['最低價'], errors='coerce')
    df_kd['收盤價'] = pd.to_numeric(df_kd['收盤價'], errors='coerce')

    # 
    df_kd.dropna(inplace=True)

    # 
    fig.add_trace(go.Scatter(x=df_kd['日期'], 
                            y=df_kd['收盤價'],
                            mode='lines',
                            line=dict(color='red', width=1.5),
                            name='收盤價',
                            yaxis='y'))

    # 
    fig.add_trace(go.Scatter(x=df_kd['日期'], 
                            y=df_kd['k'],
                            mode='lines', 
                            line=dict(color='blue', width=1.5),
                            name='K線',
                            yaxis='y2'))

    # 
    fig.add_trace(go.Scatter(x=df_kd['日期'], 
                            y=df_kd['d'],
                            mode='lines', 
                            line=dict(color='green', width=1.5),
                            name='D線',
                            yaxis='y3'))


    # 
    stock_code = df_kd['證券名稱'].iloc[0]
    stock_name = df_kd['證券代號'].iloc[0]

    y_range = [df_kd['收盤價'].min(), df_kd['收盤價'].max()]
    
    min_kd = min(df_kd['k'].min(), df_kd['d'].min())
    max_kd = max(df_kd['k'].max(), df_kd['d'].max())
    y_range2 = [min_kd, max_kd]
    
    fig.update_layout(title=f'{stock_code} {stock_name} 收盤價、KD趨勢線',
                        xaxis=dict(title='日期', type='date', tickformat='%Y%m%d', tickangle=60),
                        yaxis=dict(title='收盤價', side='left',range=y_range),
                        yaxis2=dict(title='K線、D線', overlaying='y', side='right', range=y_range2),  # overlaying='y', side='right', 
                        yaxis3=dict(title='', overlaying='y', side='right', range=y_range2),
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
    
    
    
    #     
    df_kd_time = df_kd[['證券名稱','證券代號','收盤價', 'rsv', 'k', 'd','日期']]

    buy_condition = (df_kd_time['k'] > df_kd_time['d']) & (df_kd_time['k'] <=20) & (df_kd_time['k'].shift(1) < df_kd_time['d'].shift(1))
    df_kd_time.loc[:, '買進'] = buy_condition.astype(int)



    # 
    import plotly.graph_objs as go
    fig2 = go.Figure()


    # '----' -> NaN
    df_kd_time.replace('----', pd.NA, inplace=True)

    # 

    df_kd_time['收盤價'] = pd.to_numeric(df_kd_time['收盤價'], errors='coerce')


    # 
    df_kd_time.dropna(inplace=True)

    # 
    fig2.add_trace(go.Scatter(x=df_kd_time['日期'], 
                            y=df_kd_time['收盤價'],
                            mode='lines',
                            line=dict(color='red', width=1.5),
                            name='收盤價',
                            yaxis='y1'))

    # 
    fig2.add_trace(go.Scatter(x=df_kd_time['日期'], 
                            y=df_kd_time['買進'],
                            mode='lines', 
                            line=dict(color='orange', width=1.2),
                            name='KD買進訊號',
                            yaxis='y2'))

    # 
    stock_code = df_kd_time['證券名稱'].iloc[0]
    stock_name = df_kd_time['證券代號'].iloc[0]

    min1 = df_kd_time['收盤價'].min()
    max1 = df_kd_time['收盤價'].max()
    y_range21 = [min1,max1]


    y_range22 = [0,1]

    fig2.update_layout(title=f'{stock_code} {stock_name} 收盤價、KD買進訊號',
                        xaxis=dict(title='日期', type='date', tickformat='%Y%m%d', tickangle=60),
                        yaxis=dict(title='收盤價', range=y_range21),
                        yaxis2=dict(title='KD買進訊號', overlaying='y', side='right',range=y_range22),
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

    # fig2.show()



    # 
    import plotly.graph_objs as go
    fig3 = go.Figure()


    # '----' -> NaN
    df_kd_time.replace('----', pd.NA, inplace=True)

    # 
    fig3.add_trace(go.Scatter(x=df_kd_time['日期'], 
                            y=df_kd_time['k'],
                            mode='lines',
                            line=dict(color='green', width=1.5),
                            name='K線',
                            yaxis='y1'))

    # 
    fig3.add_trace(go.Scatter(x=df_kd_time['日期'], 
                            y=df_kd_time['d'],
                            mode='lines',
                            line=dict(color='blue', width=1.5),
                            name='D線',
                            yaxis='y2'))

    # 
    fig3.add_trace(go.Scatter(x=df_kd_time['日期'], 
                            y=df_kd_time['買進'],
                            mode='lines', 
                            line=dict(color='orange', width=1.2),
                            name='KD買進訊號',
                            yaxis='y3'))

    # 
    stock_code = df_kd_time['證券名稱'].iloc[0]
    stock_name = df_kd_time['證券代號'].iloc[0]

    min_kd31 = min(df_kd_time['k'].min(), df_kd_time['d'].min())
    max_kd31 = max(df_kd_time['k'].max(), df_kd_time['d'].max())
    y_range31 = [min_kd31, max_kd31]

    y_range32 = [0,1]

    fig3.update_layout(title=f'{stock_code} {stock_name} KD線、KD買進訊號',
                        xaxis=dict(title='日期', type='date', tickformat='%Y%m%d', tickangle=60),
                        yaxis=dict(title='K線、D線', range=y_range31),
                        yaxis2=dict(title='', overlaying='y', side='left', range=y_range31), 
                        yaxis3=dict(title='KD買進訊號', overlaying='y', side='right',range=y_range32),
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

    # fig3.show()


    return fig, fig2, fig3

 

 

 



