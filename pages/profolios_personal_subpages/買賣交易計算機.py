import streamlit as st 
import math
from pages.profolios_personal_subpages.tw_stock_crawler_030_3 import calculate_earning

def main():
    st.subheader("買賣交易計算機")
    st.write('''購買股票 : 1.425% 券商手續費  
                賣出股票 : 1.425% 券商手續費 + 0.03% 證券交易稅 (ETF 0.01%)''')

    choice = float(st.text_input("ETF:1、股票:2", value='2'))
    buy_stock_price = float(st.text_input("買入金額 (元)", value='10'))
    quantity = float(st.text_input("股數", value='1000'))
    sell_stock_price = float(st.text_input("賣出金額 (元)", value='10'))
    discount = float(st.text_input("券商折扣_(折)，沒有則放置10", value='10'))
            

    if st.button("送出"):
        try:
            stock_choice, tax, discount_show, buy_price, buy_fee, buy, sell_price, sell_fee, sell_fee_p, sell, earning_money, earning_money_100, status = calculate_earning(choice, buy_stock_price, sell_stock_price, quantity, discount)
        except:
            st.error("請確保所有欄位都是有效的數字。")
            
        if earning_money_100 < 0:
            status_color = "green"
        elif earning_money_100 > 0:
            status_color = "red"
        else:
            status_color = "black"
        
        status_text = f"{status} {earning_money_100}%"
        colored_status_text = f"<font color='{status_color}'>{status_text}</font>"

        st.markdown(f'''<h6>{stock_choice}，券商折扣{discount_show}折，證交稅為{tax}%</h6>''', unsafe_allow_html=True)
        st.markdown(f'''<h6>買入股票淨值為 ${buy_price}，買進手續費為 ${buy_fee}，買入所需為 ${buy}</h6>''', unsafe_allow_html=True)
        st.markdown(f'''<h6>賣出股票淨值為 ${sell_price}，賣出手續費為 ${sell_fee}，證交稅為 ${sell_fee_p}，賣出所得為 ${sell}</h6>''', unsafe_allow_html=True)
        st.markdown(f'''<h6>利潤(虧損) ${earning_money}，{colored_status_text}</h6>''', unsafe_allow_html=True)


        
        
if __name__ == '__main__':
    main()
 