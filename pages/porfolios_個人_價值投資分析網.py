import streamlit as st 
import pandas as pd 
import numpy as np 
import plotly.express as px 
from pages.profolios_personal_subpages import  為什麼要投資, 基本面_財報分析, 基本面_價值分析, 技術面比較, 買賣交易計算機, 複利計算機   # , 籌碼面

def main():
    st.title("價值投資分析網")
    # st.subheader("")
    
    # 添加連結到新分頁
    page_selection = st.sidebar.radio("Go to", ["為什麼要投資","基本面_財報分析", "基本面_價值分析", "技術面比較",  # , "籌碼面"
                                                "複利計算機", "買賣交易計算機"]) 
    
    if page_selection == "為什麼要投資":
        為什麼要投資.main()
        
    if page_selection == "基本面_財報分析":
        基本面_財報分析.main()
        
    elif page_selection == "基本面_價值分析":
        基本面_價值分析.main()
    
    elif page_selection == "技術面比較":
        技術面比較.main()
        
    # elif page_selection == "籌碼面":
    #     籌碼面.main()
    
    elif page_selection == "複利計算機":
        複利計算機.main()
        
    elif page_selection == "買賣交易計算機":
        買賣交易計算機.main()
        
    
    

    



#%%
if __name__ == '__main__':
    main()
