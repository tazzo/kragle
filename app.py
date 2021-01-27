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


from app_dashboard import *
from app_trading import *

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



if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
    # app.run_server(debug=True,use_reloader=False)