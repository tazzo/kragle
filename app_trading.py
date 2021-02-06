import dash_html_components as html1

from dash.dependencies import Input, Output
import plotly.graph_objects as go

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
                dbc.Col(build_card(),
                        className=class_col, md=6, xl=4),
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
                    width=3
                ),
                dbc.Col(
                    html1.Div(dbc.Button("Connect", id="connect-button", className="mx-1"),
                              id='connection-div'
                              ), width=1
                ),
                dbc.Col(
                    html1.Div(dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1"),
                              id='disconnection-div'
                              ), width=1
                ),
                dbc.Col(
                    dcc.Loading(
                        id="loading-connection",
                        type="dot",
                        children=html.Div(id="loading-connection-output", className='mt-3')
                    ), width=1,
                ),
            ]),
            dcc.Interval(
                id='interval-subscription',
                interval=1 * 1000,  # in milliseconds
                n_intervals=0
            ),
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    html.Div(render_tabs()),
                    width=12
                ),
            ]),
        ])
    ], className='shadow rounded mb-3 h-100', )


def build_card():
    return dbc.Card([
        dbc.CardHeader(html.H4('Chart', className="font-weight-bold")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon("hours", addon_type="prepend"),
                            dbc.Input(placeholder="1", type="number"),
                        ],
                        className="mb-3 w-50   ",
                    ),
                ),
            ]),
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
                        className="mb-3 w-50",
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
        dbc.CardFooter('Footer')
    ], className=class_card, outline=True)


def build_counter_card():
    return dbc.Card([
        dbc.CardHeader("Counter"),
        dbc.CardBody(id='interval-counter-div')],
        className=class_card, outline=True
    )


@app.callback(
    [Output("connection-div", "children"),
     Output("disconnection-div", "children"),
     Output("loading-connection-output", "children")],
    [Input("connect-button", "n_clicks"),
     Input("disconnect-button", "n_clicks")]
)
def on_connection_button_click(n_connect, n_disconnect):
    ctx = dash.callback_context
    global trader
    button_connect = dbc.Button("Connect", id="connect-button", disabled=False, className="mx-1")
    button_connect_disabled = dbc.Button("Connect", id="connect-button", disabled=True, className="mx-1")
    button_disconnect = dbc.Button("Disconnect", id="disconnect-button", disabled=False, className="mx-1")
    button_disconnect_disabled = dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1")
    if not ctx.triggered:
        if trader is None:
            return [button_connect,
                    button_disconnect_disabled,
                    '']
        else:
            return [button_connect_disabled,
                    button_disconnect,
                    '']

    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'disconnect-button':
            print('Closing ... ')
            trader.close()
            print('Closed ... ')
            trader = None
            return [button_connect,
                    button_disconnect_disabled,
                    '']
        else:
            try:
                print('Connecting ... ')
                trader = kragle.trader.FxcmTrader()
                print('Connected!')
                return [button_connect_disabled,
                        button_disconnect,
                        '']
            except Exception as e:
                print(e)
                return [button_connect,
                        button_disconnect_disabled,
                        '']


@app.callback([Output('chart-live', 'children')],
              Input('chart-live-interval', 'n_intervals')
              )
def update_chart_live(n):
    if trader is not None:
        return build_candle_chart()
    else:
        return ['']


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
        r1 = dbc.Table.from_dataframe(trader.accounts, striped=True, bordered=True, hover=True, size='sm')
        r2 = dbc.Table.from_dataframe(trader.accounts_summary, striped=True, bordered=True, hover=True, size='sm')
        r3 = dbc.Table.from_dataframe(trader.open_positions, striped=True, bordered=True, hover=True, size='sm')
        r4 = dbc.Table.from_dataframe(trader.open_positions_summary, striped=True, bordered=True, hover=True, size='sm')
        r5 = dbc.Table.from_dataframe(trader.closed_positions, striped=True, bordered=True, hover=True, size='sm')
        r6 = dbc.Table.from_dataframe(trader.closed_positions_summary, striped=True, bordered=True, hover=True,
                                      size='sm')
        r7 = dbc.Table.from_dataframe(trader.orders, striped=True, bordered=True, hover=True, size='sm')
        r8 = dbc.Table.from_dataframe(trader.summary, striped=True, bordered=True, hover=True, size='sm')
        r9 = dbc.Table.from_dataframe(trader.offers, striped=True, bordered=True, hover=True, size='sm')

        return [r1, r2, r3, r4, r5, r6, r7, r8, r9, n]
    else:
        return ['', '', '', '', '', '', '', '', '', n]


def build_candle_chart():
    fig = go.Figure(go.Candlestick(
        x=trader.candles.index,
        open=trader.candles['bidopen'],
        high=trader.candles['bidhigh'],
        low=trader.candles['bidlow'],
        close=trader.candles['bidclose']
    ))
    return dcc.Graph(figure=fig)
