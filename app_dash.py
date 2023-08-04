from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.subplots as make_subplots
import pandas as pd
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

df=pd.read_excel('sample.xlsx')

df1=df.query("Year == 2014") # df[df['Year']==2014]
# Y축들 (Product - X축 제외하고 수치)
df2=df1.loc[:, ['Gross Sales', 'Discounts',' Sales', 'COGS', 'Profit']] 


app.layout = html.Div(
                    [
                    ############# 1. Product별 수치계산.
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label('Y축'),
                                    dcc.Dropdown(
                                        # Y축들 (Product - X축 제외)
                                        df2.columns,
                                        # default 값
                                        'Gross Sales',
                                        id='yaxis-column'
                                    ),
                                ],
                                
                                style={
                                'width' : '30%', 
                                'display': 'inline',
                                },
                            ),

                            dcc.Graph(id='yaxis_01'),
                        ],
                        style={'padding':10, 'display': 'inline-flex', 'flex-direction':'row', 'height': '600px' },
                    ),

                    ############# 2. 월별 총 매출과 이익 (in 2014)
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.RadioItems(
                                            ['Gross Sales', 'Profit'],
                                            'Gross Sales',
                                            id='yaxis_column_01',
                                            inline=True,
                                    ),
                                ],
                                style={
                                        'width' : '30%', 
                                        'display': 'inline',
                                },
                            ),
                            dcc.Graph(id='sales_and_profit'),
                        ],
                        style={'padding':10, 'display':'inline-flex', 'flex-direction':'row', 'height':'600px'}   
                    ),

                    
                    ############# 3. 상품별 판매비율 및 개수
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        df1['Country'].unique(),
                                        'Canada',
                                        id='country-column',
                                    )
                                ],
                                style={
                                        'width' : '30%', 
                                        'display': 'inline',
                                },
                            ),
                        dcc.Graph(id='pc_unit_solds_by_country'),
                        ],   
                    # dcc.Graph(id='bar_unit_solds_by_country')
                        style={'padding':10, 'display':'inline-flex', 'flex-direction':'row', 'height':'600px'}   
                    ),


                    ############# 4. 국가별, 상품별 Profit 막대그래프 및 누적막대그래프
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.RadioItems(
                                        df1['Country'].unique(),
                                        'Canada',
                                        id='country-column01',
                                        inline=True,
                                    ),
                                ],
                                style={
                                        'width' : '30%', 
                                        'display': 'inline',
                                },
                            ),
                            dcc.Graph(id='bar_profit'),
                            dcc.Graph(id='stack_bar_profit')
                        ],
                    )
                ],

                # 전체 감싸는 div : column 방향으로 정렬
                style={'display':'flex', 'flex-direction': 'column'},
            )


############# 1. Product별 수치계산.
@app.callback(
    Output('yaxis_01', 'figure'),
    Input('yaxis-column', 'value'),
)
def update_graph_yaxis01(
    yaxis_column_name
):
    
    df2=df1.groupby('Product')[yaxis_column_name].sum().reset_index()
    # print(df2[yaxis_column_name])
    fig = px.bar(df2, x=df2['Product'], y=df2[yaxis_column_name]
                 )

    fig.update_layout(
        title='Product별 '+ yaxis_column_name
    )

    fig.update_yaxes(
        title=yaxis_column_name
    )
    
    fig.update_xaxes(
        title='Product'
    )
    return fig


############# 2. 월별 총 매출과 이익
@app.callback(
    Output('sales_and_profit', 'figure'),
    Input('yaxis_column_01', 'value'),
)
def update_graph_sales_profit(
    yaxis_column_name
):
    # 1월~12월 순서대로 세팅을 위해
    month_order = ['January','February','March','April', 'May','June','July','August','September','October','November','December']
    
    # 월별 Gross_Sales or Profit 값 구함.
    data_sales_profit = df1.groupby('Month Name')[[yaxis_column_name]].sum().reindex(month_order)
    
    #df로 변환
    data_sales_profit=pd.DataFrame(data_sales_profit) 
    
    x=data_sales_profit.index
    y=data_sales_profit[yaxis_column_name]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines'))
    # fig.add_trace(go.Scatter(x=1, y=y1, mode='lines'))

    return fig

############# 3. 상품별 판매비율 및 개수
@app.callback(
        Output('pc_unit_solds_by_country','figure'),
        # Output('bar_unit_solds_by_country', 'figure'),
        Input('country-column', 'value')
)
def update_graph_country_units_sold(
    country_name
):
    # '국가' 및 '제품'별로 그룹화하고 각 그룹의 '판매 수량' 합계를 계산
    grouped_df=df1.groupby(['Country','Product'], as_index=False)['Units Sold'].sum()
    
    # 파이 차트 그리기
    fig=px.pie(grouped_df[grouped_df['Country']==country_name], values='Units Sold', names='Product', title='상품별 판매비율 및 개수'+"("+country_name+")")
    # fig.add_bar(grouped_df[grouped_df['Country']==country_name], x=grouped_df['Product'], y=grouped_df['Units Sold'])
    return fig
    

############# 4. 국가별, 상품별 Profit 막대그래프 및 누적막대그래프
@app.callback(
    Output('bar_profit', 'figure'),
    Output('stack_bar_profit', 'figure'),
    Input('country-column01', 'value')
)
def update_stack_bar_graph(
    country_column_name
):
    # data에서 Country, Product, Profit 컬럼만 불러오기
    grouped_df=df1[['Country','Product', 'Profit']]

    # Country와 Profit을 기준으로 groupby, Profit의 합계를 구함.
    stack_df=grouped_df.groupby(['Country','Product'], as_index=False)['Profit'].sum()
    
    # Country 선택시 Product별로 Profit 변화하는 막대그래프
    fig=px.bar(stack_df, x=stack_df[stack_df['Country']==country_column_name]['Product'], 
                         y=stack_df[stack_df['Country']==country_column_name]['Profit'], 
                         title='Product별 Profit'
                        )
    
    # 누적막대그래프 표현
    fig1=(px.bar(stack_df, x=stack_df['Product'],
                                       y=stack_df['Profit'],
                                       color=stack_df['Country']))

    return fig, fig1


    

if __name__ == '__main__':
    app.run_server(debug=True)