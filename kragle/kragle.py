import fxcmpy
import datetime as dt
import json
import pandas as pd
from pymongo import MongoClient
import kragle.utils as kutils


class Manager:
    def __init__(self, config_file='fxcm.cfg', dbname='krangle'):

        client = MongoClient('localhost', 27017)
        self.db = client[dbname]

    def init_fxcm(self):
        self.fxcon = fxcmpy.fxcmpy(config_file='fxcm.cfg')

    def fetch_candles(self, instrument, start, end, period='m1'):
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
            print('instrument: ' + instrument + ' period: ' + period + ' delta: ' + str(delta) + ' from: ' + str(
                tmpstart) + ' to:' + str(tmpend) + ' n: ' + str(df.size))
            if df.size > 0:
                df_json = df.T.to_json()
                df_json_list = json.loads(df_json).values()
                l = list(df_json_list)
                for tmp in l:
                    tmp['date'] = dt.datetime.fromtimestamp(tmp['date'] / 1e3)
                self.db[instrument][period].insert_many(df_json_list)

            if tmpend == end:
                loop = False
            else:
                tmpstart = tmpstart + dt.timedelta(delta)
                tmpend = tmpstart + dt.timedelta(delta)
                if tmpend > end:
                    tmpend = end

    def fetch_instrument(self, instrument, start, end):
        for p in kutils.periods:
            print('Fetching ' + instrument + ' period ' + p)
            self.fetch_candles(instrument, start, end, period=p)

    def get_instrument(self, instrument, period='m1', start=None, end=None, limit=100000):

        db = self.db[instrument][period]

        if (start is None) | (end is None):
            data = list(db.find({}).limit(100000))  # data is in json format
        else:
            data = list(db.find({'date': {'$gte': start, '$lt': end}}).limit(limit))

        df = pd.DataFrame(data)
        return df

    def insert_future(self, df, instrument, period):
        d = 10
        r = 2
        gap = d - r
        win = r * 2 + 1
        for r in range(df.shape[0] - d - r):
            tmp = df.loc[[(i + r + gap) for i in range(win)], 'bidopen']
            start = df.loc[r, 'bidopen']
            future = (tmp.mean() - start) / start

            self.db[instrument][period].update(
                {'_id': df.loc[r, '_id']}
                , {'$set': {"future": future}}
                , upsert=False)

    def fetch_dataframe(self, df, instrument, period):
        df_json = df.T.to_json()
        df_json_list = json.loads(df_json).values()
        if 'date' in df.columns:
            l = list(df_json_list)
            for tmp in l:
                tmp['date'] = dt.datetime.fromtimestamp(tmp['date'] / 1e3)
        self.db[instrument][period].insert_many(df_json_list)

    def m1(self, start, end):
        loop = True
        res = []
        tmpdate = start
        while loop:
            res.append({'date': tmpdate})
            tmpdate = tmpdate + dt.timedelta(minutes=1)

            if tmpdate.weekday() == 4:
                if (tmpdate.hour == 22) & (tmpdate.minute == 59):
                    tmpdate = tmpdate + dt.timedelta(days=2)
                    tmpdate.replace(hour=20)
            if tmpdate > end: loop = False
        return pd.DataFrame(res)
