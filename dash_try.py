import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import krangle as k
import datetime as dt
import dash_daq as daq

import dash_bootstrap_components as dbc


start = dt.datetime(2018,1,2,18,0)
end = dt.datetime(2018,1,2,19,0)

m = k.Manager()


def init_df(m, start, end):

    df = m.get_instrument('EUR/USD','m1', start, end)

    df = df.loc[:, ['date', 'bidopen', 'tickqty']]
    df2 = m.m1(start, end)
    #return df2.merge (df, left_on='date', right_on='date', how='left')
    return df

df = init_df(m, start, end)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
app.config["suppress_callback_exceptions"] = True



def build_explore_table():
    return html.Div([
            html.Div([
                html.P('From'),
                dcc.Input(
                    id='input-date-from',
                    placeholder='2019-04-29 12:00',
                    type='text',
                    value='2019-04-29 12:00'
                )  
            ]), 
            html.Div([
                html.P('To'),
                dcc.Input(
                    id='input-date-to',
                    placeholder='2019-05-02 12:00',
                    type='text',
                    value='2019-05-02 12:00'
                )  
            ]), 

            html.Div([
                dash_table.DataTable(
                    id='datatable-interactivity',
                    columns=[
                        {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
                    ],
                    data = pd.DataFrame([{}]).to_dict('records'),
                    style_cell={'textAlign': 'left', 'padding': '5px'},
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    row_selectable="multi",
                    row_deletable=True,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current= 0,
                    page_size= 20,
                ),
            ])
        ])

def build_banner():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Page 1", href="#")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("More pages", header=True),
                    dbc.DropdownMenuItem("Page 2", href="#"),
                    dbc.DropdownMenuItem("Page 3", href="#"),
                ],
                nav=True,
                in_navbar=True,
                label="More",
            ),
        ],
        brand="Krangle",
        brand_href="#",
        color="primary",
        dark=True,
    )

def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab1",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Specs-tab",
                        label="Specification Settings",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Control Charts Dashboard",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )

def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                    html.P("Operator ID"),
                    daq.LEDDisplay(
                        id="operator-led",
                        value="1705645",
                        color="#92e0d3",
                        backgroundColor="#1e2130",
                        size=50,
                    ),
                ],
            ),
            html.Div(
                id="card-2",
                children=[
                    html.P("Time to completion"),
                    daq.Gauge(
                        id="progress-gauge",
                        max=1000,
                        min=0,
                        showCurrentValue=True,  # default size 200 pixel
                    ),
                ],
            ),
            html.Div(
                id="utility-card",
                children=[daq.StopButton(id="stop-button", size=160, n_clicks=0)],
            ),
        ],
    )


@app.callback(
    [Output("app-content", "children")],
    [Input("app-tabs", "value")],
)
def render_tab_content(tab_switch):
    if tab_switch == "tab1":
        return [html.Div(
            id="status-container",
            children=[
                build_quick_stats_panel(),
                html.Div(
                    id="graphs-container",
                    children=[build_explore_table()],
                ),
            ],
        )
        ]
    return [html.Div(
            id="status-container",
            children= html.H1("Ciao")
        )]
    

app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
    ],
)


@app.callback(
    [Output('datatable-interactivity', 'style_data_conditional')
    , Output('datatable-interactivity', 'data')],
    [Input('datatable-interactivity', 'selected_columns')
    ,Input('input-date-from', 'value')
    ,Input('input-date-to', 'value')]
)
def update(selected_columns, start_date, end_date):
 
    df =pd.DataFrame({})
    if (not start_date == '')&(not end_date == ''):
        start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        df = init_df(m, start, end)
    
    return [{'if': { 'column_id': i }, 'background_color': '#D2F3FF'} for i in selected_columns], df.to_dict('records') 




if __name__ == '__main__':
    app.run_server(debug=True)