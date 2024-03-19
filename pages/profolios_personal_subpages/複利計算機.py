import streamlit as st 
from pages.profolios_personal_subpages.tw_stock_crawler_030_3 import calculate_years_to_goal,calculate_monthly_savings
    

def main():
    
    st.subheader("複利計算機")
    st.markdown('''##### 假設我每月投入固定金額__元，每年帳戶總額*報酬率__(%)，幾年後能到達目標__元?''')

    
    initial_amount = int(st.text_input("初期本金 (元) - 1", value='0'))
    monthly_saving = int(st.text_input("每月投資金額 (元) - 1", value='10000'))
    annual_interest_rate = float(st.text_input("年利率(%) - 1", value='5'))
    goal = int(st.text_input("目標金額 - 1", value='10000000'))
            

    if st.button("送出 - 1"):
        try:
            df, years = calculate_years_to_goal(initial_amount, monthly_saving, annual_interest_rate, goal)
        except:
            st.error("請確保所有欄位都是有效的數字。")
            
        st.markdown(f'''<h6>需要 {years} 年能累積到 {goal} 元的目標</h6>''', unsafe_allow_html=True)
        st.dataframe(df) 
        
        
        
    st.subheader("")
    st.subheader("")
    


    st.markdown('''##### 假設我希望__年後能到達目標__元，每年帳戶總額*報酬率__(%)，每月要投入多少__元?''')

    
    initial_amount = int(st.text_input("初期本金 (元) - 2", value='0'))
    target_amount = int(st.text_input("目標金額 (元) - 2", value='10000000'))
    annual_interest_rate = float(st.text_input("年利率(%) - 2", value='5'))
    years = int(st.text_input("投資年數 - 2", value='30'))
            

    if st.button("送出 - 2"):
        try:
            monthly_savings = calculate_monthly_savings(initial_amount, target_amount, annual_interest_rate, years)
        except:
            st.error("請確保所有欄位都是有效的數字。")
           
        st.markdown(f'''<h6>每月需要存入 {monthly_savings:.2f} 元</h6>''', unsafe_allow_html=True)



if __name__ == '__main__':
    main()


 