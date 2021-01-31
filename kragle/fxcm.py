import atexit
import signal

import fxcmpy


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

class FxcmTrader:

    def __init__(self, config_file='fxcm.cfg', instrument='EUR/USD'):
        self.con = fxcmpy.fxcmpy(config_file='fxcm.cfg')
        self.con.subscribe_market_data(instrument)
        self.instrument = instrument

    def get_prices(self):
        return self.con.get_prices(self.instrument)

    def close(self):
        print('closing <<<<----------------')
        self.con.close()
