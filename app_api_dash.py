import requests
from bs4 import BeautifulSoup 
import pandas as pd
from datetime import datetime, date

##########flask와 dash
from dash import Dash, html, dcc, Input, Output, State, dash_table
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio


# 시각화 템플릿 커스터마이징
pio.templates.default="plotly_white"


## 한국은행 OpenAPI(통계조회 조건설정)호출함수
def get_openapi(STAT_CD, PERIOD, START_DATE, END_DATE, END_NUM, START_NUM=1,  STATICS_CODE1="", STATICS_CODE2="", STATICS_CODE3="", KEY='PCD4Q4DGVD0X9ZF9CA0G'):
    url = "http://ecos.bok.or.kr/api/StatisticSearch/{}/xml/kr/{}/{}/{}/{}/{}/{}/{}/{}/{}".format(
                                                                              KEY # 인증키
                                                                            , START_NUM #요청 시작건수
                                                                            , END_NUM #요청 종료건수
                                                                            , STAT_CD # 추출할 통계지표의 코드
                                                                            , PERIOD # 기간 단위
                                                                            , START_DATE # 데이터 시작일
                                                                            , END_DATE # 데이터 종료일
                                                                            , STATICS_CODE1 # 통계항목코드1
                                                                            , STATICS_CODE2 # 통계항목코드2
                                                                            , STATICS_CODE3 # 통계항목코드3
                                                                            ) 
    
    # https://ecos.bok.or.kr/api/StatisticSearch/{}/xml/kr/1/10/802Y001/D/20130101/20230807/ - KOSPI 지수 API
    ## 정의된 OpenAPI URL을 호출                              
    # print("url", url)
    response = requests.get(url).content.decode('utf-8')
    # print("response", response)
    # bs에는 html파서를 지원하고 사용하지만, 파서보다 lxml이라는 모듈이 속도가 빨라 많이 사용함
    xml_obj = BeautifulSoup(response, 'lxml-xml')
    # row의 하위에 있는 요소들만 찾아 리스트로 변환.
    rows=xml_obj.findAll("row") 
    
    
    item_list=[
    'STAT_CODE', # 통계표코드
    'STAT_NAME', # 통계명
    'ITEM_CODE1', # 통계항목코드1
    'ITEM_NAME1', # 통계항목이름1
    'ITEM_CODE2',
    'ITEM_NAME2',
    'TIME', #날짜
    'DATA_VALUE', #뉴스 심리지수 값
    ]

    result_list = list()
    #dataFrame을 만들기 위해 값을 담는 구문
    for p in range(0, len(rows)):
        info_list = list()
        for i in item_list:
            try:
                info=rows[p].find(i).text 
            except:
                info=""
            
            info_list.append(info)
        # print(info_list) # ['521Y001', '6.4. 뉴스심리지수(실험적 통계)', 'A001', '뉴스심리지수', '20220829', '92.39']
        result_list.append(info_list)
    result_df = pd.DataFrame(result_list, columns = ['통계표코드', '통계명', '통계항목코드1', '통계항목이름1','통계항목코드2','통계항목이름2','시점', '값'])

    return result_df




####  파라미터 정의

# 일수 구하기
date_to_compare = datetime.now()-datetime.strptime("20200101", "%Y%m%d")
END_NUM = date_to_compare.days

# 인증키
KEY = 'PCD4Q4DGVD0X9ZF9CA0G'
PERIOD = 'D'
START_DATE = '20200101'
END_DATE_yymmdd = datetime.today().strftime('%Y%m%d')
END_DATE_yymm = datetime.today().strftime('%Y%m')
END_DATE_yy = datetime.today().strftime('%Y')
 
# 단순히 뉴스기사에 나타난 긍정문장과 부정문장을 카운트한 뒤 지수화한 지표이다. 
# 뉴스심리지수는 설문조사에 의존하는 다른 경제심리지수 와 달리 수시로 입수 가능한 뉴스기사를 이용하여 작성하므로, 
# 경제심리 변화를 신속하게 포착하고 변동요인을 쉽게 파악할 수 있는 장점이 있다.
result_df = get_openapi('521Y001', PERIOD, START_DATE, END_DATE_yymmdd, END_NUM)

# KOSPI
result_df1 = get_openapi('802Y001', PERIOD, START_DATE, END_DATE_yymmdd, END_NUM, STATICS_CODE1='0001000')
# object로 되어있는 컬럼타입 변경END_DATE_yymm=
result_df=result_df.astype({'값':'float'})
result_df1=result_df1.astype({'값':'float'})

# 예금은행 지역별 수신
data_dict={
    'A00' : '서울',
    'B00' : '부산',
    'C00' : '대구',
    'D00' : '인천',
    'F00' : '광주',
    'E00' : '대전',
    'G00' : '울산',
    'L00' : '경기',
    'M00' : '강원',
    'N00' : '충북',
    'P00' : '충남',
    'Q00' : '전북',
    'R00' : '전남',
    'S00' : '경북',
    'T00' : '경남',
    'U00' : '제주',
    'H00' : '세종'
}

# dataFrame 병합 : 서울 ~ 세종까지
list_tmp_df=[]
for key in (data_dict.keys()):
    result_df2 = get_openapi('141Y002', PERIOD='A', START_DATE='2013', END_DATE='2023', END_NUM=10, STATICS_CODE1='100000', STATICS_CODE2=key)
    list_tmp_df.append(result_df2)
result_df3=pd.concat(list_tmp_df, ignore_index=True)

# object로 되어있는 컬럼타입 변경
result_df3=result_df3.astype({'값':'float', '통계항목이름2':'string'})

######################### 예금은행 수신/대출금리
# 예금은행 수신금리(잔액기준)/ 예금은행 대출금리(잔액기준) 선택 후   
# 예금은행 수신금리(잔액기준) 일때, 1.총수신(요구불예금 및 수시입출식 저축성예금 포함) 
#                                2.저축성수신(요구불예금 및 수시입출식 저축성예금제외) 
#                                3.저축성수신(금융채 제외)
# 예금은행 대출금리(잔액기준) 일때 1. 총대출 2.총대출(당좌대출 제외) 그래프 출력

data_dict1={
    'BEABAB2' : '총수신(요구불예금 및 수시입출식 저축성예금)',
    'BEABAB21' : '저축성수신(요구불예금 및 수시입출식 저축성예금제외)',
    'BEABAB1' : '저축성수신(금융채 제외)'
}

data_dict2={
    'BECBLB01' : '총대출',
    'BECBLB02' : '총대출(당좌대출 제외)'
}
list_tmp_df1=[]
for key in data_dict1.keys():
    result_df4 = get_openapi('121Y013', PERIOD='A', START_DATE='2013', END_DATE='2023', END_NUM=10, STATICS_CODE1=key)
    list_tmp_df1.append(result_df4)
for key in data_dict2.keys():
    result_df5=get_openapi('121Y015', PERIOD='A',START_DATE='2013', END_DATE='2023', END_NUM=10, STATICS_CODE1=key)
    list_tmp_df1.append(result_df5)

result_df6=pd.concat(list_tmp_df1, ignore_index=True)
result_df6=result_df6.astype({'값':'float'})

######################### 은행 대출금 연체율

# 날짜의 차이를 구하기 위한 라이브러리(월단위계산) : relativedelta
from dateutil.relativedelta import relativedelta

yymm_diff=relativedelta(datetime.strptime("201301", "%Y%m"), datetime.strptime("202308", "%Y%m")) ##두 날짜의 차이 구하기
yymm_diff_months = 12*yymm_diff.years + yymm_diff.months ## 차이나는 개월수
print(-yymm_diff_months)

data_dict3={
    'MO3AA' : '기업대출',
    'MO3AB' : '가계대출',
    'MO3AC' : '신용카드대출'
}

list_tmp_df2=[]
for key in data_dict3.keys():
    result_df7=get_openapi('901Y054', PERIOD='M', START_DATE='201301', END_DATE=END_DATE_yymm, END_NUM=-yymm_diff_months, STATICS_CODE1=key, STATICS_CODE2='AB')
    list_tmp_df2.append(result_df7)
result_df8=pd.concat(list_tmp_df2, ignore_index=True)
print(result_df8['통계항목이름1'].unique())
result_df8=result_df8.astype({'값':'float'})



########################## DASH 관련 코드 작성 ##############################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
                html.Div(
                    [
                        # start of inner div
                        html.Div(
                            [
                                dcc.RadioItems(
                                    ['값',],
                                    '값',
                                    id="news_value", 
                                )
                            ]
                        ), #end of inner div
                        dcc.Graph(id = "time_series_chart"),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Dropdown(
                                    result_df3['통계항목이름2'].unique(),
                                    '서울',
                                    id='area_name_columns'
                                )
                            ]
                        ),
                        dcc.Graph(id="bar_chart_by_account")
                    ]
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                dcc.RadioItems(
                                    result_df6['통계명'].unique(),
                                    '1.3.3.1.2. 예금은행 수신금리(잔액 기준)',
                                    id='rate_radio'
                                ),
                                html.Hr(),
                                dcc.RadioItems(
                                
                                id="choice_radio")
                            ]
                        ),
                        dcc.Graph(id='time_series_chart_by_rate')
                        
                    ]
                ),

                ########### 은행 대출금 연체율
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Dropdown(
                                    result_df8['통계항목이름1'].unique(),
                                    '기업대출',
                                    id='delinquency_rate'
                                ),
                            ]
                        ),
                        dcc.Graph(id='time_series_chart_by_delinquency_rate')
                        
                    ]
                ) 
            ]) ## 전체 Div


@app.callback(
    Output("time_series_chart", "figure"),
    Input("news_value", "value")
)
def get_time_series_chart(news_value):

    # 기본 figure를 make_subplots으로 생성.
    # 이중대괄호안에 {"secondary_y" : True} 값을 넣은것은 1행, 1열의 trace에 2중 Y축을 활성화한다는 의미.
    fig = make_subplots(specs=[[{"secondary_y" : True}]])

    fig.add_trace(go.Scatter(x=result_df["시점"], y=result_df[news_value], name="뉴스심리지수"), secondary_y=False ,
                  ) #왼쪽에 축 생성
    fig.add_trace(go.Scatter(x=result_df1["시점"], y=result_df1[news_value], name="KOSPI 지수"), secondary_y=True
                  ) #오른쪽에 축 생성
    
    fig.update_yaxes(title="뉴스심리지수", secondary_y=False)
    fig.update_yaxes(title="KOSPI지수", secondary_y=True)

    fig.update_layout(coloraxis_showscale=False)
    return fig




@app.callback(
    Output("bar_chart_by_account", 'figure'),
    Input("area_name_columns","value")
)
def get_bar_chart(area_name_columns):

    fig=px.bar(data_frame=result_df3[result_df3['통계항목이름2']==area_name_columns], 
               x=result_df3[result_df3['통계항목이름2']==area_name_columns]['시점'], 
               y=result_df3[result_df3['통계항목이름2']==area_name_columns]['값'],
               title='예금은행 지역별/연도별 수신(말잔)')
    fig.update_yaxes(title="십억원", tickformat=',')
    return fig



@app.callback(
    Output("choice_radio","options"),
    Output("choice_radio", "value"),
    Input("rate_radio","value")
)
def set_ratio_options(rate_radio):
    options=(result_df6[result_df6['통계명'] == rate_radio]['통계항목이름1'].unique())
    # ['총수신(요구불예금 및 수시입출식 저축성예금 포함)' '저축성수신(요구불예금 및 수시입출식 저축성예금 제외)' '저축성수신(금융채 제외)']

    return [{'label': i , 'value': i} for i in options], options[0]

@app.callback(
    Output('time_series_chart_by_rate', 'figure'),
    Input("choice_radio","value"),
    Input("rate_radio", 'value')
)
def get_time_series_chart_by_rate(choice_radio, rate_radio):
    graph_df=(result_df6.loc[(result_df6['통계명']==rate_radio) & (result_df6['통계항목이름1']==choice_radio)])

    fig=px.line(data_frame=graph_df, x=graph_df['시점'], y=graph_df['값'], markers=True)

    fig.update_yaxes(title="이자율(%)")
    return fig



# ㅇ 연체율 : 연체금액을 대출채권금액으로 나눈 값으로 은행 대출채권의 건전성을 나타내는 지표로 활용

# ㅇ 산식 : [ 연체대출채권 / 총대출채권 ] × 100
# · 연체대출채권 : 이자 또는 원금의 상환 약정기일에 상환되지 아니한 대출채권(1개월이상 원리금연체기준)
# · 총대출채권:「은행업감독업무시행세칙」〈별표12〉에서 정한 무수익 여신 산정대상 여신에서 은행 및 종금계정의 확정지급보증을 제외한 금액

@app.callback(
    Output("time_series_chart_by_delinquency_rate", "figure"),
    Input("delinquency_rate", "value")
)
def get_time_series_chart_by_delinquency_rate(delinquency_rate_value):

    fig=go.Figure()
    fig.add_trace(go.Scatter(x=result_df8[result_df8['통계항목이름1']==delinquency_rate_value]['시점'], 
                             y=result_df8[result_df8['통계항목이름1']==delinquency_rate_value]['값'], name=delinquency_rate_value)) 

    fig.update_yaxes(title="(%)")
    fig.update_layout(
        title=dict(
        text='<b>은행대출금 연체율(은행전체기준)</b><br>연체율:전체 대출잔액중에서 한달이상 원리금이 연체된 잔액의 비중')
    )

    return fig




if __name__ == '__main__':
    app.run_server(debug=True)