import streamlit as st 
import pandas as pd 
import numpy as np 
import plotly.express as px 


def main():
    # 
    st.title("自傳")
    st.subheader("")
    
    st.write('''你好，我叫郭品妤，大學讀西班牙語系商業組，輔華語教學系華語教學組，之前擔任過一年的華語教師、三年的汽車零件業西班牙語業務。
             業務工作中，使用過一些軟體， 我發現自己對於資料有著濃厚的興趣， 2023年決定轉職， 並報名了文化大學推廣部和程式驅動合作的「AI 大數據人才養成班」  ''')  
               
    st.write('''轉職班結束後，很多同學當系統工程師，少數當資料分析、後端，我認真思考自已適合做什麼類型的工作? 我發現自己滿喜歡做商業分析、資料分析，覺得轉職班
                做過的電商平臺分析專題很有趣  ''')
              
    st.write('''可能是因為我國中時，我爸爸辭掉電子工程師的工作，他一直有個咖啡夢，加盟了咖啡店，做了幾年沒什麼賺，之後便宜頂讓掉，改做火鍋店。有次我問他 : 你說火鍋好賺很多，
            咖啡和火鍋毛利多少? 但他沒有認真計算過；
            可能是因為大學快畢業時，透過朋友接觸到股票，我問她 : 為什麼會買這檔? 她說 : 憑感覺、看線圖、聽粉專的KOL推薦，辦了證券戶、買書認識財報，我了解到數據、會行銷的重要性；
            可能是因為開始工作後，發現EXCEL業務報表可以做的很fancy，可以知道每個客戶平均毛利大約多少，我們賺了多少，業績匯報時，老闆會聽得更具體  ''')  
    
    st.write('''轉職後，目前在接案為主的乙方，主要做資料研究及量化商業分析。工作內容大致為 : 
             根據客戶產業，設置關鍵字、排除字，從資料庫的提取資料，做資料清整；與同事共同維護機器學習模型做產品分類；Tableau 商業報表建立、數據解讀
             ''')   
    
    
    # st.write('''幾年前，哥哥開始接手火鍋店，但他後期沒有認真了解市場，改了很多品項、加賣了冷凍海鮮， 過了一段時間後，他把店頂讓了，之後去澳洲拿打工度假簽證。
    #          所以我想做一個很能洞察出數據問題的分析師，不管在生活、工作上都很實用，謝謝!''')
    
    st.subheader("")
    st.subheader("")
    
    st.subheader("未來生涯規劃")
    st.subheader("")

    st.write('''上了一些Udemy課後，有一些機器學習分群、分類的方法，都覺得滿有趣的，會這些技能對分析師來說很加分。我預計在未來補好數理統計、微積分、機率概論相關科目，
             學習更多機器學習，有工作經歷後再申請相關的(資管、資料科學…)在職碩士''')  
    
    

#%%
if __name__ == '__main__':
    main()
