import streamlit as st 
import pandas as pd 
import streamlit.components.v1 as components

def main():
    st.header("Catalina Kuo")
    st.markdown('''<a href="https://06cata.github.io/Cata_web_WeHelp/">網站</a>、
                <a href="https://hackmd.io/@workcata">學習筆記</a>''', unsafe_allow_html=True)

    st.markdown('''聯絡方式 : <a href="mailto:catalinakuowork@gmail.com">Email</a>、
                <a href="https://www.linkedin.com/in/catalina-k-3a63951a5/">Linkedin</a>、
                <a href="https://github.com/06Cata/">Github</a>''', unsafe_allow_html=True)
    
    st.markdown('''Resume : <a href="https://www.cakeresume.com/s--ef1WormNkeNevqLwaCXYow--/work-cata">PDF履歷</a>''', unsafe_allow_html=True)


    # 
    # st.write("")
    # st.write('''我是一名資料分析師，目前於資訊服務出版業工作，負責資料清整、量化分析、模型維護及視覺化。使用SQL、Python、Tableau，並撰寫商業報告。\

    #          個人因興趣做了價值投資分析網，並定期更新財報於GitHub上。曾擔任西班牙語業務三年，具備數位行銷與開發拉美市場的經驗，轉職後專注於數據分析與機器學習領域的技能提升''')

    # st.write('''我相信有興趣才能走得遠，希望能透過工作加深更多相關技能， 可以透過 Email、Linkedin、Cake 聯絡我😊''')

    # st.subheader(" ")
    
    
    
    
    # # 
    # data = {
    #     'Python': ['Pandas, Numpy', 'Plotly, Matplotlib','Requests, Selenium', 'Streamlit'],
    #     '資料庫': ['Mysql', 'MSSQL', 'SQlite', 'MongoDB'],
    #     '視覺化': ['Tableau', 'Power BI','Excel',''],
    #     '雲端': ['GCP','Azure','','']
    # }
    # df = pd.DataFrame(data)

    # st.write("技能：")
    # st.dataframe(df)
    # st.subheader(" ")
    # st.subheader(" ")
    
    

if __name__ == '__main__':
    main()

