#%%
# 買賣交易計算機、複利計算機、買賣交易計算機
#%%
import pandas as pd
import math



#%%
# 定期定額複利，年複利

def calculate_future_value_annually(initial_amount, monthly_saving, years, annual_interest_rate):
    
    annual_interest_rate_100 = int(annual_interest_rate)/100
    cumulative_values = []
    cumulative_bank_values = []
    normal_values = []
    future_value = initial_amount
    normal_value = initial_amount
    bank_value = initial_amount
    
    for year in range(years):
        annual_savings = monthly_saving * 12
        future_value += annual_savings
        future_value *= (1 + (annual_interest_rate_100))
        future_value = math.floor(future_value)
        cumulative_values.append(future_value)
        
        annual_savings = monthly_saving * 12
        bank_value += annual_savings
        bank_value *= (1 + (0.02))
        bank_value = math.floor(bank_value)
        cumulative_bank_values.append(bank_value)
        
        normal_value += annual_savings
        normal_value = math.floor(normal_value)
        normal_values.append(normal_value)

    
    years_list = list(range(1, years + 1))
    df = pd.DataFrame({'Year': years_list, '投資複利累積金額': cumulative_values, '定存2%累積金額': cumulative_bank_values,'不投資累積金額': normal_values})

    
    
    # 
    import plotly.graph_objects as go
    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=df['投資複利累積金額'],
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        textposition='top center',
        name='投資複利累積金額'
    ))

    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=df['定存2%累積金額'],
        mode='lines+markers+text',
        line=dict(color='blue', width=2),
        textposition='top center',
        name='定存2%累積金額'
    ))

    fig.add_trace(go.Scatter(
        x=df['Year'],
        y=df['不投資累積金額'],
        mode='lines+markers+text',
        line=dict(color='mediumturquoise', width=2),
        textposition='top center',
        name='不投資累積金額'
    ))


    f_money = df['投資複利累積金額'].iloc[-1]

    fig.update_layout(
        title=f'每年財產累積折線圖<br>\
條件: 本金{initial_amount}元，月存{monthly_saving}元，年利率{annual_interest_rate}% (如果有投資，{years}年後可以到達{f_money}元)',
        xaxis=dict(title='年'),
        yaxis=dict(title=''),
        legend=dict(
            title='',
            x=1.0,
            y=1.4,
            traceorder='normal',
            orientation='v'
        ),
        width=1000,
        height=400,
    )


    # fig.show()
    
    return df, fig




#%%

# 假設我每月投入固定金額 $_，每年帳戶總額*報酬率 %，使用折現率概念，幾年後能到達目標 $?

def calculate_years_to_goal(initial_amount, monthly_saving, annual_interest_rate, goal):
    annual_interest_rate_100 = annual_interest_rate/100
    current_balance = initial_amount
    years = 0
    cumulative_values = []

    while current_balance < goal:
        current_balance += monthly_saving * 12  # 每年投入金額
        current_balance *= (1 + annual_interest_rate_100)
        cumulative_values.append(current_balance)
        years += 1

    df = pd.DataFrame({'Year': range(1, years + 1), '已累積金額': cumulative_values})
    
    return df, years 



# 假設我希望__年後能到達目標__元，每年帳戶總額*報酬率__(%)，每月要投入多少__元?

def calculate_monthly_savings(initial_amount, target_amount, annual_interest_rate, years):
    # 年報酬率 -> 月報酬率
    annual_interest_rate_new = annual_interest_rate/100
    monthly_interest_rate = annual_interest_rate_new / 12

    monthly_savings = (target_amount - initial_amount) / (((1 + monthly_interest_rate) ** (years * 12) - 1) / (monthly_interest_rate))
    
    
    return monthly_savings
    
    
    
    
#%%

# 股票"購買手續費"，無條件進位 (1.425% 券商手續費)
def calculate_buying_fee(buying_stock_price, buying_quantity, discount=None):
    if discount is None:
        discount = 10
    total_buying_stock_price = buying_stock_price * buying_quantity
    buying_fee = (buying_stock_price * buying_quantity) * (1.425/1000) * (discount/10)
    buying_fee = round(buying_fee,2)
    return total_buying_stock_price, buying_fee



# 股票"賣出手續費"，無條件進位 (1.425% 券商手續費 + 0.003 證券交易稅 )
def calculate_selling_fee(selling_stock_price, selling_quantity, discount=None):
    if discount is None:
        discount = 10
    total_selling_stock_price = selling_stock_price * selling_quantity
    selling_fee = ((selling_stock_price * selling_quantity) * (1.425/1000) * (discount/10)) 
    selling_fee = round(selling_fee,2)
    selling_fee_2 = ((selling_stock_price * selling_quantity) * (3/1000))
    return total_selling_stock_price, selling_fee, selling_fee_2


# 計算獲利
def calculate_earning(choice, buy_stock_price, sell_stock_price, quantity, discount=None):
    tax = 0
    if choice == 1:
        tax = 0.1
    elif choice == 2:
        tax = 0.3
        
    if discount is None:
        discount = 10
        
    discount_new = discount/10
    buy_price = round(buy_stock_price * quantity, 2)
    buy_fee = round(buy_stock_price * quantity * (1.425/1000) * discount_new, 2)
    buy = round(buy_price + buy_fee, 2)
    sell_price = round(sell_stock_price * quantity, 2)
    sell_fee = round(sell_stock_price * quantity * (1.425/1000) * discount_new, 2)
    sell_fee_p = round(sell_stock_price * quantity * float(tax/100), 2)
    sell = round(sell_price - sell_fee - sell_fee_p,2)
    
    if discount == 10:
        discount_show = 0
    else: 
        discount_show = discount_new
    
    earning_money = round(sell_price - (buy_price + buy_fee + sell_fee + sell_fee_p),2)
    earning_money_100 = round(((sell - buy) / buy * 100), 2)
    
    if earning_money_100 > 0:
        status = "賺了"
    else:
        status = "賠了"
        
    stock_choice = ""
    if choice == 1:
        stock_choice = "ETF"
    elif choice == 2:
        stock_choice = "股票"
        
    return stock_choice, tax, discount_show, buy_price, buy_fee, buy, sell_price, sell_fee, sell_fee_p, sell, earning_money, earning_money_100, status
    