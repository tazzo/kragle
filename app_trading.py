import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
from dash.dependencies import Input, Output, State

import kragle.kragle_fxcm

from app_layout import app

# TODO sistemare le classi in app_layout ?
class_box = 'shadow p-3 bg-white rounded mb-3 border border-secondary'
class_col = ""

trader = kragle.kragle_fxcm.FxcmTrader()


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
    df = trader.get_prices()
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
            ]),
            dbc.Row([
                dbc.Col(
                    dash_table.DataTable(
                        id='table-subscription',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict('records'),
                    )
                ),
            ]),
        ]
    )


@app.callback(Output('table-subscription', 'data'),
              Input('interval-subscription', 'n_intervals'))
def update_subscription(n):
    return trader.get_prices().to_dict('records')
