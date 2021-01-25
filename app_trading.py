import dash_html_components as html


def render_trading_page():
    return html.Div(children=[html.P('Trading page'),
                              html.Div(id='trading-content')])
