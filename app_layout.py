import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__, meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1"}, ],
                external_stylesheets=["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css",
                                      "https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"])

app.config["suppress_callback_exceptions"] = True

class_box = 'shadow  p-3 rounded mb-3 border'
class_card = 'shadow-1-strong rounded my-3'
class_col = ""


def render_top():
    return navbar


def render_content():
    return html.Div(children=[render_top(),
                              dcc.Location(id='url', refresh=False),
                              html.Div(id='page-content')])


navbar = dbc.Navbar([
    dbc.Row([
        dbc.Col(
            html.A([
                html.I(className='fas fa-brain'),
            ], href="/", ), width={"size": 1, "offset": 1},
        ),
        dbc.Col(
            html.A([
                dbc.NavbarBrand("KRAGLE")
            ], href="/", ), width={"size": 1, "offset": 1},
        ),
    ]),
    dbc.NavbarToggler(html.I(className='fas fa-bars'), id="navbar-toggler", ),
    dbc.Collapse(html.Ul([
            html.Li(dbc.NavLink("Trading", href="/trading" ), className='nav-item'),
            html.Li(dbc.NavLink("Dashboard", href="/dashboard"), className='nav-item'),
        ], className='navbar-nav me-auto mb-2 mb-lg-0'),
        id="navbar-collapse", navbar=True)
], color="warning", dark=True, )


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


app.layout = render_content()
