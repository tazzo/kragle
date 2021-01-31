import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots

import kragle
import kragle.utils as kutils
import kragle.synthetic
from app_layout import *
from kragle.db import *
from kragle.strategy import AgentTester, DeviationStrategy

df_fourier = None
df_random_list = []
dataset = None
kdb = KragleDB('forex_raw')
kdb_agent = KragleDB('forex_raw')


def render_dashboard_page():
    return dbc.Container(
        className='p-3', fluid=True,
        children=[
            dbc.Row(
                children=[
                    dbc.Col(
                        className=class_col, lg=6, xl=4,
                        children=html.Div(
                            className=class_box,
                            children=[
                                build_agent_box()
                            ],
                        ),
                    ),
                    dbc.Col(
                        className=class_col, lg=6, xl=4,
                        children=html.Div(
                            className=class_box,
                            children=[
                                build_dataset_manager()
                            ],
                        ),
                    ),
                    dbc.Col(
                        className=class_col, lg=6, xl=4,
                        children=html.Div(
                            className=class_box,
                            children=build_explorer(),
                        ),
                    ),
                    dbc.Col(
                        className=class_col, lg=6, xl=4,
                        children=html.Div(
                            className=class_box,
                            children=[
                                build_fourier()
                            ],
                        ),
                    ),
                    dbc.Col(
                        className=class_col, lg=6, xl=4,
                        children=html.Div(
                            className=class_box,
                            children=[
                                build_random()
                            ],
                        ),
                    ),
                    dbc.Col(
                        className=class_col, lg=6, xl=4,
                        children=html.Div(
                            className=class_box,
                            children=[
                                html.Div([
                                    dcc.Graph(
                                        figure=build_chaos_chart('xyz')
                                    ),
                                ], className='space-y-1'),
                            ],
                        ),
                    ),
                ],
            ),
        ]
    )


def build_agent_box():
    return html.Div([
        html.H1('Agent Tester'),
        dbc.Row([
            dbc.Col([
                html.Button(
                    'Refresh DB names',
                    id='button-agent-dbnames-refresh',
                    className='btn btn-primary mr-3'
                ),
                html.Button(
                    'Run',
                    id='button-agent-run',
                    className='btn btn-primary'
                ),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='agent-dbnames-dropdown',
                    clearable=False

                ),
            ], width=6),
            dbc.Col([
                dcc.Dropdown(
                    id='agent-instruments-dropdown',
                    clearable=False
                ),
            ], width=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.P('From', className='font-weight-bold'),
                dcc.Input(
                    id='agent-input-date-from',
                    placeholder='2018-11-22 12:00',
                    type='text',
                    value='2018-11-22 12:00'
                )
            ]),
            dbc.Col([
                html.P('To', className='font-weight-bold'),
                dcc.Input(
                    id='agent-input-date-to',
                    placeholder='2018-11-22 22:00',
                    type='text',
                    value='2018-11-22 22:00',
                )
            ]),
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='agent-chart'
                )
            ]),
        ]),

    ], )


def build_dataset_manager():
    return html.Div([
        html.H1('Datasets manager'),
        html.Button(
            'Refresh',
            id='button-manager-refresh',
            className='btn btn-primary'
        ),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='dataset-manager-instruments-dropdown',
                    clearable=False
                ),
            ], width=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.P('From', className='font-weight-bold'),
                dcc.Input(
                    id='dataset-manager-input-date-from',
                    placeholder='2018-11-22 12:00',
                    type='text',
                    value='2018-11-22 12:00'
                )
            ]),
            dbc.Col([
                html.P('To', className='font-weight-bold'),
                dcc.Input(
                    id='dataset-manager-input-date-to',
                    placeholder='2018-11-26 12:00',
                    type='text',
                    value='2018-11-26 12:00',
                )
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.RadioItems(
                    id='dataset-manager-period',
                    options=[
                        {'label': 'm1 ', 'value': 'm1'},
                        {'label': 'm5 ', 'value': 'm5'},
                        {'label': 'm15 ', 'value': 'm15'},
                        {'label': 'H1 ', 'value': 'H1'},
                    ],
                    value='m1',
                    labelStyle={'display': 'inline-block'},
                    inputClassName="mx-2"
                ),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='dataset-manager-chart'
                )
            ]),
        ]),

    ], )


def build_explorer():
    return html.Div([
        html.H1('Data explorer'),
        html.Button(
            'Refresh DB names',
            id='button-explorer-dbnames-refresh',
            className='btn btn-primary'
        ),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='chart-dbnames-dropdown',
                    clearable=False
                ),
            ]),
            dbc.Col([
                dcc.Dropdown(
                    id='chart-instruments-dropdown',
                    clearable=False
                ),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.P('From', className='font-weight-bold'),
                dcc.Input(
                    id='explore-input-date-from',
                    placeholder='2018-11-22 12:00',
                    type='text',
                    value='2018-11-22 12:00'
                )
            ]),
            dbc.Col([
                html.P('To', className='font-weight-bold'),
                dcc.Input(
                    id='explore-input-date-to',
                    placeholder='2018-11-26 12:00',
                    type='text',
                    value='2018-11-26 12:00',
                )
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.RadioItems(
                    id='explore-period',
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
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.P('Distance', className='font-weight-bold'),
                dcc.Input(
                    id='distance-insert-future',
                    placeholder='60',
                    type='text',
                    value='60'
                ),
            ]),
            dbc.Col([
                html.P('Window', className='font-weight-bold'),
                dcc.Input(
                    id='window-insert-future',
                    placeholder='10',
                    type='text',
                    value='10'
                ),
            ]),
        ], className='flex space-x-2'),
        dbc.Row([
            dbc.Col([
                html.Button(
                    'Insert Future',
                    id='button-insert-future',
                    className='btn btn-outline-primary'
                ),
                dcc.Loading(
                    id="loading-future",
                    type="dot",
                    children=html.Div(id="loading-future-output")
                ),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.P('Number', className='font-weight-bold'),
                dcc.Input(
                    id='number-create-dataset',
                    placeholder='10',
                    type='text',
                    value='10'
                ),
            ]),
            dbc.Col([
                html.P('History length', className='font-weight-bold'),
                dcc.Input(
                    id='history_len-create-dataset',
                    placeholder='4',
                    type='text',
                    value='4'
                ),
            ]),
        ]),
        html.Button(
            'Create dataset',
            id='button-create-dataset',
            className='btn btn-primary'
        ), html.P(id='label-create-dataset'),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='explore-chart'
                )
            ]),
        ]),
    ], )


def build_fourier():
    return html.Div([
        html.H1('Fourier synthetic data generator'),
        dbc.Row([
            dbc.Col([
                html.P('Number of values', className='font-weight-bold'),
                dcc.Input(
                    id='input-fourier-number',
                    placeholder='1000',
                    type='text',
                    value='1000'
                )
            ], width='auto'),
            dbc.Col([
                html.P('Delta', className='font-weight-bold'),
                dcc.Input(
                    id='input-fourier-delta',
                    placeholder='0.003',
                    type='text',
                    value='0.003'
                )
            ], width='auto'),
            dbc.Col([
                html.P('Noise factor', className='font-weight-bold'),
                dcc.Input(
                    id='input-fourier-noise-factor',
                    placeholder='0.5',
                    type='text',
                    value='0.5'
                )
            ], width='auto'),
        ]),
        dbc.Row([
            dbc.Col([
                html.P('An', className='font-weight-bold'),
                dcc.Input(
                    id='input-fourier-an',
                    placeholder='8.3, -0.27, 0.075, -0.11, 0, -0.053, -0.13, -0.14658, 0, 0.082, 0.054',
                    type='text',
                    value='8.3, -0.27, 0.075, -0.11, 0, -0.053, -0.13, -0.14658, 0, 0.082, 0.054',
                    className='w-100',
                )
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col([
                html.P('Bn', className='font-weight-bold'),
                dcc.Input(
                    id='input-fourier-bn',
                    placeholder='0, -1.2, -1.75, 0.47, 0.45, 0.15, -0.58, 0.039, 0.063, -0.0059, -0.35',
                    type='text',
                    value='0, -1.2, -1.75, 0.47, 0.45, 0.15, -0.58, 0.039, 0.063, -0.0059, -0.35',
                    className='w-100',
                )
            ]),
        ]),
        html.Span('Instrument name', className='font-weight-bold'),
        dbc.Row([
            dbc.Col([
                dcc.Input(
                    id='input-fourier-instrument-name',
                    placeholder='fourier_01',
                    type='text',
                    value='fourier_01',
                ),
                html.Button(
                    'Save values',
                    id='button-fourier-save',
                    className='btn btn-primary'
                ),
                html.P(id='button-fourier-label'),
                dcc.Loading(
                    id="loading-fourier-save",
                    type="dot",
                    children=html.Div(id="loading-fourier-output")
                ),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='fourier-chart',
                ),
            ]),
        ]),
    ], className='space-y-1')


def build_random():
    return html.Div([
        html.H1('Random synthetic data generator'),
        dbc.Row([
            dbc.Col([
                html.P('Number of values', className='font-weight-bold'),
                dcc.Input(
                    id='input-random-number',
                    placeholder='1000',
                    type='text',
                    value='1000'
                )
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.P('Dimensions', className='font-weight-bold'),
                dcc.Input(
                    id='input-random-dim',
                    placeholder='3',
                    type='text',
                    value='3'
                )
            ]),
        ]),
        html.Span('Instrument name', className='font-weight-bold'),
        dbc.Row([
            dbc.Col([
                dcc.Input(
                    id='input-random-instrument-name',
                    placeholder='random_',
                    type='text',
                    value='random_',
                ),
                html.Button(
                    'Save values',
                    id='button-random-save',
                    className='btn btn-primary'
                ),
                html.P(id='button-random-label'),
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
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='random-chart',
                )
            ]),
        ]),
    ], className='space-y-1')


def build_chaos_chart(axis):
    dftmp = pd.DataFrame(kragle.synthetic.attractor(20000, 0.01))
    return px.line(dftmp, x="i", y=axis, title='Attractor ')


@app.callback(
    [Output("agent-instruments-dropdown", "options"),
     Output("agent-instruments-dropdown", "value")],
    [Input('agent-dbnames-dropdown', 'value')]
)
def agent_instruments_refresh(dbname):
    global kdb_agent
    kdb_agent.close()
    kdb_agent = KragleDB(dbname)
    insrtuments = kdb_agent.get_instruments()
    options = []
    for insrtument in insrtuments:
        options.append({'label': insrtument, 'value': insrtument})
    return [options, 'EUR/USD']


@app.callback(
    [Output("agent-dbnames-dropdown", "options"),
     Output("agent-dbnames-dropdown", "value")],
    [Input('button-agent-dbnames-refresh', 'n_clicks')]
)
def button_agent_DB_names_refresh(n_clicks):
    names = kragle.db.get_db_names()
    options = []
    for name in names:
        options.append({'label': name, 'value': name})
    return [options, 'forex_raw']


@app.callback(
    [Output("agent-chart", "figure"), ],
    [Input('button-agent-run', 'n_clicks')],
    [State('agent-input-date-from', 'value'),
     State('agent-input-date-to', 'value'),
     State("agent-instruments-dropdown", "value")]
)
def button_agent_run(n_clicks, date_start, date_end, instrument):
    if n_clicks is not None:
        try:
            date_start = dt.datetime.strptime(date_start, '%Y-%m-%d %H:%M')
            date_end = dt.datetime.strptime(date_end, '%Y-%m-%d %H:%M')
        except:
            return [go.Figure()]

        at = AgentTester(kdb_agent, DeviationStrategy())
        at.test_strategy(instrument, date_start, date_end)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.update_layout(title="Agent")
        # bidopen chart
        fig.add_trace(
            go.Scatter(
                x=at.df['date'],
                y=at.df['bidopen'],
                opacity=0.5,
                name='bidopen',
                mode='lines+markers',
                marker={'size': at.df['size'].tolist(),
                        'color': at.df['color']}
            ),
            secondary_y=False)
        # wallet
        fig.add_trace(
            go.Scatter(
                x=at.df['date'],
                y=at.df['wallet'],
                opacity=0.5,
                name='wallet'),
            secondary_y=True)
        return [fig]
    return [go.Figure()]


@app.callback(
    [Output("dataset-manager-chart", "figure"), ],
    [Input('button-manager-refresh', 'n_clicks')]
)
def button_manager_refresh(n_clicks):
    if n_clicks is not None:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.update_layout(title="Dataset")
        df_dict = kragle.utils.dataset_to_dataframe_dict(dataset[0])
        for name, df in df_dict.items():
            fig.add_trace(
                go.Scatter(
                    x=df_dict[name]['date'],
                    y=df_dict[name]['value'],
                    opacity=0.5,
                    name=name),
                secondary_y=(name == 'tickqty'))
        return [fig]
    return [go.Figure()]


@app.callback(
    [Output("chart-instruments-dropdown", "options"),
     Output("chart-instruments-dropdown", "value")],
    [Input('chart-dbnames-dropdown', 'value')]
)
def chart_instruments_refresh(dbname):
    global kdb
    kdb.close()
    kdb = KragleDB(dbname)
    insrtuments = kdb.get_instruments()
    options = []
    for insrtument in insrtuments:
        options.append({'label': insrtument, 'value': insrtument})
    return [options, insrtuments[0]]


@app.callback(
    [Output("chart-dbnames-dropdown", "options"),
     Output("chart-dbnames-dropdown", "value")],
    [Input('button-explorer-dbnames-refresh', 'n_clicks')]
)
def button_chart_DB_names_refresh(n_clicks):
    names = kragle.db.get_db_names()
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
        kdb_tmp = KragleDB('kragle_synthetic')
        for i, df in enumerate(df_random_list):
            fetch_synthetic(kdb_tmp, instrument + str(i), df)
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
        kdb_tmp = KragleDB('kragle_synthetic')

        fetch_synthetic(kdb_tmp, instrument, df_fourier)
        return ['Saved {}'.format(n_clicks), '']

    return ['', '']


def fetch_synthetic(kdb, instrument, df):
    # delete old collection
    for period in kutils.periods:
        kdb.drop('{}.{}'.format(instrument, period))

    kdb.fetch_dataframe(df, instrument, 'm1')
    # m5
    droplist = []
    for i in range(df.shape[0]):
        if i % 5 != 0:
            droplist.append(i)
    dfm5 = df.drop(droplist).reset_index(drop=True)
    kdb.fetch_dataframe(dfm5, instrument, 'm5')
    # m15
    droplist = []
    for i in range(dfm5.shape[0]):
        if i % 3 != 0:
            droplist.append(i)
    dfm15 = dfm5.drop(droplist).reset_index(drop=True)
    kdb.fetch_dataframe(dfm15, instrument, 'm15')
    # m30
    droplist = []
    for i in range(dfm15.shape[0]):
        if i % 2 != 0:
            droplist.append(i)
    dfm30 = dfm15.drop(droplist).reset_index(drop=True)
    kdb.fetch_dataframe(dfm30, instrument, 'm30')
    # H1
    droplist = []
    for i in range(dfm30.shape[0]):
        if i % 2 != 0:
            droplist.append(i)
    dfH1 = dfm30.drop(droplist).reset_index(drop=True)
    kdb.fetch_dataframe(dfH1, instrument, 'H1')
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
    ds_list = kragle.synthetic.random_dataset(n=number, dim=dim)
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
    val = kragle.synthetic.fourier_dataset(n=number, delta=delta, an=an, bn=bn, noise_factor=noise_factor)
    df_fourier = pd.DataFrame(val)
    return [px.line(df_fourier, x="n", y='bidopen', title='Fourier')]


@app.callback(
    [Output("loading-future-output", "children")],
    [Input('button-insert-future', 'n_clicks')],
    [State('explore-input-date-from', 'value')
        , State('explore-input-date-to', 'value')
        , State('chart-instruments-dropdown', 'value')
        , State('explore-period', 'value')
        , State('distance-insert-future', 'value')
        , State('window-insert-future', 'value')
     ]
)
def button_insert_future(n_clicks, date_start, date_end, instrument, period, distance, window):
    try:
        date_start = dt.datetime.strptime(date_start, '%Y-%m-%d %H:%M')
        date_end = dt.datetime.strptime(date_end, '%Y-%m-%d %H:%M')
    except:
        return ['']
    kdb.insert_future(instrument, period, date_start, date_end, distance, window)
    return ['']


@app.callback(
    [Output('label-create-dataset', 'children')],
    [Input('button-create-dataset', 'n_clicks')],
    [State('chart-instruments-dropdown', 'value'),
     State('number-create-dataset', 'value'),
     State('history_len-create-dataset', 'value'),
     State('explore-input-date-from', 'value'),
     State('explore-input-date-to', 'value'), ]
)
def button_create_dataset(n_clicks, instrument, nval, history_len, date_start, date_end):
    global dataset
    if n_clicks is not None:
        try:
            nval = int(float(nval))
            history_len = int(float(history_len))
            date_start = dt.datetime.strptime(date_start, '%Y-%m-%d %H:%M')
            date_end = dt.datetime.strptime(date_end, '%Y-%m-%d %H:%M')
        except:
            return ['']
        dataset = kdb.create_dataset(nval, instrument, ['m1', 'm5', 'm15', 'H1'], history_len, date_start, date_end)

        return ['instr:{} nval:{} history length:{}'.format(instrument, nval, history_len)]
    return ['']


@app.callback(
    [Output('explore-chart', 'figure')],
    [Input('explore-input-date-from', 'value')
        , Input('explore-input-date-to', 'value')
        , Input('chart-instruments-dropdown', 'value')
        , Input('explore-period', 'value')]
)
def update_explore_chart(start_date, end_date, instrument, period):
    df = pd.DataFrame({})
    try:
        start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        df = kdb.get_instrument(instrument, period, start, end)
    except:
        pass
    if df.shape[0] == 0:
        df = pd.DataFrame({'date': [], 'bidopen': [], 'tickqty': [], 'future': []})
    ########################

    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["bidopen"], name="bidopen"),
        secondary_y=False,
    )
    if 'future' in df.columns:
        fig1.add_trace(
            go.Scatter(x=df["date"], y=df["future"], name="future", opacity=0.3),
            secondary_y=False,
        )
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["tickqty"], name="tickqty", opacity=0.3),
        secondary_y=True,
    )
    return [fig1]
