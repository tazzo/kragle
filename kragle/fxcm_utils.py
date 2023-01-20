import datetime as dt
import logging.config

import fxcmpy

from kragle.kdb import KragleDB
from kragle.utils import  periods

logger = logging.getLogger('kragle')

class FxcmManager:
    def __init__(self, config_file='fxcm.cfg', dbname='tmp'):
        logger.info('Init KragleDB ...')
        self.kdb = KragleDB(dbname)
        logger.info('Done')
        logger.info('Init fxcmpy ...')
        self.fxcon = fxcmpy.fxcmpy(config_file=config_file)
        logger.info('Done')

    def close(self):
        logger.info('Closing fxcmpy ...')
        self.fxcon.close()
        logger.info('Done')

    def fetch_candles(self, start, end, instrument='EUR/USD', period='m1'):
        delta = 600
        if period == 'm1':
            delta = 7
        elif period == 'm5':
            delta = 30
        elif period == 'm15':
            delta = 90
        elif period == 'm30':
            delta = 150
        elif period == 'H1':
            delta = 300
        tmpstart = start
        tmpend = tmpstart + dt.timedelta(delta)
        if tmpend > end:
            tmpend = end
        loop = True
        while loop:
            df = self.fxcon.get_candles(instrument, period=period, start=tmpstart, end=tmpend, with_index=False)
            logger.info('instrument: ' + instrument + ' period: ' + period + ' delta: ' + str(delta) + ' from: ' + str(
                tmpstart) + ' to:' + str(tmpend) + ' n: ' + str(df.size))

            self.kdb.fetch_dataframe(df, instrument, period)

            if tmpend == end:
                loop = False
            else:
                tmpstart = tmpstart + dt.timedelta(delta)
                tmpend = tmpstart + dt.timedelta(delta)
                if tmpend > end:
                    tmpend = end

    def fetch_instrument(self, start, end, instrument='EUR/USD'):
        for p in periods:
            logger.info('Fetching ' + instrument + ' period ' + p)
            self.fetch_candles(start, end, instrument=instrument, period=p)