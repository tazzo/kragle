from app_dashboard import *
from app_trading import *
import logging
import logging.config


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


logging.config.fileConfig('config.ini')

if __name__ == '__main__':
    logging.debug('debug message')
    logging.info('info message')
    logging.warning('warn message')
    logging.error('error message')
    logging.critical('critical message')
    app.run_server(debug=True, host='0.0.0.0')
    # app.run_server(debug=True,use_reloader=False)
