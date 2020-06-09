import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import kragle 
import datetime as dt
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

start = dt.datetime(2018,11,27,13,0)
end = dt.datetime(2018,11,27,23,0)



m = kragle.Manager()


def init_df(m, start, end, period='m1'):

    df = m.get_instrument('EUR/USD',period, start, end)

    df = df.loc[:, ['date', 'bidopen', 'askopen', 'tickqty']]
    #df2 = m.m1(start, end)
    #return df2.merge (df, left_on='date', right_on='date', how='left')
    return df

df = init_df(m, start, end)


app = dash.Dash(__name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])
#app.config["suppress_callback_exceptions"] = True



def build_explore_table():
    return html.Div([
            html.Div([
                html.P('From'),
                dcc.Input(
                    id='input-date-from',
                    placeholder='2018-11-27 13:00',
                    type='text',
                    value='2018-11-27 13:00'
                )  
            ]), 
            html.Div([
                html.P('To'),
                dcc.Input(
                    id='input-date-to',
                    placeholder='2018-11-27 23:00',
                    type='text',
                    value='2018-11-27 23:00'
                )  
            ]), 
            dcc.Dropdown(
                id='table-period',
                options=[
                    {'label': 'm1', 'value': 'm1'},
                    {'label': 'm5', 'value': 'm5'},
                    {'label': 'm15', 'value': 'm15'},
                    {'label': 'm30', 'value': 'm30'},
                    {'label': 'H1', 'value': 'H1'},
                ],
                value='m1'
            ) ,

            html.Div([
                dash_table.DataTable(
                    id='datatable-interactivity',
                    columns=[
                        {"name": i, "id": i} for i in df.columns
                    ],
                    data = pd.DataFrame([{}]).to_dict('records'),
                    style_cell={'textAlign': 'left', 'padding': '5px'},
                    sort_mode="multi",
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current= 0,
                    page_size= 20,
                ),
            ]),
            html.Br(),
        ])

def build_askbid_chart():
    return html.Div([
            html.Div([
                html.P('From'),
                dcc.Input(
                    id='askbid-input-date-from',
                    placeholder='2019-05-01 12:00',
                    type='text',
                    value='2019-05-01 12:00'
                )  
            ]), 
            html.Div([
                html.P('To'),
                dcc.Input(
                    id='askbid-input-date-to',
                    placeholder='2019-05-01 16:00',
                    type='text',
                    value='2019-05-01 16:00'
                )  
            ]), 

            html.Div([
                dcc.Graph(
                    id='askbid-chart'
                )
            ]),

        ])




def render_content():
    return html.Div(children=[render_top(),render_main_content()])

def render_top():
    return  html.Nav(
        className = "navbar",
        role = "navigation",
        children=[
            html.Div(
                className = "navbar-brand",
                children=[
                    html.A(
                        className = "navbar-item",
                        href = '/',
                        children = [
                            html.P("Kragle ", className = "title is-2 has-text-link"),
                            html.Br(),
                            html.P("AI Trading", className = "subtitle is-7 has-text-white-ter"),
                        ]
                    ),
                    html.A(
                        className = "burger navbar-burger",
                        children = [
                            html.Span( ),
                            html.Span(),
                            html.Span( ),   
                        ]
                    )
                ],
            )
        ],
        **{"aria-label":"main-navigation"},
    )


def render_main_content():
    return  html.Section(
        className = "section",
        children=[
            html.Div(
                className = "columns",
                children=[
                    html.Div(className = "column is-one-quarter",
                        children = html.Div(
                            className = "box",
                            children=[
                                html.P("Settings", className="title is-1 is-spaced"),
                                html.Br(),
                                html.P("Variabili globali", className="subtitle is-7"),
                                dcc.Input(
                                    placeholder='Enter a value...',
                                    type='text',
                                    value='',
                                    className ="is-info"
                                ),
                                html.P("""Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""),

                                html.P("""Curabitur pretium tincidunt lacus. Nulla gravida orci a odio. Nullam varius, turpis et commodo pharetra, est eros bibendum elit, nec luctus magna felis sollicitudin mauris. Integer in mauris eu nibh euismod gravida. Duis ac tellus et risus vulputate vehicula. Donec lobortis risus a elit. Etiam tempor. Ut ullamcorper, ligula eu tempor congue, eros est euismod turpis, id tincidunt sapien risus a quam. Maecenas fermentum consequat mi. Donec fermentum. Pellentesque malesuada nulla a mi. Duis sapien sem, aliquet nec, commodo eget, consequat quis, neque. Aliquam faucibus, elit ut dictum aliquet, felis nisl adipiscing sapien, sed malesuada diam lacus eget erat. Cras mollis scelerisque nunc. Nullam arcu. Aliquam consequat. Curabitur augue lorem, dapibus quis, laoreet et, pretium ac, nisi. Aenean magna nisl, mollis quis, molestie eu, feugiat in, orci. In hac habitasse platea dictumst.""")],
                        ),
                    ),
                    html.Div(
                        className = "column",
                        children = html.Div(
                            className = "box ",
                            children=build_explore_table(),
                            
                        ),
                    ),
                     html.Div(
                        className = "column ",
                        children = html.Div(
                            className = "box ",
                            children=build_askbid_chart(),
                        ),
                    ),
                ],
            )
        ]
    )

    

app.layout =render_content()


@app.callback(
    [ Output('datatable-interactivity', 'data')],
    [Input('input-date-from', 'value')
    ,Input('input-date-to', 'value')
    ,Input('table-period', 'value')
    ]
)
def update_table( start_date, end_date, period):
 
    df =pd.DataFrame({})
    if (not start_date == '')&(not end_date == ''):
        start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        df = init_df(m, start, end, period=period)
    return [ df.to_dict('records') ]

@app.callback(
    [ Output('askbid-chart', 'figure')],
    [Input('askbid-input-date-from', 'value')
    ,Input('askbid-input-date-to', 'value')]
)
def update_askbid_chart( start_date, end_date):
 
    df =pd.DataFrame({})
    if (not start_date == '')&(not end_date == ''):
        start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        df = init_df(m, start, end)
    ########################
    
    
    df['fork'] =df['askopen']-df['bidopen']

    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["bidopen"], name="bidopen"),
        secondary_y=False,
    )
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["askopen"], name="askopen"),
        secondary_y=False,
    )
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["tickqty"], name="tickqty"),
        secondary_y=True,
    )


    return [ fig1 ]




if __name__ == '__main__':
    app.run_server(debug=True)