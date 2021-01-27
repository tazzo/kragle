import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc



app = dash.Dash(__name__, meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1"},],
                external_stylesheets=[dbc.themes.YETI])




# app.config["suppress_callback_exceptions"] = True



def render_top():
    return dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink(html.Img(src='assets/logo-100.png'), active=True, href="/")),
            dbc.NavItem(dbc.NavLink("Trading", active=True, href="/trading")),
            dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
            dbc.DropdownMenu(
                [dbc.DropdownMenuItem("Item 1"), dbc.DropdownMenuItem("Item 2")],
                label="Dropdown",
                nav=True,
            ),
        ],
        className="navbar-dark bg-primary"
    )
def render_content():
    return html.Div(children=[render_top(),
                              dcc.Location(id='url', refresh=False),
                              html.Div(id='page-content')])

app.layout = render_content()