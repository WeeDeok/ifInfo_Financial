from flask import Flask, send_file, render_template, make_response
from io import BytesIO

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#plt.switch_backend('TkAgg')
from functools import wraps, update_wrapper
from datetime import datetime
from IPython.display import HTML


app = Flask(__name__)

prjRoot = os.getcwd()
df = pd.read_excel(prjRoot + "/sample.xlsx")
plt.rc('font', family='Malgun Gothic')

# 캐시제거
def nocache(view):
  @wraps(view)
  def no_cache(*args, **kwargs):
    response = make_response(view(*args, **kwargs))
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response      
  return update_wrapper(no_cache, view)


# @app.route("/gross")
# @nocache
# def get_gross_image():
    
#     data_gross = df.groupby(['Year']).agg({"Gross Sales":"sum"}).reset_index()
    
#     plt.figure(figsize=(15,10))
#     plt.title("Gross Sales", fontsize=18)
    
#     x=list(range(len(data_gross['Year'])))
#     y=np.array(data_gross['Gross Sales']) 
#     plt.plot(x, y, 'rs--')
#     currnet_values=plt.gca().get_yticks()

#     plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in currnet_values])
#     plt.xticks(x, data_gross['Year'])
    
#     img = BytesIO()
#     plt.savefig('static/img/gross_1.png', format='png', dpi=200)
#     img.seek(0)
    
#     return send_file(img, mimetype='image/png')

# @app.route("/total")
@nocache
def get_total_image():
    
    data_profit = df.groupby(['Country','Year']).agg({"Profit":"sum"}).reset_index()
    
    isin_filter = data_profit['Year'].isin([2013])
    data_2013 = data_profit[isin_filter]
    isin_filter = data_profit['Year'].isin([2014])
    data_2014 = data_profit[isin_filter]    
    
    fig, ax1 =plt.subplots(figsize=(15,10))
    bar_width = 0.25
    
    # 지역이 5개 이므로 0,1,2,3,4 위치를 기준으로 삼음
    index = np.arange(5)
    
    ax1.tick_params(bottom=False)
    plt.ylabel("unit : $", color = "red", loc = "top")
    
    b1 = plt.bar(index, data_2013['Profit'], bar_width, alpha=0.4, color='red', label='2013')
    b2 = plt.bar(index + bar_width, data_2014['Profit'], bar_width, alpha=0.4, color='blue', label='2014')
    
    # 
    plt.title("국가, 년도별 이익", fontsize=18)
    
    plt.xticks(np.arange(bar_width/2, 5 + bar_width/2, 1), data_2013['Country'])
    
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
    plt.legend()
    
    img = BytesIO()
    plt.savefig(prjRoot + '/static/img/total_1.png', format='png', dpi=200)
    img.seek(0)

    
    return send_file(img, mimetype='image/png')

# @app.route("/country")
@nocache
def get_country_image():

    product = df['Product']
    cogs = df['COGS']
    
    plt.figure(figsize=(15, 10))
    plt.title("상품별 매출원가", fontsize=18)
    plt.bar(product, cogs, color='red', width=0.6)
    plt.xticks(rotation=45)
    
    img = BytesIO()
    plt.savefig(prjRoot + '/static/img/country_1.png', format='png', dpi=200)
    img.seek(0)
    
    return send_file(img, mimetype='image/png')

@nocache
def get_sales_profit_image():
   # 월별로 차례대로 정리하기 위한 List
    month_order = ['January','February','March','April', 'May','June','July','August','September','October','November','December']

    fig, ax = plt.subplots(figsize=(15,12)) 

    ## 2013년의 데이터는 9-12월분만 존재하기때문에 2014년만 비교.
    df1=df[df['Year']==2014]

    ## 데이터 Month별로 gross_sales와 profit 추출하기
    data_sales_profit = df1.groupby('Month Name')[["Gross Sales","Profit"]].sum().reindex(month_order) 
    data_sales_profit=pd.DataFrame(data_sales_profit) 

    plt.title("월별 총 매출과 이익(2014년)", fontsize=18)

    x=data_sales_profit.index
    y=data_sales_profit['Gross Sales']
    y1=data_sales_profit['Profit']

    ## 그래프 그리기
    plt.plot(x, y, 'rs--', label="Gross Sales", alpha=0.5)
    plt.plot(x, y1, 'o--', label="Profit", alpha=0.5)

    ## 범례지정
    plt.legend()

    ## y축 label 설정(Ex) 1e8 -> 100,000,000 )
    currnet_values=plt.gca().get_yticks()
    plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in currnet_values])

    # x축의 눈금표시하기(월별)
    plt.xticks(x, data_sales_profit.index)

    img = BytesIO()
    plt.savefig(prjRoot + '/static/img/sales_profit_1.png', format='png', dpi=200)
    img.seek(0)
   
    return send_file(img, mimetype='image/png')


@nocache
def get_units_sold_image():
    # '국가' 및 '제품'별로 그룹화하고 각 그룹의 '판매 수량' 합계를 계산
    grouped_df=df.groupby(['Country','Product'])['Units Sold'].sum().to_frame()

    wedgeprops={'width': 0.7, 'edgecolor': 'w', 'linewidth': 5}
    # country = 국가명출력 // Units Sold데이터에 대한 파이 및 막대차트 그리기
    # enumerate : index 출력을 위해 사용
    for i, (country, sub_df) in enumerate(grouped_df.groupby(level='Country')):
        # 두개의 축이 있는 서브플롯 만들기.
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(12,6))

        # 파이차트
        sub_df.loc[country,:].plot.pie(y='Units Sold', ax=ax1, legend=False, autopct='%.2f%%', fontsize=12, ylabel='', wedgeprops=wedgeprops)       

        # 막대차트
        sub_df.loc[country,:].plot.bar(y='Units Sold', ax=ax2, rot=45, fontsize=12, xlabel='')

        fig.suptitle("상품별 판매개수 ("+country+")", fontsize=18)

        #서브 플롯의 레이아웃 조정
        fig.tight_layout()

        #범례지정
        plt.legend(fontsize="12")
        print(i)
        
        #저장
        img = BytesIO()
        plt.savefig(prjRoot + '/static/img/units_sold_'+str(i)+'.png', format='png', dpi=200)
        img.seek(0)

    return send_file(img, mimetype='image/png')


@nocache
def get_profit_image():
    
    plt.subplots(figsize=(12,6))

    grouped_df=df[['Country','Product', 'Profit']]

    alpha = 0.5
    
    canada_sum=grouped_df[grouped_df['Country'] == 'Canada'].groupby('Product').Profit.sum() ## 나라별로 제품 긱각의 합계를 구함.
    germany_sum=grouped_df[grouped_df['Country'] == 'Germany'].groupby('Product').Profit.sum()
    france_sum=grouped_df[grouped_df['Country'] == 'France'].groupby('Product').Profit.sum()
    mexico_sum=grouped_df[grouped_df['Country'] == 'Mexico'].groupby('Product').Profit.sum()
    us_sum=grouped_df[grouped_df['Country'] == 'United States of America'].groupby('Product').Profit.sum()

    index= canada_sum.index.unique()

    ## 차트 그리기(쌓기)
    p1=plt.bar(index, canada_sum, alpha=alpha)
    p2=plt.bar(index, germany_sum, bottom=canada_sum, alpha=alpha)
    p3=plt.bar(index, france_sum, bottom=canada_sum+germany_sum, alpha=alpha)
    p4=plt.bar(index, mexico_sum, bottom=canada_sum+germany_sum+france_sum, alpha=alpha)
    p5=plt.bar(index, us_sum, bottom=canada_sum+germany_sum+france_sum+mexico_sum, alpha=alpha)


    plt.legend((p1[0],p2[0],p3[0],p4[0],p5[0]), df['Country'].unique())
    plt.title("상품별, 국가별 누적막대차트", fontsize=18)
    ## y축 label 설정((Ex) 1e8 -> 100,000,000 )
    currnet_values=plt.gca().get_yticks()
    plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in currnet_values])

    #저장
    img = BytesIO()
    plt.savefig(prjRoot + '/static/img/profit_0.png', format='png', dpi=200)
    img.seek(0)

    return send_file(img, mimetype='image/png')



@app.route("/", methods=["GET"])
def index():

    # 함수불러오기. 이미지저장
    get_country_image()
    get_total_image()
    # get_gross_image()
    get_sales_profit_image()
    get_units_sold_image()
    get_profit_image()

    datahead=HTML(df.head().to_html(classes='type01'))

    return render_template("test.html", datahead = datahead)

    
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9901)