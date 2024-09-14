import streamlit as st 
from urllib.parse import quote
from requests.exceptions import HTTPError
import random

from pages.profolios_personal_subpages.tw_stock_crawler_030 import get_tables_of_dbtablename, get_stock_code_industry, \
plotly_ocf_icf_fcf, plotly_ocf_ni, plotly_net_free_cash_flow, plotly_business, plotly_shareholders_equity, \
plotly_cfr_3, plotly_cashncash_equivalents,\
plotly_days_sales_outstanding, plotly_fake, plotly_fixed_asset_turnover_ratio,\
plotly_roe, plotly_roa, plotly_eps, read__monthly_report_from_sqlite, plotly_3_rate, plotly_operating_margin_of_safety, plotly_year_revenue,\
plotly_4q_revenue_growth_rate, plotly_non_operating_earnings, plotly_tax,\
plotly_debt_to_asset_ratio,  plotly_ratio_of_liabilities_to_assets, plotly_total_debt_equity_ratio,\
plotly_debt_paying_ability


def main():
    st.subheader("基本面: 財報分析")
    st.write('''巴菲特曾說 "You make your money when you buy, not when you sell."，買企業，不是買股票，投資者應該專注於評估企業的基本價值，並長期持有，勝率更大  
             ''')  

    st.write('''資料來源: "公開資訊觀測站"，讀取資料庫 [(1)](https://github.com/06Cata/tw_financial_reports1)、[(2)](https://github.com/06Cata/tw_financial_reports2)、\
            [(3)](https://github.com/06Cata/tw_financial_reports3)。以上觀點僅供參考，並不構成任何交易建議或推薦。數值太接近，折線圖有可能重疊，可以分別點擊查看''')

    stock_code = st.text_input("請輸入股票代碼：", value='2885')

    if st.button("查詢"):
        loading_messages = [
            "這不是煮泡麵，需要一點時間的",
            "放輕鬆，不是等開會，是等待你的資產翻倍~",
            "抓五年資料，不是瞬間魔法，是耐力的魔法！",
            "等一下，這比你對刮刮樂快",
            "沒耐心就像打開冰箱找東西，找不到的時候只會更生氣",
            "等待中...這不是等紅燈，是等待財富的綠燈",
            "就像等待手搖飲料一樣，加點料就能更好喝，我比較喜歡奶蓋",
            "放輕鬆，這不是等考績，是等待你的投資籌碼變成黃金"
        ]

        loading_message = random.choice(loading_messages)
        st.text(loading_message)
         
        
        # stock_code, stock_name, stock_industry, related_data = get_stock_code_industry(stock_code)
        try:
            stock_code, stock_name, stock_size, stock_industry, related_data = get_stock_code_industry(stock_code)
            dfs, suss_tables = get_tables_of_dbtablename(int(stock_code))
        except Exception as e:
            st.write('很抱歉數據庫沒有這隻股票、連不上數據庫，或出現其他錯誤')
            # st.write(f'錯誤訊息: {str(e)}')
            return

                
        related_datas = []
        for r in related_data:
            related_datas.append(r)
            
        # 創建可擴展區域
        with st.expander(f"選擇的是 {stock_code} {stock_name} ，{stock_industry}  ({stock_size})，同產業的有"):
            st.write(related_datas )


        # dfs, suss_tables = get_tables_of_dbtablename(int(stock_code))
        # 創建可擴展區域_2
        with st.expander(f"用電腦更好看，已成功抓取到的資料"):
            if not dfs and not suss_tables:
                st.write('很抱歉，沒有這檔股票的資料')
            else:
                st.write(suss_tables)
        

        # 保存查詢的狀態
        st.session_state.stock_data = {
            'stock_code': stock_code,
            'dfs': dfs,
            'suss_tables': suss_tables
        }
        
        
        ##########################
        # 創建頁面上方的選項
        # if st.button("跳到現金流量"):
        #     st.markdown('[跳到現金流量](#現金流量)', unsafe_allow_html=True)

        # # 創建頁面上方的選項
        # # 在按下「跳到現金流量」按鈕時，設定 session_state.scroll_to_cash_flow
        # if st.button("跳到現金流量"):
        #     st.session_state.scroll_to_cash_flow = True

        # # 在渲染時，檢查是否需要滾動到現金流量部分
        # if getattr(st.session_state, 'scroll_to_cash_flow', False):
        #     st.markdown("""<script>window.location.href='#現金流量'</script>""", unsafe_allow_html=True)
        #     st.session_state.scroll_to_cash_flow = False

        # if st.button("跳到現金流量"):
        #     st.markdown('<div id="scroll_target"></div>', unsafe_allow_html=True)
        #     st.markdown("""<script>window.location.href='#scroll_target';</script>""", unsafe_allow_html=True)


        
        ####################################
        st.subheader("")
        # st.markdown('<div id="scroll_target"></div><a name="現金流量"></a>', unsafe_allow_html=True)
        st.subheader("【現金流量】")
        
        
        try:
            # 現金流量表 (比氣長，有三長) 
            # 001 包成def
            # ocf icf fcf
            # 銀行業ok不用調
            st.markdown("#### ★ 現金流量，現金越多氣越長，更能應對可能的不確定性")
            fig, fig2, fig3 = plotly_ocf_icf_fcf(dfs)
            st.write('''
                現金流量體現企業實際的資金，從中觀察營運方向  
                營業活動現金流: 正的，賺錢；負的，賠錢  
                投資活動現金流: 正的，變賣資產；負的，投資自己，持續擴張  
                融資活動現金流: 正的，借錢；負的，還錢、減資...
                ''')
            st.plotly_chart(fig) 
            st.plotly_chart(fig2)
            st.plotly_chart(fig3)
        
        except:
            pass
 
 

        try:
            # 001-2 包成def
            # ocf ni 比較 
            # 銀行業不看
            if stock_industry == "產業別：金融保險業（其中金控公司係控股公司，其申報之「營業收入」係認列所有子公司損益之合計數）" or stock_industry == "產業別：金融業":
                pass
            else:
                st.markdown("#### ★ 營業活動現金流量OCF比較")
                fig, fig2, fig3 = plotly_ocf_ni(dfs)
                st.write('''
                    OCF是否>0，營業活動現金流持續為正，表示企業在營運中持續產生現金，穩定增長最好  
                    OCF是否>流動負債，營業活動現金流足以支付流動負債(不怕被催收帳款)   
                    OCF是否>固定資產，營業活動現金流足夠支付固定資產的投資，表示企業有能力自主擴張，不必過度依賴外部資金(賺的錢可以自給自足，投資自己)
                    ''')
                st.plotly_chart(fig)
                st.write('''
                    營業活動現金流與淨利走勢要相同，表示企業的淨利來自實際的現金收入  
                    營業活動高、淨利低時，公司可能有高營運費用、投資活動、折舊攤銷、應收帳款、存貨增加  
                    營業活動低、淨利高時，公司可能推遲應付帳款、有非現金性質的收入  
                    公式:  
                    獲利含金量 = 營業活動現金流 / 淨利，公司實際現金流入相對於淨利潤的比例，高於100%表示企業能夠將淨利轉化為現金
                    ''')
                st.plotly_chart(fig2)
                st.plotly_chart(fig3)
        except:
            pass
        
        
        
        try:
            # 001-3 包成def
            # 淨現金流量、自由現金流量
            # 銀行業ok不用調
            st.markdown("#### ★ 淨現金流量、自由現金流量")
            fig, fig2, positive_count2  = plotly_net_free_cash_flow(dfs)
            st.write('''
                淨現金流量: 一間公司錢是流出去多or流進來多  
                自由現金流量: 公司可以自由運用的現金  
                自由現金流量高，表示公司在資本支出(擴張或投資等)後，仍有較多現金可供運用，提供了彈性   
                自由現金流量低，表示公司可能有相當多的資本支出(擴張或投資等，搭配現金、不動產、廠房及設備查看)  
                公式:   
                    淨現金流量 = 營業活動現金流 + 投資活動現金流 + 籌資活動現金流  
                    自由現金流量 = 營業活動現金流 + 投資活動現金流
                ''') 
            if positive_count2 < 5:
                st.write(f'*近八季中自由現金流量，有{positive_count2}季是正的，稍低，請與同業比較')
            else:
                st.write(f'*近八季中自由現金流量，有{positive_count2}季是正的，不錯，請與同業比較可以與同業比較')
            st.plotly_chart(fig)
            st.plotly_chart(fig2)
        except:
            pass



        try:
            # 002-2 包成def
            # 現金與約當現金(流動資產)、不動產廠房及設備(非流動資產)、流動負債合計、非流動負債合計、長期資金(非流動負債)趨勢
            # 銀行業不看
            if stock_industry == "產業別：金融保險業（其中金控公司係控股公司，其申報之「營業收入」係認列所有子公司損益之合計數）" or stock_industry == "產業別：金融業":
                pass
            else:
                st.markdown("#### ★ 與下方一起查看")
                fig, fig2 = plotly_business(dfs)
                st.write('''
                    現金、不動產、廠房及設備，與後面"資本公積"一起看  
                    觀察是否有股本溢價(現金增、資本公積增)、資產重估(現金增減、資本公積增減)、  
                    處分固定資產(現金增、不動產減、資本公積增)  
                    觀察現金、不動產、廠房及設備、長期借款，是否大幅增加，公司是否借錢來擴張業務
                            ''')
                st.plotly_chart(fig) 
                st.plotly_chart(fig2)
        except:
            pass
        
        
        
        try:
            # 004 包成def
            # 股東權益: 股本、保留盈餘、資本公積
            # 銀行業ok 
            fig, fig2 = plotly_shareholders_equity(dfs)
            st.write('''
                股本: 公司發行的所有普通股的總額  
                保留盈餘: 從淨利中保留下來的，顯示公司的獲利能力  
                資本公積: 企業收到的資金超過股票面額，代表額外的資本增值，顯示市場上的價值和投資者的信心  
                如果有企業用公積配股，要注意是否因為淨利不理想，為了維持股價而進行公積配股
                        ''')
            st.plotly_chart(fig) 
            st.plotly_chart(fig2)
        except:
            pass
        
        
        
        try:
            # 002~004 包成def
            # 現金流量關鍵
            # 銀行業不看
            if stock_industry == "產業別：金融保險業（其中金控公司係控股公司，其申報之「營業收入」係認列所有子公司損益之合計數）" or stock_industry == "產業別：金融業":
                pass
            else:
                st.markdown("#### ★ 現金流量比率")
                fig, fig2, avg_price_to_cash_flow_ratio = plotly_cfr_3(dfs)
                st.write('''
                    現金流量比率，營業活動的現金流入，是否足以因應積欠的流動負債，  
                    比率越高，短期償債能力越好，高於100%，公司的現金流量能夠覆蓋全部的流動負債  
                    公式:  
                        營業活動淨現金流量 / 流動負債 *100 (%)
                            ''')
                st.plotly_chart(fig) 
                if avg_price_to_cash_flow_ratio < 100:
                    st.write(f'近四季平均現金流量比率為{avg_price_to_cash_flow_ratio}%，低於100%，請與同業比較')
                else:
                    st.write(f'近四季平均現金流量比率為{avg_price_to_cash_flow_ratio}%，不錯，可以與同業比較')
                st.plotly_chart(fig2)
        except:
            pass



        try:
            # 005 包成def 
            # 現金佔比趨勢
            # 銀行業ok 
            st.markdown("#### ★ 現金佔比趨勢")
            fig, fig2, avg_cashncash_equivalents = plotly_cashncash_equivalents(dfs)
            st.write('''
                公司在短期內擁有多少現金資產，與同業比，最好要有10~25%，資本密集行業要更高，金融業會較低  
                公式:  
                    現金與約當現金 / 資產總額 *100 (%)
                        ''')
            st.plotly_chart(fig)
            if avg_cashncash_equivalents < 10:
                st.write(f'近四季平均現金佔比為{avg_cashncash_equivalents}%，低於10%，請與同業比較')
            elif avg_cashncash_equivalents <= 25:
                st.write(f'近四季平均現金佔比為{avg_cashncash_equivalents}%，合理範圍內，請與同業比較')
            else:
                st.write(f'近四季平均現金佔比為{avg_cashncash_equivalents}%，很不錯，可以與同業比較')

            st.plotly_chart(fig2)

        except:
            pass
        
        ##########################
        st.subheader("")
        # st.markdown("<a name='【經營能力】'></a>", unsafe_allow_html=True)
        st.subheader("【經營能力】")
        

        
        try:
            # 007 包成def
            # 應收帳款、存貨周轉、應付帳款、總資產周轉、現金佔比
            # 銀行業不看
            if stock_industry == "產業別：金融保險業（其中金控公司係控股公司，其申報之「營業收入」係認列所有子公司損益之合計數）" or stock_industry == "產業別：金融業":
                pass
            else:
                st.markdown("#### ★ 總資產、存貨、應收、應付帳款週轉率")
                fig, fig2, fig22, fig3, fig4 = plotly_days_sales_outstanding(dfs)
                st.write('''
                    總資產周轉>1次，才有賺；若<1，多數是資本密集、特殊行業，半導體、精品、網路、金融...  
                    要注意現金佔比是否足夠，最好10~25%，或更多，或應收帳款天數較短(<15天)、存貨天數較短(<60天)  
                    公式:  
                        總資產週轉 = 營業收入 / 平均資產總額   
                        存貨週轉率 = 營業成本 / 平均存貨  
                        應收帳款週轉率 = 營業收入 / 平均應收帳款淨額  
                        應付帳款週轉率 = 營業成本 / 平均應付帳款淨額               
                            ''')
                st.plotly_chart(fig) 
                st.write('''
                    存貨周轉>6次/年，就很不錯  
                    應收帳款<15天為收現金行業、B2B通常為60~90天，與同業比較 
                            ''')
                st.plotly_chart(fig2)
                st.plotly_chart(fig22) 
                st.write('''
                    應付帳款天數要平穩或上升，付越少次越好  
                    存貨天數要平穩或下降，在庫天數越少越好  
                    應收帳款天數要平穩或下降，收越多次越好  
                            ''')
                st.write('''
                    做生意完整週期>200天，現金要足夠，毛利要高  
                    公式:  
                        做生意完整週期 = 存貨天數+應收帳款天數
                            ''')
                st.plotly_chart(fig3)
                st.write('''
                    現金週轉天數，要平穩或緩慢下降，現金壓力變小  
                    公式:  
                        現金週轉天數 = 存貨天數+應收帳款天數-應付帳款天數
                            ''')
                st.plotly_chart(fig4)
        except:
            pass
 
        
        
        try:
            # 007-2 包成def
            # (若是有假公司財報，觀察應收帳款天數、應收帳款佔總資產比率、存貨天數、存貨佔總資產比率，是否急遽增加
            # 營業收入、淨利成長，但OCF一直收不到現金，現金與約當現金沒成長)
            # 銀行業不看
            if stock_industry == "產業別：金融保險業（其中金控公司係控股公司，其申報之「營業收入」係認列所有子公司損益之合計數）" or stock_industry == "產業別：金融業":
                pass
            else:
                st.markdown("#### ★ 假設有間假公司財報")
                fig, fig2 = plotly_fake(dfs)
                st.write('''
                    觀察應收帳款天數、應收帳款佔總資產比率、存貨天數、存貨佔總資產比率，是否急遽增加；  
                    營業收入、淨利成長，但OCF一直收不到現金，現金與約當現金沒成長
                            ''')
                st.plotly_chart(fig)
                st.plotly_chart(fig2) 
        except:
            pass
        
        
        
        try:
            # 008 包成def
            # 不動產、廠房及設備週轉率 Fixed Asset Turnover Ratio
            # 銀行業ok (改成利息收入/平均不動產、廠房及設備淨額)、沒有不動產就不顯示
            
            if stock_industry == "產業別：金融保險業（其中金控公司係控股公司，其申報之「營業收入」係認列所有子公司損益之合計數）" or stock_industry == "產業別：金融業":
                st.markdown("#### ★ 利息收入/平均不動產、廠房及設備週轉率")
                try:
                    fig01, fig02 = plotly_fixed_asset_turnover_ratio(dfs)
                    st.write('''
                    不動產、廠房及設備週轉率越高，公司更能有效地利用設備來產生淨收益，但也可能代表公司機台，沒跟上業務的迅速成長  
                    緩慢上升，表示不動產、廠房及設備利用效率上升，產品單位成本下降，獲利能力提升  
                    PS 記得看產業特性，電子支付類的公司數值會偏低  
                    公式:  
                        利息收入 / 平均不動產、廠房及設備
                            ''')
                    st.plotly_chart(fig01)
                    st.plotly_chart(fig02) 
                except:
                    pass
                
            else:
                st.markdown("#### ★ 不動產、廠房及設備週轉率")
                fig, fig2 = plotly_fixed_asset_turnover_ratio(dfs)
                st.write('''
                    不動產、廠房及設備週轉率越高，公司更能有效地利用設備來產生淨收益，但也可能代表公司機台，沒跟上業務的迅速成長  
                    緩慢上升，表示不動產、廠房及設備利用效率上升，產品單位成本下降，獲利能力提升  
                    *記得看產業特性，電子支付類的公司數值會偏低  
                    公式: 營業收入 / 平均不動產、廠房及設備
                            ''')
                st.plotly_chart(fig)
                st.plotly_chart(fig2) 
        except:
            pass
        
        
        ##########################
        st.subheader("")
        # st.markdown("<a name='【獲利能力】'></a>", unsafe_allow_html=True)
        st.subheader("【獲利能力】")
  


        try:
            # 005 包成def
            # ROE
            # 銀行業ok
            st.markdown("#### ★ ROE 權益報酬率")
            fig, fig2, avg_roe = plotly_roe(dfs)
            st.write('''  
                ROE權益報酬率越高，代表公司越能妥善運用資源，為股東賺回的獲利越高  
                與同業比，通常 ROE > 10-15％ (三到五年平均、連續五年)作為選股條件      
                *ROE高，記得要觀察淨利和財務槓桿，有可能是淨利高，或是財務槓桿高、股本小  
                公式:  
                    稅後淨利 / 平均權益總額 *100 (%)            
                        ''')
            st.plotly_chart(fig)
            if avg_roe > 15:
                st.write(f'近四季累計ROE為：{avg_roe}%，很不錯，可以與同業比較')
            elif avg_roe > 10 and avg_roe < 15 :
                st.write(f'近四季累計ROE為：{avg_roe}%，在合理範圍內，可以與同業比較')
            else:
                st.write(f'近四季累計ROE為：{avg_roe}%，偏低，請與同業比較')
            st.plotly_chart(fig2)
        except:
            pass
        
        
        
        try:
            # 006 包成def
            # ROA
            # 銀行業ok
            st.markdown("#### ★ ROA 資產報酬率")
            fig, fig2, avg_roa = plotly_roa(dfs)
            st.write('''
                ROA資產報酬率越高，代表整體資產帶回的獲利越高，負債比率較高的產業，金融、保險業常用ROA  
                與同業比，通常 ROA > 6-7％ (三到五年平均、連續五年等) 作為選股條件  
                *如果ROA很低，但ROE很高，公司獲利可能大部分來自高財務槓桿，風險也較高  
                公式:  
                    稅後淨利 / 平均資產總額  *100 (%) (未含利息及扣稅)
                        ''')
            st.plotly_chart(fig)
            if avg_roa > 7:
                st.write(f'近四季累計ROA為：{avg_roa}%，很不錯，可以與同業比較')
            elif avg_roa > 5 and avg_roa < 7 :
                st.write(f'近四季累計ROA為：{avg_roa}%，在合理範圍內，可以與同業比較')
            else:
                st.write(f'近四季累計ROA為：{avg_roa}%，偏低，請與同業比較')
            st.plotly_chart(fig2)
        except:
            pass    
        
        
        try:
            # 007-2 包成def
            # 月報看每月營收
            # 銀行業ok
            st.markdown("#### ★ 月營收比較")
            fig= read__monthly_report_from_sqlite(stock_code)
            st.write('''
                季報還未出來時，可以觀察每月營收、與去年當月營收比較，並參考EPS  
                假設有公司月營收、EPS都低，但營業活動現金流高，可能營業成本降低、減少資本支出、加快應收帳款週轉...  
                *直接拖拉可以放大，右上角🏛️可以重置
                        ''')
            st.plotly_chart(fig)
        except:
            pass
        
        
        
        
        try:
            # 007 包成def
            # eps
            # 銀行業ok
            st.markdown("#### ★ EPS")
            fig, fig2, fig3 = plotly_eps(dfs)
            st.write('''
                每股盈餘（Earnings Per Share）  
                是一個衡量公司盈利能力的財務指標，用於評估公司在每股普通股上實現的盈利情況  
                公式:  
                    損益表中的「基本每股盈餘」，Q4單季為全年度-(Q1+Q2+Q3)
                        ''')
            st.plotly_chart(fig)
            st.plotly_chart(fig2)
            st.plotly_chart(fig3)
        except:
            pass   
        
        
        
        
        try:
            # 綜合損益表 (獲利能力)
            # 001~004 包成def
            # 財報三率
            # 銀行業ok
            st.markdown("#### ★ 財報三率: 毛利率、營益率、淨利率")
            fig, fig2, fig3 = plotly_3_rate(dfs)
            st.write('''
                營益率 > 淨利率，公司在營業活動中有較高的效率，有效地管理營運成本和營業費用  
                營益率 < 淨利率，公司在營業支出上有較多的開支  
                費用率與同業比，越低通常規模越大  
                費用率與同業比較，品牌商通常會>20%，實體通路因為要員工，通常會>網路通路  
                公式:  
                    毛利率 = (營業收入-營業成本) / 營業收入 *100 (%)  
                    營益率 = 營業利益 / 營業收入 *100 (%)  
                    費用率 = 毛利率 - 營益率  
                    淨利率 = 稅後淨利 / 營業收入 *100 (%)
                        ''')
            st.plotly_chart(fig)
            st.plotly_chart(fig2)
            st.plotly_chart(fig3)
        except:
            pass
        
        
        
        try:
            # 004-2 包成def
            # 經營安全邊際 (越高，抵抗景氣波動能力越大)
            # 銀行業不看
            if stock_industry == "產業別：金融保險業（其中金控公司係控股公司，其申報之「營業收入」係認列所有子公司損益之合計數）" or stock_industry == "產業別：金融業":
                pass
            else:
                st.markdown("#### ★ 經營安全邊際")
                fig, fig2, avg_operating_margin_of_safety = plotly_operating_margin_of_safety(dfs)
                st.write('''
                    公司在營運方面的穩定性和抵抗景氣波動的能力，>60%很不錯，數值越高，抵抗景氣波動能力越大  
                    公式:  
                        營業利益 / 營業毛利 *100 (%)
                            ''')
                st.plotly_chart(fig)
                if avg_operating_margin_of_safety < 50:
                    st.write(f'近四季平均經營安全邊際為{avg_operating_margin_of_safety}%，偏低，請與同業比較')
                else:
                    st.write(f'近四季平均經營安全邊際為{avg_operating_margin_of_safety}%，不錯，可以與同業比較')

                st.plotly_chart(fig2)
        except:
            pass
        
        
        
        try:
            # 005包成def
            # 營收、盈餘、營益率比較
            # 銀行業ok 
            st.markdown("#### ★ 營收、盈餘、營益率比較")
            fig, fig2 = plotly_year_revenue(dfs)
            st.write('''
                當營收成長時，盈餘、營益率同步成長，才是靠本業賺錢的公司，用"營益率%"觀察本業盈餘變化  
                        ''')
            st.plotly_chart(fig)
            st.plotly_chart(fig2)
        except:
            pass   
    
        
        
        try:
            # 005-2 包成def
            # 營收成長率 Revenue Growth Rate # 季
            # 銀行業ok 
            st.markdown("#### ★ 營收成長率比較")
            try:
                fig, fig2, fig33 = plotly_4q_revenue_growth_rate(dfs)
            except:
                fig, fig2 = plotly_4q_revenue_growth_rate(dfs)

            st.plotly_chart(fig)
            st.plotly_chart(fig2)
            try:
                st.plotly_chart(fig33)
            except:
                pass
        except:
            pass
    

        
        
        try:
            # 006 包成def
            # 業內、業外
            # 銀行業不看
            if stock_industry == "產業別：金融保險業（其中金控公司係控股公司，其申報之「營業收入」係認列所有子公司損益之合計數）" or stock_industry == "產業別：金融業":
                pass
            else:
                st.markdown("#### ★ 業內、業外佔比、業外貢獻比")
                st.write('''
                公式:  
                    業內 = 營業利益 / (營業利益+營業外收入及支出)  
                    業外 = 營業外收入及支出 / (營業利益+營業外收入及支出)  
                    業外貢獻比，業外收入對總獲利的貢獻比例 = 稅前淨利 / 營業利益
                        ''')
                fig, fig2 = plotly_non_operating_earnings(dfs)
                st.plotly_chart(fig)
                st.plotly_chart(fig2)
        except:
            pass    
            
        
        
        try:
            # 010 包成def
            # 賦稅優勢
            # 銀行業ok
            st.markdown("#### ★ 賦稅優勢")
            fig, fig2 = plotly_tax(dfs)
            st.write('''
                與同業比，越高越好，表示公司有較好的賦稅優勢，能夠有效地降低應繳納的所得稅，提高稅後淨利  
                公式:  
                    稅後淨利 / 稅前淨利
                        ''')
            st.plotly_chart(fig)
            st.plotly_chart(fig2)
        except:
            pass
        
        
        
        ##########################
        st.subheader("")
        # st.markdown("<a name='【財務結構】'></a>", unsafe_allow_html=True)
        st.subheader("【財務結構】")
        
        
        try:
            # 001 包成def
            # 資產負債比率 Debt to Asset Ratio
            # 銀行業ok
            st.markdown("#### ★ 資產負債比率")
            fig, fig2, avg_debt_to_asset_ratio = plotly_debt_to_asset_ratio(dfs)
            st.write('''
                負債比率越低，代表股東權益較高，股東對公司越有信心，公司的風險就越小  
                負債比率越高，代表公司使用更多的債務資金，可能增加了財務風險，但也可能提高了潛在的收益  
                與同業比，通常不高於50%~60% (銀行保險壽險、營建業會較高)  
                公式:  
                    負債總額 / 資產總額 *100 (%)
                        ''')
            st.plotly_chart(fig)
            if avg_debt_to_asset_ratio > 60:
                st.write(f'近四季平均資產負債比為：{avg_debt_to_asset_ratio}%，偏高，請與同業比較')
            elif avg_debt_to_asset_ratio > 40 and avg_debt_to_asset_ratio < 60 :
                st.write(f'近四季平均資產負債比為：{avg_debt_to_asset_ratio}%，在合理範圍內，可以與同業比較')
            else:
                st.write(f'近四季平均資產負債比為：{avg_debt_to_asset_ratio}%，偏低，債務比率控管得當，可以與同業比較')
            st.plotly_chart(fig2)
        except:
            pass
        
        
        
        try:
            # 002 包成def
            # 長期資金佔不動產、廠房及設備比 Ratio of liabilities to assets
            # 銀行業不看
            if stock_industry == "產業別：金融保險業（其中金控公司係控股公司，其申報之「營業收入」係認列所有子公司損益之合計數）" or stock_industry == "產業別：金融業":
                pass
            else:
                st.markdown("#### ★ 長期資金佔不動產、廠房及設備比")
                fig, fig2, avg_ratio_of_liabilities_to_assets = plotly_ratio_of_liabilities_to_assets(dfs)
                st.write('''
                    長期資金佔固定資產比率>1 ，用長期資金來買不動產、廠房及設備，相當安全  
                    長期資金佔固定資產比率<1，買不動產、廠房及設備的錢從短期資金支付，數值過低可能會導致營運風險   
                    公式:  
                        (權益總額 + 非流動負債) / 不動產、廠房及設備
                            ''')
                st.plotly_chart(fig)
                if avg_ratio_of_liabilities_to_assets > 1:
                    st.write(f'近四季平均長期資金佔不動產、廠房及設備比率為：{avg_ratio_of_liabilities_to_assets}倍，用長期資金來買固定資產，相當安全，可以與同業比較')
                else:
                    st.write(f'近四季平均長期資金佔不動產、廠房及設備比率為：{avg_ratio_of_liabilities_to_assets}倍，偏低，用短期資金來買固定資產，可以會導致營運風險，請與同業比較')
                st.plotly_chart(fig2)      
        except:
            pass        
            
        
        
        try:
            # 003 包成def
            # 總負債/股東權益比 Total Debt/Equity Ratio、財務槓桿
            # 銀行業ok 
            st.markdown("#### ★ 總負債/股東權益比")
            fig, fig2, avg_total_debt_equity_ratio = plotly_total_debt_equity_ratio(dfs)
            st.write('''
                數字越小，表示公司相對擁有較高的資本自足率，自有資金多  
                數字越大，可能公司正在成長，但相對地使用了一定程度的財務槓桿  
                公式:  
                    (負債總額 + 權益總額) / 權益總額 
                        ''')
            st.plotly_chart(fig)
            if avg_total_debt_equity_ratio > 3:
                st.write(f'近四季平均財務槓桿為：{avg_total_debt_equity_ratio}倍，偏高，請與同業比較')
            else:
                st.write(f'近四季平均財務槓桿為：{avg_total_debt_equity_ratio}倍，在合理範圍內，可以與同業比較')
            st.plotly_chart(fig2)
        except:
            pass            
                    
                    
                
        ##########################
        st.subheader("")
        # st.markdown("<a name='【償債能力】'></a>", unsafe_allow_html=True)
        
        try:
            # 009 包成def
            # 償債能力 debt-paying ability: 流動、速動
            # 銀行業不看
            if stock_industry == "產業別：金融保險業（其中金控公司係控股公司，其申報之「營業收入」係認列所有子公司損益之合計數）" or stock_industry == "產業別：金融業":
                pass
            else:
                st.subheader("【償債能力】")
                st.markdown("#### ★ 流動、速動比率")
                fig, fig2, average_current_ratio, average_quick_ratio  = plotly_debt_paying_ability(dfs)
                
                st.write('''
                    流動比率、速動比率，輕資產行業會偏高，重資產行業會偏低  
                    流動比率: 公司每1元的流動負債，可以用多少元的流動資產來還債?  
                    (低標為1，與同業比，通常要 1.5-2.5)  
                    速動比率: 扣除存貨和預付費用，公司每1元的流動負債，可以用多少元的流動資產來還債?  
                    (低標為1，與同業比，通常要 1-1.5)  
                    若是速動比率過低，現金與約當現金最好有10%以上、應收帳款天數<15天、總資產週轉率>1  
                    公式:  
                        流動比率 = 流動資產 / 流動負債)   
                        速動比率 = (流動資產-存貨-預付款項) / 流動負債
                            ''')
                st.plotly_chart(fig)
                if average_current_ratio < 1:
                    st.write(f'近四季平均流動比為：{average_current_ratio}，低於1，請與同業比較')
                elif average_current_ratio > 1 and average_current_ratio < 1.5 :
                    st.write(f'近四季平均流動比為：{average_current_ratio}，微高於低標，請與同業比較')
                elif average_current_ratio > 1.5 and average_current_ratio < 2 :
                    st.write(f'近四季平均流動比為：{average_current_ratio}，及格，可以與同業比較') 
                else:
                    st.write(f'近四季平均流動比為：{average_current_ratio}，很不錯，可以與同業比較')
                    

                if average_quick_ratio < 1:
                    st.write(f'近四季平均速動比為：{average_quick_ratio}，低於1，請與同業比較')
                elif average_quick_ratio > 1 and average_quick_ratio < 1.4 :
                    st.write(f'近四季平均速動比為：{average_quick_ratio}，及格，可以與同業比較') 
                else:
                    st.write(f'近四季平均速動比為：{average_quick_ratio}，很不錯，可以與同業比較')
                st.plotly_chart(fig2)
        except:
            pass
            
            
            
        ##########################
        st.write("")
        st.write("")
        st.write("")
        # HTML和CSS置中樣式
        st.markdown("""
            <div style="text-align: center; margin-top: 50px;">
                <p>以上觀點僅供參考，並不構成任何交易建議或推薦</p>
            </div>
        """, unsafe_allow_html=True)
        
        
        
        
        
        
        
if __name__ == '__main__':
    main()
 