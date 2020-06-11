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
                value='m1',
                clearable=False
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
                    className='border',
                    placeholder='2019-05-01 12:00',
                    type='text',
                    value='2019-05-01 12:00'
                )  
            ]), 
            html.Div([
                html.P('To'),
                dcc.Input(
                    id='askbid-input-date-to',
                    className='border',
                    placeholder='2019-05-01 16:00',
                    type='text',
                    value='2019-05-01 16:00'
                )  
            ]), 
            dcc.RadioItems(
                id='askbid-table-period',
                options=[
                    {'label': 'm1 ', 'value': 'm1'},
                    {'label': 'm5 ', 'value': 'm5'},
                    {'label': 'm15 ', 'value': 'm15'},
                    {'label': 'm30 ', 'value': 'm30'},
                    {'label': 'H1 ', 'value': 'H1'},
                ],
                value='m1',
                labelStyle={'display': 'inline-block'},
                inputClassName = "mx-2"
            ),
            html.Div([
                dcc.Graph(
                    id='askbid-chart'
                )
            ]),

        ])

def build_chaos_chart():
    return html.Div([
            html.Div([
                dcc.Graph(
                    figure = chaosChartFigure('xyz')
                )
            ]),

        ])





def chaosChartFigure(axis):
    df = pd.DataFrame(kragle.utils.attractor(15000, 0.02))
    return px.line(df, x="i", y=axis, title='Attractor ' + axis)



def render_content():
    return html.Div(children=[render_top(),render_main_content()])

def render_top():
    return  html.Nav(
       children=[
            html.Div(
                className = "bg-gray-900 text-gray-200 px-4 ",
                children=[
                    html.P( "Kragle", className="text-5xl text-bold inline-block"),
                    html.P( "AI - Trading", className="ml-4 text- text-xs inline-block"),
                ],
            )
        ],
        **{"aria-label":"main-navigation"},
    )

def boxOut(): return "w-full lg:w-1/2 p-4"
def boxIn(): return "bg-white p-4 rounded-lg shadow-xl border"

def render_main_content():
    return  html.Div(
        className = "bg-white font-sans leading-normal tracking-normal mt-12",
        children=[
            html.Div(
                className = "flex flex-wrap p-4",
                children=[
                    html.Div(className = boxOut(),
                        children = html.Div(
                            className = boxIn(),
                            children=[
                                html.P("Settings", className="text-2xl font-extrabold"),
                                html.Br(),
                                html.P("Variabili globali", className="text-lg"),
                                dcc.Input(
                                    placeholder='Enter a value...',
                                    type='text',
                                    value='',
                                    className ="border"
                                ),
                                build_chaos_chart()
                            ],
                        ),
                    ),
                    html.Div(
                        className = boxOut(),
                        children = html.Div(
                            className = boxIn(),
                            children=build_askbid_chart(),
                        ),
                    ),
                    html.Div(
                        className =boxOut(),
                        children = html.Div(
                            className = boxIn(),
                            children=build_explore_table(),
                        ),
                    ),
                ],
            ),
        ]
    )

    



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
    ,Input('askbid-input-date-to', 'value')
    ,Input('askbid-table-period', 'value')]
)
def update_askbid_chart( start_date, end_date, period):
    df =pd.DataFrame({})
    if (not start_date == '')&(not end_date == ''):
        start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        df = init_df(m, start, end, period)
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



app.layout =render_content()

if __name__ == '__main__':
    app.run_server(debug=True)