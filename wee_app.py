from dash import dcc, dash_table

import json
import requests
import plotly.express as px
import pandas as pd

CONST_URL       = "http://ecos.bok.or.kr/api/StatisticSearch/"
CONST_KEY       = "W9PNCPSLDXK51N58Q8QE"
CONST_NO_RESULT = "조회값이 없습니다."
CONST_ERROR     = "조회 중 에러가 발생하였습니다."

dfColumns = ['통계표코드', '통계명', '통계항목코드1', '통계항목명1', '통계항목코드2', '통계항목명2', '통계항목코드3', '통계항목명3', '통계항목코드4', '통계항목명4', '단위', '시점', '값']

def getDf (rptVal, cylVal, fromDt, toDt, pgNbr, pgCnt, itmCd1, itmCd2, itmCd3, itmCd4) :

    try : 

        urlStr = CONST_URL + CONST_KEY + "/json/kr/" + str((pgNbr - 1) * pgCnt + 1) + "/" + str(pgNbr * pgCnt) + "/" + rptVal + "/" + cylVal + str("/" + fromDt) + str("/" + toDt)

        if itmCd1 != None and itmCd1 != "" : urlStr = str(urlStr + "/" + itmCd1)
        if itmCd2 != None and itmCd2 != "" : urlStr = str(urlStr + "/" + itmCd2)
        if itmCd3 != None and itmCd3 != "" : urlStr = str(urlStr + "/" + itmCd3)
        if itmCd4 != None and itmCd4 != "" : urlStr = str(urlStr + "/" + itmCd4)                                                                                                                              

        response = requests.get(urlStr)
        
        if response.status_code == 200 :

            json_data = json.loads(response.text)
            
            if json_data.get("StatisticSearch") :

                if json_data["StatisticSearch"]["list_total_count"] > 0 :
                    
                    df = pd.read_json(json.dumps(json_data["StatisticSearch"]["row"]), dtype = "object")
                    
                    df.columns = dfColumns

                    return df
                    
                else :
                        
                    return CONST_NO_RESULT
            
            else :
                
                return json_data["RESULT"]["MESSAGE"]

        else :

            return CONST_ERROR
        
    except Exception as e :
        print(str(e))
        return CONST_ERROR

def draw_DataTable (df) :

    return dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])

def draw_Graph (df, fromDt, toDt, cylVal) :

    cyl = str(cylVal.split('-')[1]).lstrip()

    fig = px.bar(df, x = df['통계항목명1'], y = df['값'])

    titleStr = fromDt + cyl
    if (toDt != None and toDt != "") and fromDt != toDt : titleStr = titleStr + " ~ " + toDt + cyl 
    titleStr = titleStr + " 기준"

    fig.update_layout(
        title = titleStr
    )

    fig.update_yaxes(
        title = "금리(%)"
    )
    
    fig.update_xaxes(
        title = '통계항목명'
    )

    return dcc.Graph(figure=fig)
