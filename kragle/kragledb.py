import datetime as dt
import json
import pandas as pd
from pymongo import MongoClient

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
        ret = [{'x':{'m1':[1,2,3,4], 'm5':[11,22,44,55]}, 'y':1.11350},{'x':{}, 'y':1.11350}]
        return ret
       

    




