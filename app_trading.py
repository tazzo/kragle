import dash_html_components as html1

import dash_table
import pandas as pd
from dash.dependencies import Input, Output

import kragle.trader
from app_layout import *

trader = None

fake_connection = False


def render_trading_page():
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col(build_trader_box(), className=class_col, width=12, style={'height': '350px'}),
            ]),
            dbc.Row([
                dbc.Col(build_counter_card(), className=class_col, md=6, xl=4),
                dbc.Col(build_card(), className=class_col, md=6, xl=4),
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

        ]
    )


def build_trader_box():
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col(
                    html.H2('FXCM Trader'),
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
        dbc.CardHeader("Card header"),
        dbc.CardBody(
            [
                html.H5("Card title", className="card-title"),
                html.P(
                    "This is some card content that we'll reuse",
                    className="card-text",
                ),
            ]
        )],
        className=class_card, outline=True
    )


def build_counter_card():
    return dbc.Card([
        dbc.CardHeader("Counter"),
        dbc.CardBody(id='interval-counter-div')],
        className=class_card, outline=True
    )


@app.callback(
    [Output("connection-div", "children"), Output("disconnection-div", "children")],
    [Input("connect-button", "n_clicks"), Input("disconnect-button", "n_clicks")]
)
def on_connection_button_click(n_connect, n_disconnect):
    ctx = dash.callback_context
    global trader
    if not ctx.triggered:
        if trader is None:
            return [dbc.Button("Connect", id="connect-button", disabled=False, className="mx-1"),
                    dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1")]
        else:
            return [dbc.Button("Connect", id="connect-button", disabled=True, className="mx-1"),
                    dbc.Button("Disconnect", id="disconnect-button", disabled=False, className="mx-1")]

    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'disconnect-button':
            if not fake_connection:
                print('Closing ... ')
                trader.close()
                print('Closed ... ')
                trader = None
            return [dbc.Button("Connect", id="connect-button", disabled=False, className="mx-1"),
                    dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1")]
        else:
            if not fake_connection:
                try:
                    print('Connecting ... ')
                    trader = kragle.trader.FxcmTrader()
                    print('Connected!')
                    return [dbc.Button("Connect", id="connect-button", disabled=True, className="mx-1"),
                            dbc.Button("Disconnect", id="disconnect-button", disabled=False, className="mx-1")]
                except Exception as e:
                    print(e)
                    return [dbc.Button("Connect", id="connect-button", disabled=False, className="mx-1"),
                            dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1")]

            dbc.Tab('tab_accounts', label="Accounts", id='tab_accounts'),
            dbc.Tab('tab_accounts_summary', label="Accounts summary", id='tab_accounts_summary'),
            dbc.Tab('tab_open_positions', label="Open positions", id='tab_open_positions'),
            dbc.Tab('tab_open_positions_summary', label="Open positions_summary", id='tab_open_positions_summary'),
            dbc.Tab('tab_closed_positions', label="Closed positions", id='tab_closed_positions'),
            dbc.Tab('tab_closed_positions_summary', label="Closed positions summary",
                    id='tab_closed_positions_summary'),
            dbc.Tab('tab_orders', label="Orders", id='tab_orders'),
            dbc.Tab('tab_summary', label="Summary", id='tab_summary'),


@app.callback([Output('tab_accounts', 'children'),
               Output('tab_accounts_summary', 'children'),
               Output('tab_open_positions', 'children'),
               Output('tab_open_positions_summary', 'children'),
               Output('tab_closed_positions', 'children'),
               Output('tab_closed_positions_summary', 'children'),
               Output('tab_orders', 'children'),
               Output('tab_summary', 'children'),
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
        return [r1, r2, r3, r4, r5, r6, r7, r8, n]
    else:
        return ['', '', '', '', '', '', '', '', n]
