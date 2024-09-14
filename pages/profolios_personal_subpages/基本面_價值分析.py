import streamlit as st 
import random
import pandas as pd

from pages.profolios_personal_subpages.tw_stock_crawler_030 import get_stock_code_industry, get_tables_of_dbtablename, plotly_eps, read__monthly_report_from_sqlite
from pages.profolios_personal_subpages.tw_stock_crawler_030_1 import read_pe_pb_from_sqlite, read_daily_price_from_sqlite_for_pe_pb,\
merge_daily_pe_pb, daily_eps, merge_daily_pe_pb_eps, read_merged_df_2, plotly_yield, plotly_pb, plotly_pe


@st.cache_data
def fetch_data_prepared(stock_code):
    try:
        stock_code, stock_name, stock_size, stock_industry, related_data = get_stock_code_industry(stock_code)
    except Exception as e:
        st.write('很抱歉數據庫沒有這隻股票、連不上數據庫，或出現其他錯誤')
        st.write(f'錯誤訊息: {str(e)}')
        return None
    
    related_datas = []
    for r in related_data:
        related_datas.append(r)
        
    
    # 創建可擴展區域
    with st.expander(f"選擇的是 {stock_code} {stock_name} ，{stock_industry}  ({stock_size})，同產業的有"):
        st.write(related_datas)
        
    
    try:
        dfs, suss_tables = get_tables_of_dbtablename(stock_code)
    except Exception as e:
        st.write('很抱歉數據庫沒有這隻股票、連不上數據庫，或出現其他錯誤')
        st.write(f'錯誤訊息: {str(e)}')
        return None, None
    
    # 創建可擴展區域
    with st.expander(f"用電腦更好看，已成功抓取到的資料"):
            if not dfs and not suss_tables:
                st.write('很抱歉，沒有這檔股票的資料')
                st.write(f'錯誤訊息: {str(e)}')
            else:
                st.write(suss_tables)
                
    st.text("在非洲，每六十秒，就有一分鐘過去，但在這裡，我們不必等那麼久")
    
    try:
        daily_df = read_daily_price_from_sqlite_for_pe_pb(stock_code, stock_size)
    except Exception as e:
        st.write('很抱歉數據庫沒有這隻股票、連不上數據庫，或出現其他錯誤')
        st.write(f'錯誤訊息: {str(e)}')
        return None
    
    # 創建可擴展區域_2
    with st.expander(f"已成功抓取到的盤後資料表"):
        st.write(daily_df)
        
        
    try:
        df_pe_pb = read_pe_pb_from_sqlite(stock_code, stock_size)
    except Exception as e:
        st.write('很抱歉數據庫沒有這隻股票、連不上數據庫，或出現其他錯誤')
        st.write(f'錯誤訊息: {str(e)}')
        return None
    
    # 創建可擴展區域_2
    with st.expander(f"已成功抓取到的盤後資料表"):
        st.write(df_pe_pb)
        
    
   
    merged_df = merge_daily_pe_pb(stock_size, daily_df, df_pe_pb)
    merge_eps_df = daily_eps(dfs)

    
    return  merge_daily_pe_pb_eps(merged_df, merge_eps_df), dfs, stock_code



def analyze_daily_pe_pb(merged_df_2, dfs, stock_code):
    
    date_range = st.select_slider("選擇日期範圍", options=['1個月', '2個月', '3個月', '6個月', '1年', '1年6個月', '2年', '2年6個月', '3年'], value='3年')
    
    merged_df_2_date = read_merged_df_2(merged_df_2, date_range)
        
    st.subheader("")
    try:
        st.markdown("#### ★ 殖利率")
        st.write('''
                高殖利率表示相對較高的股利，但不一定代表股票的良好投資選擇，還是要先觀察財報和業務狀況    
                盈餘穩定的公司適合使用，當殖利率高時，可能是**買入**訊號；殖利率低時，可能是**賣出**訊號。和同業比較，常見的股票殖利率標準在2%至6%  
                公式:  
                公司每股派發的股息 / 股價
                 ''')
        fig = plotly_yield(merged_df_2_date)
        st.plotly_chart(fig) 
    except:
        pass  
    st.subheader("")
    
    
    try:
        st.markdown("#### ★ 股價淨值比")
        st.write('''
                 股價淨值比為公司如果被清算後，一股可以拿回多少? 通常只適合資產密集產業，特別是固定資產和物質資產較多的產業，如製造業、基礎建設、房地產、金融業等。
                 這些公司資產和負債相對穩定，可以比較容易估算其淨資產  
                 公式:  
                 市值（股價*股本數）/ 公司的淨資產總額（總資產-總負債）
                 ''')
        fig = plotly_pb(merged_df_2_date)
        st.plotly_chart(fig) 
    except:
        pass  
    st.subheader("")
    
    
    try:
        st.markdown("#### ★ 本益比河流圖")
        st.write('''
                高本益比表示投資人願意為每股支付更高的價格，可能意味著市場持樂觀態度，但也可能意味著公司被過度高估，應與同業本益比倍數比較  
                本益比不考慮基本面是否惡化，不能只單看目前本益比，要看公司營利、本益比長期趨勢，是否都平穩或緩慢向上，好公司應該是: 基本面財報穩、河流圖長期平穩或向上、本益比(倍)/價格在合理區間下，或與自己過去趨勢比較  
                  
                河流圖趨勢向上，代表預估價格向上 => 獲利增加；河流圖趨勢向下，代表預估價格向下 => 獲利衰退  
                河流圖某段突然向上 => 一次性獲利；河流圖某段突然向下 => 一次性虧損  
                河流圖固定間隔上下 => 淡旺季變化；河流圖不固定間隔上下 => 基本面不穩  
                河流圖尾端變寬 => 市場預期價格擴大；河流圖尾端變窄 => 市場預期價格縮小  
                本益比不斷創低 => 基本面惡化，股價會貼著低估價走  
                  
                公式: 本益比 = 當日收盤價 / 近四季累積EPS  
                        昂貴價 = 近四季累積EPS * 兩年內最高本益比  
                        偏高價 = 近四季累積EPS * ((兩年內最高本益比 + 兩年內中位數本益比) / 2)  
                        合理價 = 近四季累積EPS * 兩年內中位數本益比  
                        便宜價 = 近四季累積EPS * 兩年內最低本益比  
                        便宜價 = 近四季累積EPS * * ((兩年內最低本益比 + 兩年內中位數本益比) / 2)  
                 ''')
        fig2, fig3 = plotly_pe(merged_df_2_date)
        st.plotly_chart(fig2) 
        st.plotly_chart(fig3) 
    except:
        pass  
    st.subheader("")
    
    
    try:
        # 007-2 包成def
        # 月報看每月營收
        # 銀行業ok
        st.markdown("#### ★ 月營收比較")
        fig0 = read__monthly_report_from_sqlite(stock_code)
        st.write('''
            季報還未出來時，可以觀察每月營收、與去年當月營收比較，並參考EPS  
            假設有公司月營收、EPS都低，但營業活動現金流高，可能營業成本降低、減少資本支出、加快應收帳款週轉...
                    ''')
        st.plotly_chart(fig0)
        st.session_state.monthly_report_fig = fig0
    except:
        pass
    
    
    try:
        # 007 包成def
        # eps
        # 銀行業ok
        st.markdown("#### ★ EPS")
        fig, fig2, fig3 = plotly_eps(dfs)
        st.write('''
            每股盈餘（Earnings Per Share）  
            是一個衡量公司盈利能力的財務指標，用於評估公司在每股普通股上實現的盈利情況  
            公式:  
                損益表中的「基本每股盈餘」，Q4單季為全年度-(Q1+Q2+Q3)
                    ''')
        st.plotly_chart(fig)
        st.plotly_chart(fig2)
        st.plotly_chart(fig3)
        st.session_state.monthly_report_fig = fig
        st.session_state.eps_fig = fig2
        st.session_state.eps_fig2 = fig3
    except:
        pass   
    
    
    
    ######################################################
    st.write("")
    st.write("")
    st.write("")
    st.markdown("""
        <div style="text-align: center; margin-top: 50px;">
            <p>以上觀點僅供參考，並不構成任何交易建議或推薦</p>
        </div>
    """, unsafe_allow_html=True)



def main():
    st.subheader("基本面: 價值分析")
    st.write('''選擇好的股票只是投資的第一步，更重要的是在適當的時間，以合理的價格買進  
             價值投資者通常專注於股票的內在價值，尋找被低估的股票，以便在未來獲得良好的回報
             ''')  
    st.write('''資料來源: "公開資訊觀測站"、"台灣證券交易所"、"證券櫃檯買賣中心"，讀取資料庫 [(1)](https://github.com/06Cata/tw_financial_reports1)、[(2)](https://github.com/06Cata/tw_financial_reports2)、\
            [(3)](https://github.com/06Cata/tw_financial_reports3)。以上觀點僅供參考，並不構成任何交易建議或推薦。直接拖拉圖片可以放大，右上角🏛️可以重置''')
    
    stock_code = st.text_input("請輸入股票代碼：", value='2885')
    if st.button("查詢"):
        
        try:
            merged_df_2, dfs, stock_code = fetch_data_prepared(stock_code)
        except Exception as e:
            st.write('很抱歉數據庫沒有這隻股票、連不上數據庫，或出現其他錯誤')
            return None
        
        if merged_df_2 is not None:
            st.session_state.merged_df_2 = merged_df_2
            st.session_state.dfs = dfs
            st.session_state.stock_code = stock_code
    
    if "merged_df_2" in st.session_state:
        analyze_daily_pe_pb(st.session_state.merged_df_2, st.session_state.dfs, st.session_state.stock_code)   


if __name__ == '__main__':
    main()

 