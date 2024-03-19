import streamlit as st 
import pandas as pd 
import numpy as np 
import plotly.express as px 


def main():
    # 
    st.title("學經歷")
    st.subheader("")
    st.subheader("")
    
    
    st.subheader("大數據人才養成班")
    st.write("**文化大學推廣部+程式驅動 ( Mar, 2023 - Sep, 2023 ) 半年**")
    st.write("在養成班中，學習了Linux、Python、資料庫、視覺化、分佈式系統、Git等技能。後期利用實習的機會，學習ELK平臺，做了\
            「各縣市ESG公開資訊整合平臺」，也和組員做了「ITRAVEL 智遊旅伴」。")
    st.write("為了深入學習，自九月底以來，觀看了Udemy及一些統計系開放式平臺課程，來加強技能、練習Kaggle案例，希望能彌補自身背景的不足，\
            將筆記寫在HackMD，也做了自己的作品「價值投資分析網」。")
    st.subheader("")
    st.subheader("")
    
    
    st.subheader("西班牙語業務 • 數位行銷")
    st.write("**CARICO ENTERPRISE CO., LTD, 新北市 ( Mar, 2020 - Feb, 2023 ) 三年**")
    st.write("業務開發 : 負責開發和維繫拉丁美洲B2B市場，確保為客戶高效地解決問題，開發過薩爾瓦多、宏都拉斯、英國的第一個長期客戶。") 
    st.write("數位行銷 : 與媒體公司的合作中，開啟新的西班牙語網站專案，每日訪客人數從10~20人/日到，平均超過300人/日，增長率超過 1400%；\
                開啟新的 SEO 項目、投放廣告及制定關鍵字計畫，使用 Google Analystic, Google Search Console, Ads, GTM，讓至少三個目標\
                關鍵詞上台灣Google搜索引擎首頁排名。") 
    st.write("這些經歷讓我發現自己對資料分析的興趣，搜尋很多資訊後，找到勞動部提供資源的產業新尖兵計畫，其中的大數據人才養成班也成為我轉職的契機。") 
    st.subheader("")
    st.subheader("")
    
    
    st.subheader("全職中文教師")
    st.write("**Centro Cultural Chino Panameño, Panama City ( Feb, 2019 - Jan, 2020 ) 一年**")
    st.write("學習華語教學課程後，我想嘗試當華語教師，便申請了巴拿馬合作計畫項目，當時被分配到一所私立學校擔任三年級學生的中文教師，\
                該項目可以在當地正職工作，同時拿到輔系學分。這些經歷讓我更容易適應不同的環境，不太會擔心轉職後不適應的問題。")
    st.subheader("")
    st.subheader("")
    
    
    st.subheader("學生實習")
    st.write("**Hilos Kingtex, Akai Internacional S.A de C.V., Mexico ( Jun, 2017 - Jan, 2018 ) 七個月**")
    st.write("公司主要進出口、加工線材，在倉管部，統計和協調每日生產計劃；在會計行政部門，賬目對賬、文件處理、生產產品顏色檢查、\
                與當地業務團隊合作協助催帳、核銷賬目。這些經歷讓我對商業運作有更深的理解，企業財務管理的重要性，及如何與不同部門合作。")
    st.subheader("")
    st.subheader("")
    
    
    # 
    st.subheader("學歷: ")
    st.write('''文藻外語大學  
            主 : 西班牙語文學系 商業組  2014-2018  
            輔 : 應用華語文學系 華語教學組  2016-2020''')
    


#%%
if __name__ == '__main__':
    main()
