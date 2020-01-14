import fxcmpy
import datetime as dt
import json
import pandas as pd
from pymongo import MongoClient

instruments = [  'USD/SEK', 
                'USD/NOK','USD/MXN', 'USD/ZAR', 'USD/HKD', 'USD/TRY', 'USD/ILS', 'USD/CNH',  'XAU/USD', 
                'XAG/USD', 'BTC/USD', 'BCH/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD']

done = ['EUR/USD', 'USD/JPY','ETH/USD','USD/CHF','GBP/USD','USD/CAD', 'AUD/USD','NZD/USD','EUR/GBP', 
        'EUR/JPY', 'EUR/CHF']
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

    def get_instrument(self, instrument , period = 'm1', start = None, end = None):

        db = self.db.raw[instrument][period]
        
        if (start is None) | (end is None):
            data = list(db.find({}).limit(100000)) # data is in json format
        else:
            data = list(db.find({'date': {'$gte': start, '$lt': end}}).limit(100000))
        
        df =  pd.DataFrame(data)
        return df

    def insert_future(self, df, instrument , period ):
        d = 10
        r = 2
        gap=d-r
        win=r*2+1
        for r in range(df.shape[0]-d-r):
            
            tmp = df.loc[[(i+r+gap)  for i in range(win)],'bidopen']
            start = df.loc[r,'bidopen']
            future = (tmp.mean()-start)/start
            
            self.db.raw[instrument][period].update(
                { '_id': df.loc[r,'_id']}
                , { '$set': { "future": future } }
                , upsert=False )
            
    def fetch_dataframe(self, df, instrument, period):
        df_json = df.T.to_json()
        df_json_list = json.loads(df_json).values() 
        if 'date' in df.columns:
            l=list(df_json_list)
            for tmp in l: 
                tmp['date'] = dt.datetime.fromtimestamp(tmp['date']/ 1e3)
        self.db.raw[instrument][period].insert_many(df_json_list )

    def m1(self, start, end):
        loop=True
        res = []
        tmpdate = start
        day = {}
        while loop:
            res.append({'date':tmpdate})
            tmpdate = tmpdate +  dt.timedelta(minutes=1)
            day[tmpdate.weekday()] = True
            
            if (tmpdate.weekday() == 4) :
               if (tmpdate.hour == 22) & (tmpdate.minute == 59):
                    tmpdate = tmpdate + dt.timedelta(days=2)
                    tmpdate.replace(hour=20)
            if tmpdate > end : loop = False
        return pd.DataFrame(res)

if __name__ == '__main__':
    print('init')
    m = Manager()
    m.init_fxcm()
    start = dt.datetime(2018, 1, 1)

    end = dt.datetime(2020, 1, 1)
    print('fetch_candles')
    #try:
    m.fetch_instrument('EUR/CHF', start, end)
    #except err:
    #    print("OS error: {0}".format(err))
    #    print ('Error !!!')
    print ('Done !!!')
    m.fxcon.close()
    exit(0)



        
        

    