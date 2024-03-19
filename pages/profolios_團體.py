import streamlit as st 
import pandas as pd 
import numpy as np 
import plotly.express as px 
from pages.profolios_group_subpages import  各縣市ESG公開資訊整合平臺ppt, ITRAVEL_智遊旅伴ppt

def main():
    st.title("團體作品")
    # st.subheader("")
    
    # 添加連結到新分頁
    page_selection = st.sidebar.radio("Go to", ["各縣市ESG公開資訊整合平臺ppt", "ITRAVEL_智遊旅伴ppt"]) 
    
    if page_selection == "各縣市ESG公開資訊整合平臺ppt":
        各縣市ESG公開資訊整合平臺ppt.main()
        
    elif page_selection == "ITRAVEL_智遊旅伴ppt":
        ITRAVEL_智遊旅伴ppt.main()
    



#%%
if __name__ == '__main__':
    main()
