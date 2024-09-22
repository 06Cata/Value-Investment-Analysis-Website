import streamlit as st 
from pages.profolios_personal_subpages.tw_stock_crawler_030_3 import calculate_future_value_annually

def main():
    st.subheader("為什麼要投資?")
    st.write('''很多股票、ETF長期都有年利率4%以上，遠遠高於定存的1~2%。試試看，買零股，複利再投入，一個月只投2000也有差別 !''')

    
    initial_amount = int(st.text_input("初期本金 (元)", value='0'))
    monthly_saving = int(st.text_input("每月投資金額 (元)", value='2000'))
    years = int(st.text_input("投資年數", value='30'))
    annual_interest_rate = float(st.text_input("年利率(%)", value='5'))
            

    if st.button("送出"):
        try:
            df, fig = calculate_future_value_annually(initial_amount, monthly_saving, years, annual_interest_rate)
        except:
            st.error("請確保所有欄位都是有效的數字")
            
        st.dataframe(df) 
        st.plotly_chart(fig) 
    




if __name__ == '__main__':
    main()


 