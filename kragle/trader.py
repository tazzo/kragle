import threading
import fxcmpy
import time
import logging

import pandas as pd
import kragle.utils as kutils


class FxcmTrader:

    def __init__(self, config_file='fxcm.cfg', instrument='EUR/USD', strategy=None, sleep=10):
        self.strategy = strategy
        self.sleep = sleep
        self.logger = logging.getLogger('kragle')
        self.accounts = pd.DataFrame()
        self.open_positions = pd.DataFrame()
        self.closed_positions = pd.DataFrame()
        self.orders = pd.DataFrame()
        self.open_positions_summary = pd.DataFrame()
        self.closed_positions_summary = pd.DataFrame()
        self.accounts_summary = pd.DataFrame()
        self.summary = pd.DataFrame()
        self.offers = pd.DataFrame()
        self.candles = pd.DataFrame()
        self.candles_number = 100
        self.candles_period = 'm1'
        self.instrument = instrument

        self.con = fxcmpy.fxcmpy(config_file='fxcm.cfg')
        # self.con.subscribe_market_data(instrument)
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
        #

        while self._loop:
            self.logger.info('Trader Loop (sleep time = {})'.format(self.sleep))
            # update periodico dati
            self.update()
            # nuovi ordini
            if self.check_time():  # non troppi ordini di fila
                if self.check_orders():  # controllo numero massim ordini
                    self.logger.info('Order and time check passed, trying strategy')
                    if self.strategy is not None:
                        a = self.strategy.action(pd.DataFrame())
                        if a == kutils.Action.HOLD:
                            pass
                        elif a == kutils.Action.SELL:
                            self.sellOrder()
                        elif a == kutils.Action.BUY:
                            self.buyOrder()
                        else:
                            self.logger.error(
                                'Should not be here. Strategy action should be one of 3 action HOLD/BUY/SELL, got: ' + str(
                                    a))
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

    def get_accounts(self):
        return self.accounts

    def update(self):
        self.logger.info('Trader update internal data')
        self.accounts = self.con.get_accounts()
        self.accounts_summary = self.con.get_accounts_summary()
        self.open_positions = self.con.get_open_positions()
        self.open_positions_summary = self.con.get_open_positions_summary()
        self.closed_positions = self.con.get_closed_positions()
        self.closed_positions_summary = self.con.get_closed_positions_summary()
        self.orders = self.con.get_orders()
        self.summary = self.con.get_summary()
        self.offers = self.con.get_offers()
        self.candles = self.con.get_candles(self.instrument, period=self.candles_period, number=self.candles_number)
