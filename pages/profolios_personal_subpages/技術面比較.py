import streamlit as st 
import random
from pages.profolios_personal_subpages.tw_stock_crawler_030 import get_stock_code_industry
from pages.profolios_personal_subpages.tw_stock_crawler_030_2 import read_daily_price_from_sqlite_all, read_daily_price_from_sqlite,\
    plotly_tec_ma, plotly_tec_rsi, plotly_tec_kd, plotly_tec_box

@st.cache_data
def fetch_data(stock_code):
    try:
        stock_code, stock_name, stock_size, stock_industry, related_data = get_stock_code_industry(stock_code)
    except Exception as e:
        st.write('很抱歉數據庫沒有這隻股票、連不上數據庫，或出現其他錯誤')
        return None
    
    related_datas = []
    for r in related_data:
        related_datas.append(r)
        
    
    # 創建可擴展區域
    with st.expander(f"選擇的是 {stock_code} {stock_name} ，{stock_industry}  ({stock_size})，同產業的有"):
        st.write(related_datas)
    
    st.text("在非洲，每六十秒，就有一分鐘過去，但在這裡，我們不必等那麼久")
    
    
    return read_daily_price_from_sqlite_all(stock_code, stock_size)



def analyze_data(daily_df_all):
    date_range = st.select_slider("選擇日期範圍", options=['1個月', '2個月', '3個月', '6個月', '1年', '1年6個月', '2年', '2年6個月', '3年'], value='3年')
    daily_df = read_daily_price_from_sqlite(daily_df_all, date_range)


    st.subheader("")
    try:
        st.markdown("#### ★ 收盤價 + 移動平均線")
        st.write('''
                 當短期平均線**上穿**長期平均線時(收盤價上穿移動平均線、60MA上穿120MA)，稱為金叉Golden Cross，可能是**買入**訊號  
                 當短期平均線**下穿**長期平均線時(收盤價下穿移動平均線、60MA下穿120MA)，稱為死叉Death Cross，可能是**賣出**訊號  
                     
                 當股價遠離均線時，表示股價可能超買（過高）或超賣（過低），可能發生價格回歸的情況。例如股票處在下跌趨勢，收盤價始終保持在MA下方，通常會被視為賣出訊號；反之則是買入訊號
                 ''')
        fig = plotly_tec_ma(daily_df)
        st.plotly_chart(fig) 
    except:
        pass  
    st.subheader("")
    
    
    try:
        st.markdown("#### ★ 盒鬚圖 + 30MA")
        st.write('''紅K（或稱紅色蠟燭）: 收盤價>開盤價  
                    黑K（或稱黑色蠟燭）: 收盤價<開盤價  
                    連續出現多個紅K，表示股價處於上升趨勢；連續出現多個黑K，表示股價處於下降趨勢
                 ''')
        fig = plotly_tec_box(daily_df)
        st.plotly_chart(fig) 
    except:
        pass  
    st.subheader("")
    
    
    try:
        st.markdown("#### ★ 收盤價 + RSI")
        st.write('''
                RSI的值範圍在0到100之間，通常70作為**超買**，可能會出現價格**下跌**的訊號；30作為**超賣**，可能會出現價格**上漲**的訊號，但同時也有可能市場中的許多投資者都處於恐慌狀態，發生大規模拋售  
                公式:  
                相對強度（RS）= 平均漲幅 / 平均跌幅，一段時間(通常為14天)股價上漲與下跌幅度的平均值，得到相對強度值，RS值越大，漲勢越強；RS值越小，跌勢越強  
                相對強弱指標(RSI) = 100 - (100 / (1 + RS))                  
                 ''')
        st.write("")
        st.write('''
                 當14MA**上穿**RSI線時，14日均線代表短期趨勢，RSI代表強度，可能是**買入**訊號  
                 當14MA**下穿**RSI線時，14日均線代表短期趨勢，RSI代表強度，可能是**賣出**訊號  
                 ''')
        fig = plotly_tec_rsi(daily_df)
        st.plotly_chart(fig)    
    except:
        pass    
    st.subheader("")
    
    
    
    try:
        st.markdown("#### ★ 收盤價 + RSV + KD")
        st.write('''
                RSV（Raw Stochastic Value）是隨機指標，用於衡量價格在一段時間內的相對位置，K值是RSV值的移動平均值，D值則是K值的移動平均值  
                當K值**上穿**D值時，稱為金叉Golden Cross，意味著短期的RSV變動趨勢向上，可能是**買入**訊號  
                當K值**下穿**D值時，稱為死叉Death Cross，意味著短期的RSV變動趨勢向下，可能是**賣出**訊號  
                  
                當KD值>80，為**超買**，可能是**買入**訊號  
                當KD值<20，為**超賣**，可能是**賣出**訊號  
                公式:  
                買進訊號 = K值<D值，轉為 K值>D值，且K值<=20
                 ''')
        fig, fig2, fig3 = plotly_tec_kd(daily_df)
        st.plotly_chart(fig) 
        st.plotly_chart(fig3) 
        st.plotly_chart(fig2) 
    except:
        pass  
    st.subheader("")
    
    
    
    ##################################################
    st.write("")
    st.write("")
    st.write("")
    st.markdown("""
        <div style="text-align: center; margin-top: 50px;">
            <p>以上觀點僅供參考，並不構成任何交易建議或推薦</p>
        </div>
    """, unsafe_allow_html=True)




def main():
    st.subheader("技術面比較")
    st.write('''對價值投資者來說，更著重在長期持有、關注投資的價值  
             比較看看，一些市面上常見的技術分析時機點，與股價實際上的走勢 
             ''')  
    st.write('''資料來源: "公開資訊觀測站"、"台灣證券交易所"、"證券櫃檯買賣中心"，讀取資料庫 [(1)](https://github.com/06Cata/tw_financial_reports1)、[(2)](https://github.com/06Cata/tw_financial_reports2)，
             以上觀點僅供參考，並不構成任何交易建議或推薦。直接拖拉圖片可以放大，右上角🏛️可以重置''')
    
    stock_code = st.text_input("請輸入股票代碼：", value='1101')
    if st.button("查詢"):
        daily_df_all = fetch_data(stock_code)
        
        # 創建可擴展區域_2
        with st.expander(f"已成功抓取到的資料表"):
            st.write(daily_df_all)
        
        if daily_df_all is not None:
            st.session_state.daily_df_all = daily_df_all
    
    if "daily_df_all" in st.session_state:
        analyze_data(st.session_state.daily_df_all)
        
        
        
if __name__ == '__main__':
    main()
