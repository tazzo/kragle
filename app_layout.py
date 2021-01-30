import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1"}, ],
                external_stylesheets=[dbc.themes.YETI])


# app.config["suppress_callback_exceptions"] = True


class_box = 'shadow p-3 bg-white rounded mb-3 border border-secondary'
class_col = ""

def render_top():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Trading", href="/trading")),
            dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
        ],
        brand="KRAGLE",
        brand_href="/",
        color="primary",
        dark=True,
    )


def render_content():
    return html.Div(children=[render_top(),
                              dcc.Location(id='url', refresh=False),
                              html.Div(id='page-content')])


app.layout = render_content()
