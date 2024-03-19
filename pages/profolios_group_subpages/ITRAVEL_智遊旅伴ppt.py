import streamlit as st

def main():
    st.subheader("ITRAVEL 智遊旅伴")
    st.write('點選"投影播放"即可放大並開始')
    
    google_slides_url2 = "https://docs.google.com/presentation/d/1fbZCnZoVFKst7yvkhn5IEyALPHPj3XhuYwc9UQkTRf0/edit?usp=sharing"
    
    # 使用 iframe 嵌入 Google Slides
    st.markdown(f'<iframe src="{google_slides_url2}" width="800" height="600"></iframe>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()