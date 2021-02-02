import threading
import fxcmpy
import time
import logging

import pandas as pd
import kragle.strategy

class FxcmTrader:

    def __init__(self, config_file='fxcm.cfg', instrument='EUR/USD', strategy=None, sleep=10):
        self.strategy = strategy
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
                    if self.strategy is not None:
                        a = self.strategy.action(pd.DataFrame())
                        if a == kragle.strategy.Action.HOLD:
                            pass
                        elif a == kragle.strategy.Action.SELL:
                            self.sellOrder()
                        elif a == kragle.strategy.Action.BUY:
                            self.buyOrder()
                        else:
                            self.logger.error('Should not be here. Strategy action should be one of 3 action HOLD/BUY/SELL, got: ' + str(a))
                    else:
                        self.logger.warning('None strategy found.')
            time.sleep(self.sleep)

    def check_time(self):
        self.logger.info('check_time')
        return True

    def check_orders(self):
        self.logger.info('check_orders')
        return True

    def buyOrder(self):
        pass

    def sellOrder(self):
        pass

