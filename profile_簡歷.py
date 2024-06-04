import streamlit as st 
import pandas as pd 
import streamlit.components.v1 as components

def main():
    st.header("Catalina Kuo 郭品妤 簡歷")
    # st.write('''聯絡方式:  [Linkedin](https://www.linkedin.com/in/catalina-k-3a63951a5/)''')
    st.markdown('''聯絡方式 :  <a href="mailto:catalinakuowork@gmail.com">Email</a>、
                <a href="https://www.linkedin.com/in/catalina-k-3a63951a5/">Linkedin</a>、
                <a href="https://github.com/06Cata/">Github</a>、
                <a href="https://www.cakeresume.com/s--ef1WormNkeNevqLwaCXYow--/work-cata">PDF履歷</a>''', unsafe_allow_html=True)


    # 
    st.write("")
    st.write('''大學主修西班牙語商業組，輔華語教學。擔任過一年的華語教師、三年的汽車零件業西班牙語業務。
             工作中使用過一些軟體， 我發現自己對於資料有著濃厚的興趣， 2023年決定轉職， 並報名了文化大學推廣部和程式驅動合作的「大數據人才養成班」。
             我相信有興趣才能走得遠，希望能透過工作加深更多相關技能， 可以透過 Email、Linkedin 聯絡我😊''')
    st.subheader(" ")
    st.subheader(" ")
    
    
    
    
    # 
    data = {
        'Python': ['Requests, Selenium', 'Pandas, Numpy', 'Plotly, Matplotlib, Jieba', 'Streamlit, Flask'],
        '資料處理': ['ELK','Apache Spark','R language',''],
        '資料庫': ['Mysql, SQLServer, SQlite', 'MongoDB','',''],
        '視覺化': ['Tableau', 'Power BI','',''],
        '雲端': ['GCP','Azure','','']
    }
    df = pd.DataFrame(data)

    st.write("技能：")
    st.dataframe(df)
    st.subheader(" ")
    st.subheader(" ")
    
    
    
    
    # 
    st.write("學習筆記 : ")
    st.write("[【Python 視覺化 : Matplotlib (Seaborn)、Plotly】](https://hackmd.io/@workcata/Hk6yp_ay6)")
    url = "https://hackmd.io/@workcata/Hk6yp_ay6"
    st.components.v1.iframe(url, height=350) 
    st.subheader(" ")
    st.write("[【Apache Spark 巨量資料探勘分析】ft.PySpark](https://hackmd.io/@workcata/rkQXQY2Ja)")
    url = "https://hackmd.io/@workcata/rkQXQY2Ja"
    st.components.v1.iframe(url, height=350) 
    st.subheader(" ")
    st.write("[【回歸模型評估: MAE、MAPE、SSE、MSE、RMSE、R²】](https://hackmd.io/@workcata/rk6YuVfNA)")
    url = "https://hackmd.io/@workcata/rk6YuVfNA"
    st.components.v1.iframe(url, height=350) 
    st.subheader(" ")
    st.write("[【 Mysql 系統權限操作】](https://hackmd.io/@workcata/BkWZ13NJ6)")
    url = "https://hackmd.io/@workcata/BkWZ13NJ6"
    st.components.v1.iframe(url, height=350) 
    st.subheader(" ")
    

 
    

if __name__ == '__main__':
    main()

