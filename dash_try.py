import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import krangle as k
import datetime as dt

start = dt.datetime(2018,1,1,18,0)
end = dt.datetime(2018,1,10)

m = k.Manager()
df = m.get_instrument('EUR/USD','m1', start, end)

df = df.loc[:, ['date', 'bidopen', 'tickqty']]
df2 = m.m1(start, end)
df = df2.merge (df, left_on='date', right_on='date', how='left')


app = dash.Dash(__name__)

app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
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

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]




if __name__ == '__main__':
    app.run_server(debug=True)