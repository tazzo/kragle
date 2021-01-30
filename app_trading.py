import dash_table
import pandas as pd
from dash.dependencies import Input, Output

from app_layout import *

trader = None


def render_trading_page():
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col(html.Div(
                    className=class_box,
                    children=[
                        build_subscription_box()
                    ]), className=class_col, width=12),
                dbc.Col(html.Div("2 One of four columns", className=class_box), className=class_col, md=6, xl=4),
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
        return [[dbc.Button("Connect", id="connect-button", className="mx-1"),
                 dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1")]]
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'disconnect-button':
            # trader.close()
            # trader = None
            return [[dbc.Button("Connect", id="connect-button", disabled=False, className="mx-1"),
                     dbc.Button("Disconnect", id="disconnect-button", disabled=True, className="mx-1")]]
        else:
            # trader = kragle.kragle_fxcm.FxcmTrader()
            return [[dbc.Button("Connect", id="connect-button", disabled=True, className="mx-1"),
                     dbc.Button("Disconnect", id="disconnect-button", disabled=False, className="mx-1")]]


@app.callback(Output('table-subscription', 'data'),
              Input('interval-subscription', 'n_intervals'))
def update_subscription(n):
    return trader.get_prices().to_dict('records') if trader is not None else pd.DataFrame().to_dict('records')
