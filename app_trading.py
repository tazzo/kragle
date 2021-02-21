import plotly.graph_objects as go

import pandas as pd

import kragle.trader
import kragle.utils
from app_layout import *
from kragle.utils import table_from_dataframe

import logging

from kragle.utils import get_fired_input_id

logger = logging.getLogger('kragle')
trader = None


def render_trading_page():
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col(build_trader_box(), className=class_col + ' mb-3', width=12),
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
                    dbc.Button("Connect", id="connect-button", className="ml-1 ", color='primary'), width=5, sm=4,
                    md=3, lg=2, xl=1, ),
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
        ], ),
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
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup(
                            [
                                dbc.Label("Instrument", size='sm'),
                                dbc.Select(
                                    options=[{"label": v, "value": v} for v in kragle.utils.instruments],
                                    value='EUR/USD',
                                    id="order-instrument-input",
                                    disabled=True,
                                ),
                            ],
                            className="mb-3 w-50",
                        ),
                    ], width=12),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dbc.FormGroup(
                                    [
                                        dbc.Label("Amount €", size='sm'),
                                        dbc.Input(
                                            value=1,
                                            type="number",
                                            id="order-amount-input",
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                            ], width=6, ),
                            dbc.Col([
                                dbc.FormGroup(
                                    [
                                        dbc.Label("Buy/Sell", size='sm'),
                                        dbc.RadioItems(
                                            options=[
                                                {"label": "Buy", "value": True},
                                                {"label": "Sell", "value": False},
                                            ],
                                            value=True,
                                            id="order-isbuy-input",
                                            inline=True,
                                        ),
                                    ]
                                )

                            ], width=6, ),
                        ], className='border mb-2 shadow-sm'),
                    ], width=12),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dbc.FormGroup(
                                    [
                                        dbc.Label("Time in force"),  # .
                                        dbc.Select(
                                            options=[{"label": v, "value": v} for v in kragle.utils.time_in_force],
                                            value='GTC',
                                            id="order-timeinforce-input",
                                            disabled=True,
                                        ),
                                    ],
                                    className="mb-3 w-50",
                                ),
                            ], width=6),
                            dbc.Col([
                                dbc.FormGroup(
                                    [
                                        dbc.Label("Order type"),
                                        dbc.RadioItems(
                                            options=[
                                                {"label": "AtMarket", "value": "AtMarket"},
                                                {"label": "MarketRange", "value": "MarketRange", 'disabled': True},
                                            ],
                                            value="AtMarket",
                                            id="order-type-input",
                                            inline=True,
                                        ),
                                    ]
                                )
                            ], width=6),
                        ], className='border mb-2 shadow-sm'),
                    ], width=12),
                    dbc.Col([
                        dbc.FormGroup(
                            [
                                dbc.Label("Rate"),
                                dbc.Input(
                                    value=0,
                                    type="number",
                                    id="order-rate-input",
                                    disabled=True
                                ),
                            ],
                            className="mb-3",
                        ),
                    ], width=6, ),
                    dbc.Col([
                        dbc.FormGroup(
                            [
                                dbc.Label("Is in pips"),
                                dbc.Checklist(
                                    options=[
                                        {"label": "", "value": True, 'disabled': True},
                                    ],
                                    value=[True],
                                    id="order-isinpips-input",
                                    inline=True,
                                    switch=True,

                                ),
                            ]
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dbc.FormGroup(
                                    [
                                        dbc.Label("Limit"),
                                        dbc.Input(
                                            value=15,
                                            type="number",
                                            id="order-limit-input",
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                            ], width=6),
                            dbc.Col([
                                dbc.FormGroup(
                                    [
                                        dbc.Label("Stop"),
                                        dbc.Input(
                                            value=-15,
                                            type="number",
                                            id="order-stop-input",
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                            ], width=6),
                        ], className='border mb-2 shadow-sm'),
                    ], width=12),
                    dbc.Col([
                        dbc.FormGroup(
                            [
                                dbc.Label("At market"),
                                dbc.Input(
                                    value=0,
                                    type="number",
                                    id="order-atmarket-input",
                                    disabled=True
                                ),
                            ],
                            className="mb-3",
                        ),
                    ], width=6),
                    dbc.Col([
                        dbc.FormGroup(
                            [
                                dbc.Label("Trailing step"),
                                dbc.Input(
                                    value=None,
                                    id="order-trailingstep-input",
                                    disabled=True
                                ),
                            ],
                            className="mb-3",
                        ),
                    ], width=6),
                    dbc.Col([
                        dbc.FormGroup(
                            [
                                dbc.Label("Account id"),
                                dbc.Input(
                                    value='TO DO',
                                    id="order-account-input",
                                    disabled=True
                                ),
                            ],
                            className="mb-3",
                        ),
                    ], width=12),
                    dbc.Col([
                        dbc.Button("Open trade", id="order-open-trade-button", className="ml-1 ", color='danger'),
                        dbc.Popover(
                            [
                                dbc.PopoverHeader(["r u sure ?"]),
                                dbc.PopoverBody([
                                    dbc.Button('Cancel', id="order-open-trade-cancel-button", color='light',
                                               className='ml-2', ),
                                    dbc.Button("Confirm", id="order-open-trade-confirm-button", className="ml-1 ",
                                               color='danger'),
                                ]),
                            ],
                            id="order-popover",
                            is_open=False,
                            target="order-open-trade-button",
                        ),
                    ], width=12)
                ])
            ]),
        ]),
        dcc.Interval(
            id='order-interval',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        ),
        dbc.CardFooter([html.Div(id='order-footer')])
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
                        className="mb-3 shadow-sm",
                    ),
                ),
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon("number", addon_type="prepend"),
                            dbc.Input(placeholder="100", type="number", id="chart-n-input", value='100'),
                        ],
                        className="mb-3 shadow-sm",
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
        dbc.CardFooter([html.Div(id='chart-footer')])
    ], className=class_card, outline=True)


def build_counter_card():
    return dbc.Card([
        dbc.CardHeader("Counter"),
        dbc.CardBody(id='interval-counter-div')],
        className=class_card, outline=True
    )


@app.callback(
    [Output("order-footer", "children"),
     Output("order-popover", "is_open"), ],
    [Input("order-open-trade-button", "n_clicks"),
     Input("order-open-trade-cancel-button", "n_clicks"),
     Input("order-open-trade-confirm-button", "n_clicks"),
     Input("order-instrument-input", "value"),
     Input("order-amount-input", "value"),
     Input("order-isbuy-input", "value"),
     Input("order-isinpips-input", "value"),
     Input("order-stop-input", "value"),
     Input("order-limit-input", "value"),
     Input("order-rate-input", "value"),
     Input("order-type-input", "value"),
     Input("order-timeinforce-input", "value"), ],
    [State("order-popover", "is_open")]
)
def on_order_change(n, n_cancel, n_confirm, instrument, amount, isbuy, isinpips, stop, limit, rate, type, timeinforce,
                    is_open):
    ctx = dash.callback_context
    if n is None: n = 0
    if not ctx.triggered:
        return [html.I(className=get_battery(0)), is_open]
    else:
        button_id = get_fired_input_id(ctx)
        logger.info(
            'Open trade n:{} instrument:{} amount:{} isbuy:{} isinpips:{} stop:{} limit:{} rate:{} type:{} timeinforce:{} '
                .format(n, instrument, amount, isbuy, isinpips, stop, limit, rate, type, timeinforce))
        if button_id == 'order-open-trade-button':
            logger.info('Open trade button ')
            return [html.I(className=get_battery(n)), True]
        elif button_id == 'order-open-trade-cancel-button':
            logger.info('Open trade cancelled ')
            return [html.I(className=get_battery(n)), False]
        elif button_id == 'order-open-trade-confirm-button':
            logger.info('Open trade confirmed ')
            if trader is not None:
                try:
                    trader.con.open_trade(symbol=instrument, is_buy=isbuy, is_in_pips=isinpips[0],
                                          amount=amount, time_in_force=timeinforce,
                                          order_type=type, limit=limit, stop=stop)
                except Exception:
                    logger.error("Fatal error on open_trade: ", exc_info=True)
            else:
                logger.warning('Trying to open_trade without connection')
            return [html.I(className=get_battery(n)), False]
    return [html.I(className=get_battery(n)), False]


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
