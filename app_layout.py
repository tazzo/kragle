import dash
import dash_core_components as dcc
import dash_html_components as html




app = dash.Dash(__name__, meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
])

# app.config["suppress_callback_exceptions"] = True



def render_top():
    return html.Nav(
        children=[
            html.Div(
                className="bg-gray-200 text-gray-200 p-4 space-x-4",
                children=[
                    html.Div([
                        dcc.Link(
                            html.Img(src='assets/logo-100.png', className=" inline-block"),
                            href='/'
                        ),
                        # dcc.Link('Kragle', href='/', className="text-5xl text-bold inline-block"),
                        html.P("AI - Trading", className="ml-4 text-xs inline-block")
                    ], className="inline-block text-gray-900"),
                    dcc.Link('Trading', href='/trading', className="inline-block px-8 text-gray-900"),
                    dcc.Link('Dashboard', href='/dashboard', className="inline-block px-8 text-gray-900")

                ],
            )
        ]
    )

def render_content():
    return html.Div(children=[render_top(),
                              dcc.Location(id='url', refresh=False),
                              html.Div(id='page-content')])

app.layout = render_content()