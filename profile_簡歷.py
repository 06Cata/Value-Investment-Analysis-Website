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
    st.write('''我是一名數據分析師，目前於資訊服務出版業工作，負責資料清整、量化分析、模型維護及視覺化。使用SQL、Python、Tableau，並撰寫商業報告。\

             個人因興趣做了價值投資分析網，並定期更新財報於GitHub上。曾擔任西班牙語業務三年，具備數位行銷與開發拉美市場的經驗，轉職後專注於數據分析與機器學習領域的技能提升''')

    st.write('''我相信有興趣才能走得遠，希望能透過工作加深更多相關技能， 可以透過 Email、Linkedin、Cake 聯絡我😊''')

    st.subheader(" ")
    
    
    
    
    # 
    data = {
        'Python': ['Pandas, Numpy', 'Plotly, Matplotlib','Requests, Selenium', 'Streamlit'],
        '資料庫': ['Mysql', 'MSSQL', 'SQlite', 'MongoDB'],
        '視覺化': ['Tableau', 'Power BI','Excel',''],
        '雲端': ['GCP','Azure','','']
    }
    df = pd.DataFrame(data)

    st.write("技能：")
    st.dataframe(df)
    st.subheader(" ")
    st.subheader(" ")
    
    
    
    # 
    # st.write("學習筆記 : ")
    # st.write("[【Python 視覺化 : Matplotlib (Seaborn)、Plotly】](https://hackmd.io/@workcata/Hk6yp_ay6)")
    # url = "https://hackmd.io/@workcata/Hk6yp_ay6"
    # st.components.v1.iframe(url, height=350) 
    # st.subheader(" ")
    # st.write("[【Apache Spark 巨量資料探勘分析】ft.PySpark](https://hackmd.io/@workcata/rkQXQY2Ja)")
    # url = "https://hackmd.io/@workcata/rkQXQY2Ja"
    # st.components.v1.iframe(url, height=350) 
    # st.subheader(" ")
    # st.write("[【回歸模型評估: MAE、MAPE、SSE、MSE、RMSE、R²】](https://hackmd.io/@workcata/rk6YuVfNA)")
    # url = "https://hackmd.io/@workcata/rk6YuVfNA"
    # st.components.v1.iframe(url, height=350) 
    # st.subheader(" ")
    # st.write("[【 Mysql 系統權限操作】](https://hackmd.io/@workcata/BkWZ13NJ6)")
    # url = "https://hackmd.io/@workcata/BkWZ13NJ6"
    # st.components.v1.iframe(url, height=350) 
    # st.subheader(" ")
    

if __name__ == '__main__':
    main()

