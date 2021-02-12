import dash_html_components as html1
import plotly.graph_objects as go

import pandas as pd

import kragle.trader
import kragle.utils
from app_layout import *
from kragle.utils import table_from_dataframe

import logging

logger = logging.getLogger('kragle')
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
                    html.H3('FXCM Trader', className="font-weight-bold "),
                    lg=3, sm=5, xs=6
                ),

                dbc.Col(
                    dbc.Button("Connect", id="connect-button", className="ml-1 shadow", color='primary'), width=5, sm=4, md=3, lg=2, xl=1,),
                dbc.Col(
                    dcc.Loading(
                        id="loading-connection",
                        type="dot",
                        children=html.Div(id="loading-connection-output", className='mt-3')
                    ), width=1
                ),


            ], justify="start"),
            dbc.Row([
                dbc.Col(
                    dcc.Interval(
                        id='interval-subscription',
                        interval=1 * 1000,  # in milliseconds
                        n_intervals=0
                    )
                )
            ], )
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    html.Div(render_tabs()),
                    width=12
                ),
            ]),
        ])
    ], className=class_card + 'h-100', )


# open_trade(symbol, is_buy, amount, time_in_force, order_type, rate=0, is_in_pips=True, limit=None, at_market=0, stop=None, trailing_step=None, account_id=None)
def build_order_card():
    return dbc.Card([
        dbc.CardHeader(html.H4('Order', className="font-weight-bold")),
        dbc.CardBody([
            dbc.Form([
                dbc.FormGroup(
                    [
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Symbol"),
                            ], width=12),
                            dbc.Col([
                                dbc.Label("Is buy"),
                            ], width=12),
                            dbc.Col([
                                html.H6("Order type"),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Buy", "value": 'buy'},
                                        {"label": "Sell", "value": 'sell'},
                                    ],
                                    value='buy',
                                    id="order-type-input",
                                    inline=True,
                                ),
                            ], width=12, className='border'),
                            dbc.Col([
                                dbc.Label("Amount"),
                            ], width=12),
                            dbc.Col([
                                dbc.Label("Time in force"),
                            ], width=12),
                            dbc.Col([
                                dbc.Label("Order type"),
                            ], width=12),
                            dbc.Col([
                                dbc.Label("Rate"),
                            ], width=12),
                            dbc.Col([
                                dbc.Label("Is in pips"),
                            ], width=12),
                            dbc.Col([
                                dbc.Label("Limit"),
                            ], width=12),
                            dbc.Col([
                                dbc.Label("At market"),
                            ], width=12),
                            dbc.Col([
                                dbc.Label("Stop"),
                            ], width=12),
                            dbc.Col([
                                dbc.Label("Trailing step"),
                            ], width=12),
                            dbc.Col([
                                dbc.Label("Account id"),
                            ], width=12),
                        ])
                    ]),
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
                            dbc.InputGroupAddon("number", addon_type="prepend"),
                            dbc.Input(placeholder="100", type="number", id="chart-n-input", value='100'),
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


def get_battery(n):
    battery_loop = ['fas fa-battery-empty', 'fas fa-battery-quarter', 'fas fa-battery-half',
                    'fas fa-battery-three-quarters', 'fas fa-battery-full', ]
    return battery_loop[n % 5]


@app.callback([Output('chart-live', 'children'),
               Output('chart-footer', 'children')],
              Input('chart-live-interval', 'n_intervals'),
              [State('chart-period-input', 'value'),
               State('chart-n-input', 'value')]
              )
def update_chart_live(n, period, n_candles):
    if trader is not None:
        global battery
        nn = 100
        try:
            nn = int(n_candles)
        except:
            pass
        logger.info('Chart live period:[{}] number of candles:[{}]'.format(period, n_candles))
        trader.candles_number = nn
        trader.candles_period = period
        return [build_candle_chart(), html.I(className=get_battery(n))]
    else:
        return ['', html.I(className=get_battery(n))]


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
