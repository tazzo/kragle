import threading
import fxcmpy
import time
import logging


class FxcmTrader:

    def __init__(self, config_file='config.ini', instrument='EUR/USD'):
        self.con = fxcmpy.fxcmpy(config_file='config.ini')
        self.con.subscribe_market_data(instrument)
        self.instrument = instrument
        self._loop = True
        th = threading.Thread(target=self.loop, name='loop', daemon=True)
        logging.info('starting loop thread')
        th.start()


    def get_prices(self):
        return self.con.get_prices(self.instrument)

    def close(self):
        logging.info('closing Trader')
        self.con.close()
        self._loop = False

    def loop(self):
        while self._loop:
            logging.info('Trader Loop')
            if self.check_time():#non troppi ordini di fila
                if self.check_orders():#controllo numero massim ordini
                    logging.info('Order and time check passed, tring strategy')
            time.sleep(2)

    def check_time(self):
        logging.info('check_time')
        return True

    def check_orders(self):
        return True
