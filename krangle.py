import fxcmpy
import datetime as dt
import json
import pandas as pd
from pymongo import MongoClient

instruments = [  'USD/SEK', 
                'USD/NOK','USD/MXN', 'USD/ZAR', 'USD/HKD', 'USD/TRY', 'USD/ILS', 'USD/CNH',  'XAU/USD', 
                'XAG/USD', 'BTC/USD', 'BCH/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD']

done = ['EUR/USD', 'USD/JPY','ETH/USD','USD/CHF','GBP/USD','USD/CAD', 'AUD/USD','NZD/USD','EUR/GBP', 'EUR/JPY']
periods = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'D1']

class Manager:
    def __init__(self, config_file='fxcm.cfg', dbname = 'krangle'):

        client = MongoClient('localhost', 27017)
        self.db = client[dbname]

    def init_fxcm(self):
        self.fxcon = fxcmpy.fxcmpy(config_file='fxcm.cfg')

    def fetch_candles(self, instrument,  start, end, period='m1'):
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
        tmpend = tmpstart  + dt.timedelta(delta)
        if tmpend > end: 
            tmpend = end
        loop = True
        while loop:
            df =  self.fxcon.get_candles(instrument, period=period, start=tmpstart, end=tmpend, with_index=False)
            print ('instrument: ' + instrument + ' period: ' + period + ' delta: ' + str(delta) + ' from: ' + str(tmpstart) + ' to:' + str(tmpend) + ' n: ' + str(df.size))
            if df.size > 0:
                df_json = df.T.to_json()
                df_json_list = json.loads(df_json).values()
                l=list(df_json_list)
                for tmp in l: 
                    tmp['date'] = dt.datetime.fromtimestamp(tmp['date']/ 1e3)
                self.db.raw[instrument][period].insert_many(df_json_list )
           

            if tmpend == end:
                loop = False
            else:
                tmpstart = tmpstart  + dt.timedelta(delta)
                tmpend = tmpstart  + dt.timedelta(delta)
                if tmpend > end: 
                    tmpend = end

    def fetch_instrument(self, instrument,  start, end):
        for p in periods:
            print ('Fetching ' + instrument + ' period ' + p)
            self.fetch_candles(instrument, start, end, period=p)

    def get_instrument(self, instrument , period = 'm1'):

        db = self.db.raw[instrument][period]

        exclude_col = {'_id': False } # we are ignoring '_id' column.
        data = list(db.find({}, projection=exclude_col).limit(10000)) # data is in json format

        # converting json to pandas dataframe
        return pd.DataFrame(data)


if __name__ == '__main__':
    print('init')
    m = Manager()
    m.init_fxcm()
    start = dt.datetime(2018, 1, 1)

    end = dt.datetime(2020, 1, 1)
    print('fetch_candles')
    #try:
    m.fetch_instrument('EUR/JPY', start, end)
    #except err:
    #    print("OS error: {0}".format(err))
    #    print ('Error !!!')
    print ('Done !!!')
    m.fxcon.close()
    exit(0)



        
        

    