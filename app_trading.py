import dash_html_components as html
import dash_bootstrap_components as dbc

class_box = 'shadow p-3 bg-white rounded mb-3 border border-secondary'
class_col = ""


def render_trading_page():
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div("1 One of four columns", className=class_box), className=class_col, md=6, xl=4),
                    dbc.Col(html.Div("2 One of four columns", className=class_box), className=class_col, md=6, xl=4),
                    dbc.Col(html.Div("3 One of four columns", className=class_box), className=class_col, md=6, xl=4),
                    dbc.Col(html.Div("4 One of four columns", className=class_box), className=class_col, md=6, xl=4),
                    dbc.Col(html.Div("5 One of four columns", className=class_box), className=class_col, md=6, xl=4),
                    dbc.Col(html.Div("6 One of four columns", className=class_box), className=class_col, md=6, xl=4),
                ]
            ),
        ],
        className='p-3', fluid=True
    )
