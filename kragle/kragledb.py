import datetime as dt
import json
import pandas as pd
from pymongo import MongoClient
import kragle.utils as kutils 
import random as rnd

instruments = [  'USD/SEK', 
                'USD/NOK','USD/MXN', 'USD/ZAR', 'USD/HKD', 'USD/TRY', 
                'USD/ILS', 'USD/CNH',  'XAU/USD', 
                'XAG/USD', 'BTC/USD', 'BCH/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD']

done = ['EUR/USD', 'USD/JPY','ETH/USD','USD/CHF','GBP/USD','USD/CAD', 
        'AUD/USD','NZD/USD','EUR/GBP', 
        'EUR/JPY', 'EUR/CHF']
periods = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'D1']

class KragleDB:


    def __init__(self, dbname = 'kragle'):

        self.client = MongoClient('localhost', 27017)
        self.db = self.client[dbname]
        self.dbname = dbname

    def close(self):
        self.client.close()


    def get_instrument(self, instrument , period = 'm1', start = None, end = None, limit = 100000):

        db = self.db[instrument][period]
        
        if (start is None) | (end is None):
            data = list(db.find({}).limit(100000)) # data is in json format
        else:
            data = list(db.find({'date': {'$gte': start, '$lt': end}}).limit(limit))
        
        df =  pd.DataFrame(data)
        return df


    def fetch_dataframe(self, df, instrument, period):
        self.db[instrument][period].insert_many(df.to_dict("records"))


    def dataframe_to_json(self, df, path):
        df.drop('_id', axis=1).to_json(path, orient='records', date_format='iso')


    def dataframe_read_json(self,  path):
        return pd.read_json(path, orient='records')

    
    def create_dataset(self, n, instrument, periods, histlen, start, end):
        if start >= end: 
            raise ValueError('Date error, start date must be before end date.')
        ret = []
        for i in range(n):
            m1date = kutils.random_date(start, end) 
            ret.append(self.create_value(n, instrument, periods, histlen, m1date ))
        return ret
       
    def create_value(self, n, instrument, periods, histlen, m1date):
        val = {'date': m1date, 'x':{}, 'y':rnd.random()}
        before = None
        for period in periods:
            l = self.get_history(instrument, period, histlen, m1date)
            if len(l) < histlen : 
                raise ValueError('Not enough data to fulfill the request in period ' + period)
            if before != None:
                l = self.correct_last(l,before)
            before = l
            val['x'][period] = l   
        return val
    
    def correct_last(self, l, before):
        df = pd.DataFrame(before)
        df = df.loc[df.date >= l[0]['date'],:]
        agg = self.aggregate_dataframe(df)
        l[0]['bidopen']=agg['bidopen']
        l[0]['bidclose']=agg['bidclose']
        l[0]['bidhigh']=agg['bidhigh']
        l[0]['bidlow']=agg['bidlow']
        l[0]['askopen']=agg['askopen']
        l[0]['askclose']=agg['askclose']
        l[0]['askhigh']=agg['askhigh']
        l[0]['asklow']=agg['asklow']
        l[0]['tickqty']=agg['tickqty']
        return l

    def get_history(self,  instrument, period, histlen, date):
        return list(self.db[instrument][period]
            .find({'date': { '$lte': date}})
            .sort([('date', -1)])
            .limit(histlen)
        )
        
    def aggregate_dataframe(self, df):
        return kutils.aggregate_dataframe(df)

    def insert_future(self, instrument , period, start, end, d=12, r=2 ):
        df = self.get_instrument( instrument , period, start , end )
        self._insert_future(df, instrument , period, d=d, r=r)

    def _insert_future(self, df, instrument , period, d=12, r=2 ):
        gap=d-r
        win=r*2+1
        for r in range(df.shape[0]-d-r):
            
            tmp = df.loc[[(i+r+gap)  for i in range(win)],'bidopen']
            start = df.loc[r,'bidopen']
            future = round((tmp.mean()-start), 4)
            
            self.db[instrument][period].update(
                { '_id': df.loc[r,'_id']}
                , { '$set': { "future": future } }
                , upsert=False )



  
    




