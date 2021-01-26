from kragle.app_dashboard import *
from app import app
# tmp = 0
# def sensor():
#     """ Function for test purposes. """
#     global tmp
#     while True:
#         tmp +=1
#         print("Scheduler is alive!" + str(tmp))
#         time.sleep(2)
#
#
# a = threading.Thread(target=sensor, name='Scheduler', daemon = True)
# a.start()







def render_content():
    return html.Div(children=[render_top(),
                              dcc.Location(id='url', refresh=False),
                              html.Div(id='page-content')])

def render_trading_page():
    return html.Div(children=[html.P('Trading page'),
                          html.Div(id='trading-content')])



@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/trading':
        return render_trading_page()
    elif pathname == '/dashboard':
        return render_dashboard_page()
    else:
        return render_trading_page()
    # You could also return a 404 "URL not found" page here


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
                        html.P("AI - Trading", className="ml-4 text-xs inline-block")
                    ], className="inline-block text-gray-900"),
                    dcc.Link('Trading', href='/trading', className="inline-block px-8 text-gray-900"),
                    dcc.Link('Dashboard', href='/dashboard', className="inline-block px-8 text-gray-900")

                ],
            )
        ]
    )


app.layout = render_content()

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
    #app.run_server(debug=True,use_reloader=False)

