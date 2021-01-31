import dash_table
import pandas as pd
from dash.dependencies import Input, Output

import kragle.fxcm
from app_layout import *

trader = None

fake_connection = False


def render_trading_page():
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col(html.Div(
                    className=class_box,
                    children=[
                        build_subscription_box()
                    ]), className=class_col, width=12),
                dbc.Col(html.Div("2 One of four columns", className=class_box, id='interval-counter-div'),
                        className=class_col, md=6, xl=4),
                dbc.Col(html.Div("3 One of four columns", className=class_box), className=class_col, md=6, xl=4),
            ]),
        ],
        className='p-3', fluid=True
    )


def build_subscription_box():
    df = trader.get_prices() if trader is not None else pd.DataFrame()
    return html.Div(
        [
            dbc.Row([
                dbc.Col([
                    dcc.Interval(
                        id='interval-subscription',
                        interval=1 * 1000,  # in milliseconds
                        n_intervals=0
                    ),
                    html.H1('EUR/USD subscription'),
                ]),
                dbc.Col([
                    html.Div(
                        [dbc.Button("Connect", id="connect-button", className="mx-1"),
                         dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1")],
                        id='connection-div'
                    )
                ], width=1),
            ]),
            dbc.Row([
                dbc.Col(
                    dash_table.DataTable(
                        id='table-subscription',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict('records'),
                        page_size=10,
                    ),
                    width=6
                ),
            ]),
        ]
    )


@app.callback(
    [Output("connection-div", "children")],
    [Input("connect-button", "n_clicks"), Input("disconnect-button", "n_clicks")]
)
def on_connection_button_click(n_connect, n_disconnect):
    ctx = dash.callback_context
    global trader
    if not ctx.triggered:
        if trader is None:
            return [[dbc.Button("Connect", id="connect-button", disabled=False, className="mx-1"),
                     dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1")]]
        else:
            return [[dbc.Button("Connect", id="connect-button", disabled=True, className="mx-1"),
                     dbc.Button("Disconnect", id="disconnect-button", disabled=False, className="mx-1")]]

    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'disconnect-button':
            if not fake_connection:
                print('Closing ... ')
                trader.close()
                print('Closed ... ')
                trader = None
            return [[dbc.Button("Connect", id="connect-button", disabled=False, className="mx-1"),
                     dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1")]]
        else:
            if not fake_connection:
                try:
                    print('Connecting ... ')
                    trader = kragle.fxcm.FxcmTrader()
                    print('Connected!')
                    return [[dbc.Button("Connect", id="connect-button", disabled=True, className="mx-1"),
                             dbc.Button("Disconnect", id="disconnect-button", disabled=False, className="mx-1")]]
                except Exception as e:
                    print(e)
                    return [[dbc.Button("Connect", id="connect-button", disabled=False, className="mx-1"),
                             dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1")]]


@app.callback([Output('table-subscription', 'data'), Output('table-subscription', 'columns'),
               Output('interval-counter-div', 'children')],
              Input('interval-subscription', 'n_intervals')
              )
def update_subscription(n):
    df = trader.get_prices() if trader is not None else pd.DataFrame()
    d = df.to_dict('records')
    df_columns = [{"name": i, "id": i} for i in df.columns]
    return [d, df_columns, n]
