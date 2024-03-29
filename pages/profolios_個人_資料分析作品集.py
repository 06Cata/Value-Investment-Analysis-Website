import streamlit as st 
import pandas as pd 

def main():
    st.title("資料分析作品集")
    st.subheader(" ")
    
    st.write("[★ 【潛力產品、店家銷售分析 Potential products and store sales analysis】- EXCEL](https://hackmd.io/@workcata/SyERmB--T)")
    url = "https://hackmd.io/@workcata/SyERmB--T"
    st.components.v1.iframe(url, height=400) 
    st.subheader(" ")
    st.subheader(" ")
    
    st.write("[★ 【韓文補習班新課程商業分析 Business Analysis of new Korean language school courses】- EXCEL](https://hackmd.io/@workcata/S1yMfOsfp)")
    url = "https://hackmd.io/@workcata/S1yMfOsfp"
    st.components.v1.iframe(url, height=400) 
    st.subheader(" ")
    st.subheader(" ")
    
    st.write("[★ 【SF Salaries 薪水分析】ft. Kaggle - Python](https://hackmd.io/@workcata/HyAT-KhJp)")
    url = "https://hackmd.io/@workcata/HyAT-KhJp"
    st.components.v1.iframe(url, height=400) 
    st.subheader(" ")
    

if __name__ == '__main__':
    main()
