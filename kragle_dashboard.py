import datetime as dt

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots

import kragle

start = dt.datetime(2018, 11, 27, 13, 0)
end = dt.datetime(2018, 11, 27, 23, 0)

df_fourier = None

kdb = kragle.KragleDB('forex_raw')

app = dash.Dash(__name__, meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
])


# app.config["suppress_callback_exceptions"] = True


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
        ),

        html.Div([
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[
                    {"name": i, "id": i} for i in ['date', 'bidopen', 'tickqty']
                ],
                data=[],
                style_cell={'textAlign': 'left', 'padding': '5px'},
                sort_mode="multi",
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=20,
            ),
        ]),
        html.Br(),
    ])


def build_askbid_chart():
    return html.Div([
        html.Button(
            'Refresh DB names',
            id='button-dbnames-refresh',
            className='btn btn-blue'
        ),
        html.Div([
            dcc.Dropdown(
                id='chart-dbnames-dropdown',
            ),
            dcc.Dropdown(
                id='chart-instruments-dropdown',
            ),
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
            inputClassName="mx-2"
        ),
        html.Div([
            dcc.Graph(
                id='askbid-chart'
            )
        ]),

    ])


def build_sintetic_chart():
    return html.Div([
        html.Div([
            html.Div([
                html.P('Number of values'),
                dcc.Input(
                    id='input-fourier-number',
                    placeholder='1000',
                    type='text',
                    value='1000'
                )
            ]),
            html.Div([
                html.P('Delta'),
                dcc.Input(
                    id='input-fourier-delta',
                    placeholder='0.01',
                    type='text',
                    value='0.01'
                )
            ]),
            html.Button(
                'Save values',
                id='button-fourier-save',
                className='btn btn-blue'
            ),
            dcc.Loading(
                id="loading-1",
                type="default",
                children=html.Div(id="loading-output-1")
            ),
            html.P('...', id='button-fourier-save-label'),
            dcc.Graph(
                id='fourier-chart',
            ),
            dcc.Graph(
                figure=chaosChartFigure('xyz')
            ),
        ]),

    ])


def chaosChartFigure(axis):
    dftmp = pd.DataFrame(kragle.sintetic.attractor(20000, 0.01))
    return px.line(dftmp, x="i", y=axis, title='Attractor ')


def render_content():
    return html.Div(children=[render_top(), render_main_content()])


def render_top():
    return html.Nav(
        children=[
            html.Div(
                className="bg-gray-900 text-gray-200 px-4 ",
                children=[
                    html.P("Kragle", className="text-5xl text-bold inline-block"),
                    html.P("AI - Trading", className="ml-4 text- text-xs inline-block"),
                ],
            )
        ],
        **{"aria-label": "main-navigation"},
    )


def render_main_content():
    return html.Div(
        className="bg-white font-sans leading-normal tracking-normal mt-12 w-full",
        children=[
            html.Div(
                className="box-container",
                children=[
                    html.Div(className='box-wrapper',
                             children=html.Div(
                                 className='box',
                                 children=[
                                     build_sintetic_chart()
                                 ],
                             ),
                             ),
                    html.Div(
                        className='box-wrapper',
                        children=html.Div(
                            className='box',
                            children=build_askbid_chart(),
                        ),
                    ),
                    html.Div(
                        className='box-wrapper',
                        children=html.Div(
                            className='box',
                            children=build_explore_table(),
                        ),
                    ),
                ],
            ),
        ]
    )


@app.callback(
    [Output("chart-instruments-dropdown", "options"),
     Output("chart-instruments-dropdown", "value")],
    [Input('chart-dbnames-dropdown', 'value')]
)
def chartInstrumentsRefresh(dbname):
    global kdb
    kdb.close()
    kdb = kragle.KragleDB(dbname)
    insrtuments = kdb.get_instruments()
    options = []
    for insrtument in insrtuments:
        options.append({'label': insrtument, 'value': insrtument})
    return [options, insrtuments[0]]


@app.callback(
    [Output("chart-dbnames-dropdown", "options"),
     Output("chart-dbnames-dropdown", "value")],
    [Input('button-dbnames-refresh', 'n_clicks')]
)
def buttonDBNamesRefresh(n_clicks):
    names = kragle.getDBNames()
    options = []
    for name in names:
        options.append({'label': name, 'value': name})
    return [options, 'forex_raw']


@app.callback(
    Output("loading-output-1", "children"),
    [Input('button-fourier-save', 'n_clicks')]
)
def buttonFourierSaveLabel(n_clicks):
    if (n_clicks is not None):
        kdb = kragle.KragleDB('kragle_sintetic')
        kdb.client.drop_database('kragle_sintetic')
        instrument = 'fourier_01'
        kdb.fetch_dataframe(df_fourier, instrument, 'm1', check_duplicates=False)

        droplist = []
        for i in range(df_fourier.shape[0]):
            if i % 5 != 0:
                droplist.append(i)
        dfm5 = df_fourier.drop(droplist).reset_index(drop=True)
        kdb.fetch_dataframe(dfm5, instrument, 'm5', check_duplicates=False)

        droplist = []
        for i in range(dfm5.shape[0]):
            if i % 3 != 0:
                droplist.append(i)
        dfm15 = dfm5.drop(droplist).reset_index(drop=True)
        kdb.fetch_dataframe(dfm15, instrument, 'm15', check_duplicates=False)

        droplist = []
        for i in range(dfm15.shape[0]):
            if i % 2 != 0:
                droplist.append(i)
        dfm30 = dfm15.drop(droplist).reset_index(drop=True)
        kdb.fetch_dataframe(dfm30, instrument, 'm30', check_duplicates=False)

        droplist = []
        for i in range(dfm30.shape[0]):
            if i % 2 != 0:
                droplist.append(i)
        dfH1 = dfm30.drop(droplist).reset_index(drop=True)
        kdb.fetch_dataframe(dfH1, instrument, 'H1', check_duplicates=False)
        kdb.close()
    return [n_clicks]


@app.callback(
    [Output('fourier-chart', 'figure')],
    [Input('input-fourier-number', 'value')
        , Input('input-fourier-delta', 'value')
     ]
)
def fourierChartFigure(number, delta):
    global df_fourier
    number = int(float(number))
    delta = float(delta)
    df_fourier = pd.DataFrame(kragle.sintetic.fourier_01(number, delta))
    return [px.line(df_fourier, x="n", y='bidopen', title='Fourier')]


@app.callback(
    [Output('datatable-interactivity', 'data')],
    [Input('input-date-from', 'value')
        , Input('input-date-to', 'value')
        , Input('table-period', 'value')
     ]
)
def update_table(start_date, end_date, period):
    df = pd.DataFrame({})
    if (not start_date == '') & (not end_date == ''):
        start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        df = kdb.get_instrument('EUR/USD', period, start, end)
        df = df.loc[:, ['date', 'bidopen', 'tickqty']]
    return [df.to_dict('records')]


@app.callback(
    [Output('askbid-chart', 'figure')],
    [Input('askbid-input-date-from', 'value')
        , Input('askbid-input-date-to', 'value')
        , Input('askbid-table-period', 'value')]
)
def update_askbid_chart(start_date, end_date, period):
    df = pd.DataFrame({})
    k = kdb
    if (not start_date == '') & (not end_date == ''):
        start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        df = kdb.get_instrument('EUR/USD', period, start, end)

    ########################

    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["bidopen"], name="bidopen"),
        secondary_y=False,
    )
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["tickqty"], name="tickqty"),
        secondary_y=True,
    )
    return [fig1]


app.layout = render_content()

if __name__ == '__main__':
    app.run_server(debug=True)
