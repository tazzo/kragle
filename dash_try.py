import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import krangle as k
import datetime as dt


start = dt.datetime(2018,1,2,18,0)
end = dt.datetime(2018,1,2,19,0)

m = k.Manager()


def init_df(m, start, end):

    df = m.get_instrument('EUR/USD','m1', start, end)

    df = df.loc[:, ['date', 'bidopen', 'tickqty']]
    df2 = m.m1(start, end)
    #return df2.merge (df, left_on='date', right_on='date', how='left')
    return df

df = init_df(m, start, end)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.P('From'),
        dcc.Input(
            id='input-date-from',
            placeholder='2019-04-29 12:00',
            type='text',
            value='2019-04-29 12:00'
        )  
    ]), 
    html.Div([
        html.P('To'),
        dcc.Input(
            id='input-date-to',
            placeholder='2019-05-02 12:00',
            type='text',
            value='2019-05-02 12:00'
        )  
    ]), 

    html.Div([
        dash_table.DataTable(
            id='datatable-interactivity',
            columns=[
                {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
            ],
            data = pd.DataFrame([{}]).to_dict('records'),
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 20,
        ),
    ])
])
    

@app.callback(
    [Output('datatable-interactivity', 'style_data_conditional')
    , Output('datatable-interactivity', 'data')],
    [Input('datatable-interactivity', 'selected_columns')
    ,Input('input-date-from', 'value')
    ,Input('input-date-to', 'value')]
)
def update(selected_columns, start_date, end_date):
 
    df =pd.DataFrame({})
    if (not start_date == '')&(not end_date == ''):
        start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        df = init_df(m, start, end)
    
    return [{'if': { 'column_id': i }, 'background_color': '#D2F3FF'} for i in selected_columns], df.to_dict('records') 




if __name__ == '__main__':
    app.run_server(debug=True)