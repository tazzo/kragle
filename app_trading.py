import dash_html_components as html1
import dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go

import pandas as pd

import kragle.trader
import kragle.utils
from app_layout import *

trader = None


def render_trading_page():
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col(build_trader_box(), className=class_col, width=12),
            ]),
            dbc.Row([
                dbc.Col(build_chart_card(), className=class_col, md=6, xl=4),
                dbc.Col(build_order_card(), className=class_col, md=6, xl=4),
                dbc.Col(build_counter_card(), className=class_col, md=6, xl=4),
            ]),
        ],
        className='p-3', fluid=True
    )


def render_tabs():
    return dbc.Tabs(
        [
            dbc.Tab('tab_accounts', label="Accounts", id='tab_accounts'),
            dbc.Tab('tab_accounts_summary', label="Accounts summary", id='tab_accounts_summary'),
            dbc.Tab('tab_open_positions', label="Open positions", id='tab_open_positions'),
            dbc.Tab('tab_open_positions_summary', label="Open positions_summary", id='tab_open_positions_summary'),
            dbc.Tab('tab_closed_positions', label="Closed positions", id='tab_closed_positions'),
            dbc.Tab('tab_closed_positions_summary', label="Closed positions summary",
                    id='tab_closed_positions_summary'),
            dbc.Tab('tab_orders', label="Orders", id='tab_orders'),
            dbc.Tab('tab_summary', label="Summary", id='tab_summary'),
            dbc.Tab('tab_offers', label="Offers", id='tab_offers'),

        ]
    )


def build_trader_box():
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col(
                    html.H2('FXCM Trader', className="font-weight-bold"),
                    lg=3, sm=4, xs=6
                ),
                dbc.Col(
                    html1.Div(dbc.Button("Connect", id="connect-button", className="ml-1", color='primary'),
                              id='connection-div')
                ),
                dbc.Col(
                    dcc.Loading(
                        id="loading-connection",
                        type="dot",
                        children=html.Div(id="loading-connection-output", className='mt-3')
                    ),
                ),
                dbc.Col(
                    dcc.Interval(
                        id='interval-subscription',
                        interval=1 * 1000,  # in milliseconds
                        n_intervals=0
                    ), lg=7, sm=5
                ),
            ], justify="start"),
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    html.Div(render_tabs()),
                    width=12
                ),
            ]),
        ])
    ], className='shadow-1-strong rounded mb-3 h-100', )


def build_order_card():
    return dbc.Card([
        dbc.CardHeader(html.H4('Order', className="font-weight-bold")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    dbc.Form([
                        dbc.FormGroup(
                            [
                                dbc.Label("Order type"),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Buy", "value": 'buy'},
                                        {"label": "Sell", "value": 'sell'},
                                    ],
                                    value='buy',
                                    id="order-type-input",
                                    inline=True,
                                ),
                            ],
                            className="mx-3",
                        ),
                    ])
                ),
            ]),
        ]),
        dcc.Interval(
            id='order-interval',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        ),
        dbc.CardFooter(['Footer', html.Div(id='order-footer')])
    ], className=class_card, outline=True)


def build_chart_card():
    return dbc.Card([
        dbc.CardHeader(html.H4('Chart', className="font-weight-bold")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon("periods", addon_type="prepend"),
                            dbc.Select(
                                options=[{"label": v, "value": v} for v in kragle.utils.periods],
                                value='m1',
                                id="chart-period-input",
                            ),
                        ],
                        className="mb-3",
                    ),
                ),
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon("hours", addon_type="prepend"),
                            dbc.Input(placeholder="1", type="number"),
                        ],
                        className="mb-3",
                    ),
                ),
            ]),
            dbc.Row([
                dbc.Col(
                    html.Div(id='chart-live')
                ),
            ]),
        ]),
        dcc.Interval(
            id='chart-live-interval',
            interval=2 * 1000,  # in milliseconds
            n_intervals=0
        ),
        dbc.CardFooter(['Footer', html.Div(id='chart-footer')])
    ], className=class_card, outline=True)


def build_counter_card():
    return dbc.Card([
        dbc.CardHeader("Counter"),
        dbc.CardBody(id='interval-counter-div')],
        className=class_card, outline=True
    )


@app.callback(
    [Output("connect-button", "children"),
     Output("loading-connection-output", "children")],
    [Input("connect-button", "n_clicks")]
)
def on_connection_button_click(n_connect):
    ctx = dash.callback_context
    global trader

    if not ctx.triggered:
        if trader is None:
            return ['Connect', '']
        else:
            return ['Disconnect', '']

    elif trader is not None:
        print('Closing ... ')
        trader.close()
        print('Closed ... ')
        trader = None
        return ['Connect', '']
    else:
        try:
            print('Connecting ... ')
            trader = kragle.trader.FxcmTrader()
            print('Connected!')
        except Exception as e:
            print(e)
        return ['Disconnect', '']


@app.callback([Output('chart-live', 'children'),
               Output('chart-footer', 'children')],
              Input('chart-live-interval', 'n_intervals')
              )
def update_chart_live(n):
    if trader is not None:
        return [build_candle_chart(), n]
    else:
        return ['', n]


@app.callback([Output('tab_accounts', 'children'),
               Output('tab_accounts_summary', 'children'),
               Output('tab_open_positions', 'children'),
               Output('tab_open_positions_summary', 'children'),
               Output('tab_closed_positions', 'children'),
               Output('tab_closed_positions_summary', 'children'),
               Output('tab_orders', 'children'),
               Output('tab_summary', 'children'),
               Output('tab_offers', 'children'),
               Output('interval-counter-div', 'children')],
              Input('interval-subscription', 'n_intervals')
              )
def update_subscription(n):
    if trader is not None:
        r1 = table_from_dataframe(trader.accounts)
        r2 = table_from_dataframe(trader.accounts_summary)
        r3 = table_from_dataframe(trader.open_positions)
        r4 = table_from_dataframe(trader.open_positions_summary)
        r5 = table_from_dataframe(trader.closed_positions)
        r6 = table_from_dataframe(trader.closed_positions_summary)
        r7 = table_from_dataframe(trader.orders)
        r8 = table_from_dataframe(trader.summary)
        t = table_from_dataframe(trader.offers)
        r9 = table_from_dataframe(trader.offers)

        return [r1, r2, r3, r4, r5, r6, r7, r8, r9, n]
    else:
        tmp = table_from_dataframe(pd.DataFrame())
        return [tmp, tmp, tmp, tmp, tmp, tmp, tmp, tmp, tmp, n]


def build_candle_chart():
    fig = go.Figure(go.Candlestick(
        x=trader.candles.index,
        open=trader.candles['bidopen'],
        high=trader.candles['bidhigh'],
        low=trader.candles['bidlow'],
        close=trader.candles['bidclose']
    ))
    return dcc.Graph(figure=fig)


def table_from_dataframe(df):
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        style_table={'height': '200px', 'overflowY': 'auto'}

    )
