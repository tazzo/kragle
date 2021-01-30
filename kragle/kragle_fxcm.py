import atexit
import signal

import fxcmpy


class FxcmTrader:

    def __init__(self, config_file='fxcm.cfg', instrument='EUR/USD'):
        self.con = fxcmpy.fxcmpy(config_file='fxcm.cfg')
        self.con.subscribe_market_data(instrument)
        self.instrument = instrument
        atexit.register(self.close)
        signal.signal(signal.SIGINT, self.close)  # ctlr + c


    def get_prices(self):
        return self.con.get_prices(self.instrument)

    def close(self):
        self.con.close()
