import datetime as dt

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots

import kragle

df_fourier = None
df_random_list = []

kdb = kragle.KragleDB('forex_raw')

app = dash.Dash(__name__, meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
])


# app.config["suppress_callback_exceptions"] = True


def build_askbid_chart():
    return html.Div([
        html.Button(
            'Refresh DB names',
            id='button-dbnames-refresh',
            className='btn btn-blue'
        ),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='chart-dbnames-dropdown',
                    clearable=False

                ),
            ], className='w-1/2'),
            html.Div([
                dcc.Dropdown(
                    id='chart-instruments-dropdown',
                    clearable=False
                ),
            ], className='w-1/2'),
        ], className='flex'),
        html.Div([
            html.Div([
                html.P('From'),
                dcc.Input(
                    id='askbid-input-date-from',
                    placeholder='2018-11-22 12:00',
                    type='text',
                    value='2018-11-22 12:00'
                )
            ]),
            html.Div([
                html.P('To'),
                dcc.Input(
                    id='askbid-input-date-to',
                    placeholder='2018-11-26 12:00',
                    type='text',
                    value='2018-11-26 12:00',
                )
            ]),
        ], className='flex space-x-2'),
        dcc.RadioItems(
            id='askbid-period',
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

    ],
        className='space-y-1')


def build_random():
    return html.Div([
        html.P('Random sintetic data generator', className='text-2xl font-bold'),
        html.Div([
            html.Div([
                html.P('Number of values', className='font-bold'),
                dcc.Input(
                    id='input-random-number',
                    className='w-40',
                    placeholder='1000',
                    type='text',
                    value='1000'
                )
            ]),
        ], className='flex flex-wrap space-x-2'),
        html.Div([
            html.Div([
                html.P('Dimensions', className='font-bold'),
                dcc.Input(
                    id='input-random-dim',
                    className='w-40',
                    placeholder='3',
                    type='text',
                    value='3'
                )
            ]),
        ], className='flex flex-wrap space-x-2'),
        html.Span('Instrument name', className='font-bold'),
        html.Div([
            dcc.Input(
                id='input-random-instrument-name',
                className='px-2',
                placeholder='random_',
                type='text',
                value='random_',
            ),
            html.Button(
                'Save values',
                id='button-random-save',
                className='btn btn-blue'
            ),
            html.P(id='button-random-label', className='w-24 font-mono font-bold text-gray-400'),
            dcc.Loading(
                id="loading-random",
                type="dot",
                children=html.Div(id="loading-random-output")
            ),
            dcc.Loading(
                id="loading-random-2",
                type="dot",
                children=html.Div(id="loading-random-output-2")
            ),
        ], className='flex space-x-2'),
        dcc.Graph(
            id='random-chart',
        )
    ], className='space-y-1')


def build_fourier():
    return html.Div([
        html.P('Fourier sintetic data generator', className='text-2xl font-bold'),
        html.Div([
            html.Div([
                html.P('Number of values', className='font-bold'),
                dcc.Input(
                    id='input-fourier-number',
                    className='w-40',
                    placeholder='1000',
                    type='text',
                    value='1000'
                )
            ]),
            html.Div([
                html.P('Delta', className='font-bold'),
                dcc.Input(
                    id='input-fourier-delta',
                    className='w-24',
                    placeholder='0.003',
                    type='text',
                    value='0.003'
                )
            ]),
            html.Div([
                html.P('Noise factor', className='font-bold'),
                dcc.Input(
                    id='input-fourier-noise-factor',
                    className='w-24',
                    placeholder='0.5',
                    type='text',
                    value='0.5'
                )
            ]),
        ],
            className='flex flex-wrap space-x-2',
        ),
        html.Div([
            html.P('An', className='font-bold'),
            dcc.Input(
                id='input-fourier-an',
                className='w-full',
                placeholder='8.3, -0.27, 0.075, -0.11, 0, -0.053, -0.13, -0.14658, 0, 0.082, 0.054',
                type='text',
                value='8.3, -0.27, 0.075, -0.11, 0, -0.053, -0.13, -0.14658, 0, 0.082, 0.054',
            )
        ]),
        html.Div([
            html.P('Bn', className='font-bold'),
            dcc.Input(
                id='input-fourier-bn',
                className='w-full',
                placeholder='0, -1.2, -1.75, 0.47, 0.45, 0.15, -0.58, 0.039, 0.063, -0.0059, -0.35',
                type='text',
                value='0, -1.2, -1.75, 0.47, 0.45, 0.15, -0.58, 0.039, 0.063, -0.0059, -0.35',
            )
        ]),
        html.Span('Instrument name', className='font-bold'),
        html.Div([
            dcc.Input(
                id='input-fourier-instrument-name',
                className='px-2',
                placeholder='fourier_01',
                type='text',
                value='fourier_01',
            ),
            html.Button(
                'Save values',
                id='button-fourier-save',
                className='btn btn-blue'
            ),
            html.P(id='button-fourier-label', className='w-24 font-mono font-bold text-gray-400'),
            dcc.Loading(
                id="loading-fourier-save",
                type="dot",
                children=html.Div(id="loading-fourier-output")
            ),
        ],
            className='flex space-x-2',
        ),
        dcc.Graph(
            id='fourier-chart',
        ),
    ], className='space-y-1')


def build_chaos_chart(axis):
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
                    html.Div(
                        className='box-wrapper',
                        children=html.Div(
                            className='box',
                            children=[
                                build_fourier()
                            ],
                        ),
                    ),
                    html.Div(
                        className='box-wrapper',
                        children=html.Div(
                            className='box',
                            children=[
                                build_random()
                            ],
                        ),
                    ),
                    html.Div(
                        className='box-wrapper',
                        children=html.Div(
                            className='box',
                            children=[
                                html.Div([
                                    dcc.Graph(
                                        figure=build_chaos_chart('xyz')
                                    ),
                                ], className='space-y-1'),
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
                ],
            ),
        ]
    )


@app.callback(
    [Output("chart-instruments-dropdown", "options"),
     Output("chart-instruments-dropdown", "value")],
    [Input('chart-dbnames-dropdown', 'value')]
)
def chart_instruments_refresh(dbname):
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
def button_DB_names_refresh(n_clicks):
    names = kragle.getDBNames()
    options = []
    for name in names:
        options.append({'label': name, 'value': name})
    return [options, 'forex_raw']


@app.callback(
    [Output("button-random-label", "children"),
     Output("loading-random-output-2", "children")],
    [Input('button-random-save', 'n_clicks')],
    [State('input-random-instrument-name', 'value')]
)
def button_random_save(n_clicks, instrument):
    if n_clicks is not None:
        kdb_tmp = kragle.KragleDB('kragle_sintetic')
        for i, df in enumerate(df_random_list):
            fetch_sintetic(kdb_tmp, instrument + str(i), df)
        return ['Saved {}'.format(n_clicks), '']
    return ['', '']


@app.callback(
    [Output("button-fourier-label", "children"),
     Output("loading-fourier-output", "children")],
    [Input('button-fourier-save', 'n_clicks')],
    [State('input-fourier-instrument-name', 'value')]
)
def button_fourier_save(n_clicks, instrument):
    if n_clicks is not None:
        kdb_tmp = kragle.KragleDB('kragle_sintetic')

        fetch_sintetic(kdb_tmp, instrument, df_fourier)
        return ['Saved {}'.format(n_clicks), '']
    return ['', '']


def fetch_sintetic(kdb, instrument, df):
    # delete old collection
    for period in kragle.periods:
        kdb.drop('{}.{}'.format(instrument, period))

    kdb.fetch_dataframe(df, instrument, 'm1', check_duplicates=False)
    # m5
    droplist = []
    for i in range(df.shape[0]):
        if i % 5 != 0:
            droplist.append(i)
    dfm5 = df.drop(droplist).reset_index(drop=True)
    kdb.fetch_dataframe(dfm5, instrument, 'm5', check_duplicates=False)
    # m15
    droplist = []
    for i in range(dfm5.shape[0]):
        if i % 3 != 0:
            droplist.append(i)
    dfm15 = dfm5.drop(droplist).reset_index(drop=True)
    kdb.fetch_dataframe(dfm15, instrument, 'm15', check_duplicates=False)
    # m30
    droplist = []
    for i in range(dfm15.shape[0]):
        if i % 2 != 0:
            droplist.append(i)
    dfm30 = dfm15.drop(droplist).reset_index(drop=True)
    kdb.fetch_dataframe(dfm30, instrument, 'm30', check_duplicates=False)
    # H1
    droplist = []
    for i in range(dfm30.shape[0]):
        if i % 2 != 0:
            droplist.append(i)
    dfH1 = dfm30.drop(droplist).reset_index(drop=True)
    kdb.fetch_dataframe(dfH1, instrument, 'H1', check_duplicates=False)
    kdb.close()


@app.callback(
    [Output('random-chart', 'figure'),
     Output('loading-random-output', 'children')],
    [Input('input-random-number', 'value'),
     Input('input-random-dim', 'value')
     ]
)
def random_chart_figure(number, dim):
    global df_random_list
    df_random_list = []
    number = int(float(number))
    dim = int(float(dim))
    ds_list = kragle.sintetic.random_dataset(n=number, dim=dim)
    fig = go.Figure()
    fig.update_layout(title="Random")
    for ds in ds_list:
        df_random = pd.DataFrame(ds)
        df_random_list.append(df_random)
        fig.add_trace(go.Scatter(x=df_random['n'], y=df_random['bidopen'], opacity=0.5))

    return [fig, '']


@app.callback(
    [Output('fourier-chart', 'figure')],
    [Input('input-fourier-number', 'value')
        , Input('input-fourier-delta', 'value')
        , Input('input-fourier-an', 'value')
        , Input('input-fourier-bn', 'value')
        , Input('input-fourier-noise-factor', 'value')
     ]
)
def fourier_chart_figure(number, delta, an_str, bn_str, noise_factor):
    global df_fourier
    try:
        an = list(map(float, an_str.split(',')))
    except:
        an = [1]
    try:
        bn = list(map(float, bn_str.split(',')))
    except:
        bn = [0]

    number = int(float(number))
    delta = float(delta)
    try:
        noise_factor = float(noise_factor)
    except:
        noise_factor = 1
    val = kragle.sintetic.fourier_dataset(n=number, delta=delta, an=an, bn=bn, noise_factor=noise_factor)
    df_fourier = pd.DataFrame(val)
    return [px.line(df_fourier, x="n", y='bidopen', title='Fourier')]


@app.callback(
    [Output('askbid-chart', 'figure')],
    [Input('askbid-input-date-from', 'value')
        , Input('askbid-input-date-to', 'value')
        , Input('chart-instruments-dropdown', 'value')
        , Input('askbid-period', 'value')]
)
def update_askbid_chart(start_date, end_date, instrument, period):
    df = pd.DataFrame({'date': [], 'bidopen': [], 'tickqty': []})
    try:
        start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        df = kdb.get_instrument(instrument, period, start, end)
    except:
        pass
    if df.shape[0] == 0:
        df = pd.DataFrame({'date': [], 'bidopen': [], 'tickqty': []})
    ########################

    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["bidopen"], name="bidopen"),
        secondary_y=False,
    )
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["tickqty"], name="tickqty", opacity=0.3),
        secondary_y=True,
    )
    return [fig1]


app.layout = render_content()

if __name__ == '__main__':
    app.run_server(debug=True)