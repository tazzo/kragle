import threading
import fxcmpy
import time
import logging


class FxcmTrader:

    def __init__(self, config_file='fxcm.cfg', instrument='EUR/USD', sleep=10):
        self.sleep = sleep
        self.logger = logging.getLogger('kragle')
        self.con = fxcmpy.fxcmpy(config_file='fxcm.cfg')
        self.con.subscribe_market_data(instrument)
        self.instrument = instrument
        self._loop = True
        th = threading.Thread(target=self.loop, name='loop', daemon=True)
        self.logger.info('starting loop thread')
        th.start()

    def get_prices(self):
        return self.con.get_prices(self.instrument)

    def close(self):
        self.logger.info('closing Trader')
        self.con.close()
        self._loop = False

    def loop(self):
        while self._loop:
            self.logger.info('Trader Loop')
            if self.check_time():  # non troppi ordini di fila
                if self.check_orders():  # controllo numero massim ordini
                    self.logger.info('Order and time check passed, trying strategy')
            time.sleep(self.sleep)

    def check_time(self):
        self.logger.info('check_time')
        return True

    def check_orders(self):
        self.logger.info('check_orders')
        return True
