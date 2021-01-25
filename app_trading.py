import dash_html_components as html


def render_trading_page():
    return html.Div(
        className="bg-white font-sans leading-normal tracking-normal mt-12 w-full",
        children=[
            html.Div(
                className="box-container",
                children=[
                    html.Div(
                        className='w-full p-2',
                        children=html.Div(
                            className='box',
                            children=[
                                "Trading dashboard"
                            ],
                        ),
                    ),

                ],
            ),
        ]
    )
