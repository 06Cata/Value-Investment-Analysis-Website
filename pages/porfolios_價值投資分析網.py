import streamlit as st 
import pandas as pd 
import numpy as np 
import plotly.express as px 
from pages.profolios_personal_subpages import  為什麼要投資, 基本面_財報分析, 基本面_價值分析, 技術面比較, 買賣交易計算機, 複利計算機   # , 籌碼面

def main():
    st.title("價值投資分析網")
    st.write('''爬蟲爬取資產負債表、損益表、現金流量表、盤後資料存進sqlite，
             主要使用pandas整理，plotly繪圖。代碼上傳到github，部屬在streamlit上。使用者送出公司代號後，會下載github上的db，繪製相關指標
            ''')
    # st.subheader("")
    
    # 添加連結到新分頁
    page_selection = st.sidebar.radio("Go to", ["基本面_財報分析", "基本面_價值分析", "技術面比較",  # , "籌碼面"
                                                "為什麼要投資", "複利計算機", "買賣交易計算機"]) 
        
    if page_selection == "基本面_財報分析":
        基本面_財報分析.main()
        
    elif page_selection == "基本面_價值分析":
        基本面_價值分析.main()
    
    elif page_selection == "技術面比較":
        技術面比較.main()
        
    # elif page_selection == "籌碼面":
    #     籌碼面.main()
    
    elif page_selection == "為什麼要投資":
        為什麼要投資.main()
    
    elif page_selection == "複利計算機":
        複利計算機.main()
        
    elif page_selection == "買賣交易計算機":
        買賣交易計算機.main()
        
    
    

    



#%%
if __name__ == '__main__':
    main()
