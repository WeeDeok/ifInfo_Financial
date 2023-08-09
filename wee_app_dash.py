from dash import Dash, html, dcc, Input, Output, State
import wee_app as wp

app = Dash(__name__)

CONST_NO_RESULT = "조회값이 없습니다."
CONST_ERROR     = "조회 중 에러가 발생하였습니다."

global gdf
gdf = ""

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

                                    ],
                                    style = {}
                                ),  
                                html.Div(
                                    [
                                        
                                        dcc.Input(

                                            id = 'fromDt'
                                            , value = '2015'
                                            , style= {'width': '150px'}

                                        ),
                                        
                                        dcc.Input(

                                            id = 'toDt'
                                            , value = '2020'
                                            , style= {'width': '150px'}

                                        ),

                                    ]
                                    , style = {}
                                ),

                            ] 
                            , style = {"padding" : "10px"}       
                        ),
                        html.Div([
                                html.Button(
                                id = "srh_Btn"
                                , n_clicks = 0
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

@app.callback(
              Output('srh_Rst', 'children', allow_duplicate=True), 
              Input('srh_Btn', 'n_clicks'),
              State('rpt_Lst', 'value'), 
              State('cyl_Lst', 'value'), 
              State('fromDt', 'value'), 
              State('toDt', 'value'),
              State('frme_Lst', 'value'),
              prevent_initial_call=True
)
def update_Df (n_clicks, rptVal, cylVal, fromDt, toDt, frmeVal) :

    try : 
        global gdf
        gdf = wp.getDf(str(rptVal.split("-")[0].rstrip()), str(cylVal.split("-")[0].rstrip()), fromDt, toDt, 1, 1000)
        return draw_Select(gdf, frmeVal, fromDt, toDt, cylVal)

    except Exception as e :
        print(str(e))
        return CONST_ERROR

@app.callback(
              Output('srh_Rst', 'children'), 
              Input('frme_Lst', 'value'),
              State('srh_Rst', 'children'),
              State('cyl_Lst', 'value'), 
              State('fromDt', 'value'), 
              State('toDt', 'value'),  
              prevent_initial_call = True,  
)
def frme_Lst_on_Change (frmeVal, children, cylVal, fromDt, toDt) :

    if children == CONST_NO_RESULT or children == CONST_ERROR : return children
        
    return draw_Select(gdf, frmeVal, fromDt, toDt, cylVal)

def draw_Select (df, frmeVal, fromDt, toDt, cylVal) :

    if frmeVal == frameLst[0] :

        return wp.draw_DataTable(df)

    elif frmeVal == frameLst[1] :

        return wp.draw_Graph(df, fromDt, toDt, cylVal)

    else :

        return CONST_ERROR

if __name__ == '__main__':
    app.run_server(debug=True)