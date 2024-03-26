import streamlit as st

def main():
    st.subheader("各縣市ESG公開資訊整合平臺")
    st.write('''轉職班中，和組員做過的專題。使用ELK平臺，爬蟲、公開資訊平台 API抓取需要資料、設定排程，Logstash整理、導入ESG相關資訊平台資料，Kibana 整理並繪製出所需畫面。最後由前端組員，使用Angular、鑲嵌iFrame、串接API至前端
            ''')
    st.write('')
    
    st.write('點選"投影播放"即可放大並開始')
    google_slides_url = "https://docs.google.com/presentation/d/16N8TuPlKy23CEiewDIMT6lhfBTDcGFU1kj9tVgXoaZo/edit?usp=sharing"
    
    # 使用 iframe 嵌入 Google Slides
    st.markdown(f'<iframe src="{google_slides_url}" width="800" height="600"></iframe>', unsafe_allow_html=True)
    st.write("")


if __name__ == '__main__':
    main()