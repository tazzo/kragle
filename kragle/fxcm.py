import threading
import fxcmpy
import time
import logging


class FxcmTrader:

    def __init__(self, config_file='fxcm.cfg', instrument='EUR/USD'):
        self.con = fxcmpy.fxcmpy(config_file='fxcm.cfg')
        self.con.subscribe_market_data(instrument)
        self.instrument = instrument
        self._loop = True
        th = threading.Thread(target=self.loop, name='loop', daemon=True)
        th.start()

    def get_prices(self):
        return self.con.get_prices(self.instrument)

    def close(self):
        print('closing <<<<----------------')
        self.con.close()
        self._loop = False

    def loop(self):
        while self._loop:
            logging.error('---->> loop <<----')
            time.sleep(2)
