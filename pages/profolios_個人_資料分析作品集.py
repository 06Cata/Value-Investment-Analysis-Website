import streamlit as st 
import pandas as pd 

def main():
    st.title("資料分析作品集")
    st.subheader(" ")
    
    st.write("[★ 【潛力產品、店家銷售分析 Potential products and store sales analysis】- EXCEL](https://hackmd.io/@workcata/SyERmB--T)")
    url = "https://hackmd.io/@workcata/SyERmB--T"
    st.components.v1.iframe(url, height=400, width=750) 
    st.subheader(" ")
    st.subheader(" ")
    
    st.write("[★ 【韓文補習班新課程商業分析 Business Analysis of new Korean language school courses】- EXCEL](https://hackmd.io/@workcata/S1yMfOsfp)")
    url = "https://hackmd.io/@workcata/S1yMfOsfp"
    st.components.v1.iframe(url, height=400, width=750) 
    st.subheader(" ")
    st.subheader(" ")
    
    st.write("[★ 【SF Salaries 薪水分析】ft. Kaggle - Python](https://hackmd.io/@workcata/HyAT-KhJp)")
    url = "https://hackmd.io/@workcata/HyAT-KhJp"
    st.components.v1.iframe(url, height=400, width=750) 
    st.subheader(" ")
    st.subheader(" ")
    
    st.write("[★ 個人對資料分析的理解](https://docs.google.com/document/d/1Rc2MGMd14DQ0x_Z-9Rr5_LaAjLJ6RKy0/edit?usp=sharing&ouid=105016364475687404819&rtpof=true&sd=true)")
    url = "https://docs.google.com/document/d/1Rc2MGMd14DQ0x_Z-9Rr5_LaAjLJ6RKy0/edit?usp=sharing&ouid=105016364475687404819&rtpof=true&sd=true"
    st.components.v1.iframe(url, height=600, width=750) 
    st.subheader(" ")
    st.subheader(" ")

if __name__ == '__main__':
    main()
