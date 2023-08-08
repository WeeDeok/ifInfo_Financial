from dash import Dash, html, dcc, Input, Output, State, dash_table

import json
import requests
import plotly.express as px
import plotly.subplots as make_subplots
import pandas as pd
import plotly.graph_objs as go

app = Dash(__name__)

CONST_URL       = "http://ecos.bok.or.kr/api/StatisticSearch/W9PNCPSLDXK51N58Q8QE/json/kr/1/1000/"
CONST_NO_RESULT = "조회값이 없습니다."
CONST_ERROR     = "조회 중 에러가 발생하였습니다."

dfColumns = ['통계표코드', '통계명', '통계항목코드1', '통계항목명1', '통계항목코드2', '통계항목명2', '통계항목코드3', '통계항목명3', '통계항목코드4', '통계항목명4', '단위', '시점', '값']

rptDropDownLst = ["722Y001 - 1.3.1. 한국은행 기준금리 및 여수신금리", 
                  "817Y002 - 1.3.2.1. 시장금리(일별)", 
                  "721Y001 - 1.3.2.2. 시장금리(월,분기,년)", 
                  "121Y006 - 1.3.3.2.1. 예금은행 대출금리(신규취급액 기준)", 
                  "121Y015 - 1.3.3.2.2. 예금은행 대출금리(잔액 기준)"]

cylDropDownLst = ["A - 년", 
                  "S - 반년", 
                  "Q - 분기", 
                  "M - 월", 
                  "SM - 반월", 
                  "D - 일"]

frameLst = [
    "DataTable",
    "Graph"
]

app.layout = html.Div(

                    [

                        html.Div(
                            [

                                dcc.Dropdown(
                                    rptDropDownLst
                                    , rptDropDownLst[0]
                                    , id = 'rpt_Lst'
                                    , style= {'width': '500px'}

                                ),

                                dcc.Dropdown(
                                    cylDropDownLst
                                    , cylDropDownLst[0]
                                    , id = 'cyl_Lst'
                                    , style= {'width': '500px'}

                                ),

                                dcc.Input(

                                    id = 'fromDt'
                                    , value = '2015'
                                    , style= {'width': '500px'}

                                ),

                                dcc.Input(

                                    id = 'toDt'
                                    , value = '2020'
                                    , style= {'width': '500px'}
                                    , disabled = True

                                ),

                            ] 
                            , style = {"padding" : "10px"}       
                        ),
                        html.Div([
                                html.Button(
                                id = "srh_Btn"
                                , n_clicks= 0
                                , children = "조회"
                                ),
                            ],
                            style = {"padding" : "10px"}
                        ),
                         
                        html.Div([
                                    dcc.Dropdown(
                                        frameLst
                                        , frameLst[0]
                                        , id = 'frme_Lst'
                                        , style= {'width': '300px'}
                                    ),
                                ]
                                , style = {"padding" : "10px"}
                            ),
                        html.Div(
                            id = "srh_Rst"
                            , children = CONST_NO_RESULT
                            , style = {"padding" : "10px"}
                        ),
                        
                    ]

                )

@app.callback(Output('srh_Rst', 'children', allow_duplicate=True), 
              Input('srh_Btn', 'n_clicks'),
              State('rpt_Lst', 'value'), 
              State('cyl_Lst', 'value'), 
              State('fromDt', 'value'), 
              State('toDt', 'value'),
              State('frme_Lst', 'value'),
              prevent_initial_call=True)
def update_Lst (n_clicks, rpt_Lst_Value, cyl_Lst_Value, fromDt_Value, toDt_Value, frme_Value) :

    try : 

        response = requests.get(CONST_URL + str(rpt_Lst_Value.split('-')[0]).rstrip() + "/" + str(cyl_Lst_Value.split('-')[0]).rstrip() + str("/" + fromDt_Value) + str("/" + fromDt_Value))
        
        if response.status_code == 200 :

            json_data = json.loads(response.text)
                
            if json_data["StatisticSearch"]["list_total_count"] > 0 :
                
                global df

                df = pd.read_json(json.dumps(json_data["StatisticSearch"]["row"]))
                
                df.columns = dfColumns

                return draw_Select(frme_Value, fromDt_Value, toDt_Value, cyl_Lst_Value)
                
            else :
                    
                return CONST_NO_RESULT
            
        else :

            return CONST_ERROR
        
    except Exception as e :
        print(str(e))
        return CONST_ERROR

@app.callback(Output('srh_Rst', 'children'), 
              Input('frme_Lst', 'value'),
              State('srh_Rst', 'children'),
              State('cyl_Lst', 'value'), 
              State('fromDt', 'value'), 
              State('toDt', 'value'),  
              prevent_initial_call = True,  
)
def frme_Lst_on_Change (frme_Value, children, cyl_Lst_Value, fromDt_Value, toDt_Value) :

    if children == CONST_NO_RESULT or children == CONST_ERROR : return

    return draw_Select(frme_Value, fromDt_Value, toDt_Value, cyl_Lst_Value)

def draw_DataTable () :

    children = []
    children.append(dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]))

    return children

def draw_Graph (fromDt, toDt, cylVal) :

    fig = px.bar(df, x = df['통계항목명1'], y = df['값'])
    
    fig.update_layout(
        title = fromDt + str(cylVal.split('-')[1]).lstrip() + " 기준"
    )

    fig.update_yaxes(
        title = "금리(%)"
    )
    
    fig.update_xaxes(
        title = '통계항목명'
    )

    children = []
    children.append(dcc.Graph(figure=fig))
    
    return children

def draw_Select (frmeVal, fromDt, toDt, cylVal) :

    if frmeVal == frameLst[0] :

        return draw_DataTable()

    elif frmeVal == frameLst[1] :

        return draw_Graph(fromDt, toDt, cylVal)

    else :

        return CONST_ERROR

if __name__ == '__main__':
    app.run_server(debug=True)