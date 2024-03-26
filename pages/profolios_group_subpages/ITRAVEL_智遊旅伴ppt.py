import streamlit as st

def main():
    st.subheader("ITRAVEL 智遊旅伴")
    
    st.write('''轉職班中，和組員做過的專題。使用爬蟲、套gcp api抓資料、清洗，從台灣景點、餐廳、住宿資料提取tag，配合最後網頁使用者偏好使用，
             為了不要讓行程點太遠，用了sklearn.cluster DBSCAN ，把景點依照距離分群。最後由前端組員，串接Flask，傳入使用者偏好的JSON檔，發出API請求，推送旅遊行程呈現在網頁

            ''')
    st.write('')
    
    st.write('點選"投影播放"即可放大並開始')
    google_slides_url2 = "https://docs.google.com/presentation/d/1fbZCnZoVFKst7yvkhn5IEyALPHPj3XhuYwc9UQkTRf0/edit?usp=sharing"
    
    # 使用 iframe 嵌入 Google Slides
    st.markdown(f'<iframe src="{google_slides_url2}" width="800" height="600"></iframe>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()