import random as rnd

import pandas as pd
from pymongo import MongoClient

import kragle.utils as kutils

instruments = ['USD/SEK',
               'USD/NOK', 'USD/MXN', 'USD/ZAR', 'USD/HKD', 'USD/TRY',
               'USD/ILS', 'USD/CNH', 'XAU/USD',
               'XAG/USD', 'BTC/USD', 'BCH/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD']

done = ['EUR/USD', 'USD/JPY', 'ETH/USD', 'USD/CHF', 'GBP/USD', 'USD/CAD',
        'AUD/USD', 'NZD/USD', 'EUR/GBP',
        'EUR/JPY', 'EUR/CHF']
periods = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'D1']


def getDBNames():
    client = MongoClient('localhost', 27017)
    l = client.list_database_names()
    client.close()
    return l

class KragleDB:

    def __init__(self, dbname='forex_raw'):

        self.client = MongoClient('localhost', 27017)
        self.db = self.client[dbname]
        self.dbname = dbname

    def close(self):
        self.client.close()

    def get_instruments(self):
        return list(self.get_instruments_and_periods())

    def get_periods(self, instrument):
        return self.getInstrumentsAndPeriods()[instrument]

    def get_instruments_and_periods(self):
        names = self.db.collection_names()
        return self._calc_instruments_and_periods(names)

    def _calc_instruments_and_periods(self, names):
        res = {}
        for name in names:
            try:
                l = name.split('.')
                val = res.get(l[0], [])
                val.append(l[1])
                res[l[0]] = val
            except:
                pass
        return res

    def get_instrument(self, instrument, period='m1', start=None, end=None, limit=100000):

        db = self.db[instrument][period]

        if (start is None) | (end is None):
            data = list(db.find({}).limit(100000))  # data is in json format
        else:
            data = list(db.find({'date': {'$gte': start, '$lte': end}}).limit(limit))

        return pd.DataFrame(data)

    def get_instrument_value(self, instrument, period, date):
        db = self.db[instrument][period]
        return db.find_one({'date': date})

    # TODO: add a test
    def fetch_dataframe(self, df, instrument, period, check_duplicates=True):
        """
        Fetch the dataframe in the DB using 'date' to replace existing elements o creating a new one

        Args:
            df (pandas.DataFrame): the dataframe to fetch
            instrument (String): the forex instrument ('EUR/USD', 'EUR/JPY' ... )
            period (String): the instrument period ('m1', 'm5', 'm15' ... )
        """
        if check_duplicates:
            for record in df.to_dict("records"):
                self.db[instrument][period].replace_one({'date': record['date']}, record, upsert=True)
        else:
            self.db[instrument][period].insert_many(df.to_dict("records"))

    def dataframe_to_json(self, df, path):
        """
        Write the dataframe to a file (specified with path) in 'records' format
        while eliminating '_id' column derived from mongoDB

        Args:
            df (DataFrame): A Pandas DataFrame to write
            path ([type]): Path to file
        """
        df.drop('_id', axis=1).to_json(path, orient='records', date_format='iso')

    def dataframe_read_json(self, path):
        """
        Pandas read_json with orient='records'

        Args:
            path (String): path to file

        Returns:
            [DataFrame]: pandas dataframe
        """
        return pd.read_json(path, orient='records')

    # TODO: create a test
    def create_dataset(self, n, instrument, periods, histlen, start, end):
        if start >= end:
            raise ValueError('Date error, start date must be before end date.')
        ret = []
        for i in range(n):
            m1date = kutils.random_date(start, end)
            ret.append(self.create_value(n, instrument, periods, histlen, m1date))
        return ret

    def create_value(self, n, instrument, periods, histlen, m1date):
        val = {'date': m1date, 'x': {}, 'y': rnd.random()}
        before = None
        for period in periods:
            l = self.get_history(instrument, period, histlen, m1date)
            if len(l) < histlen:
                raise ValueError('Not enough data to fulfill the request in period ' + period)
            if before != None:
                l = self.correct_last(l, before)
            before = l
            val['x'][period] = l

        return val

    def correct_last(self, l, before):
        df = pd.DataFrame(before)
        df = df.loc[df.date >= l[0]['date'], :]
        agg = kutils.aggregate_dataframe(df)
        l[0]['bidopen'] = agg['bidopen']
        l[0]['bidclose'] = agg['bidclose']
        l[0]['bidhigh'] = agg['bidhigh']
        l[0]['bidlow'] = agg['bidlow']
        l[0]['askopen'] = agg['askopen']
        l[0]['askclose'] = agg['askclose']
        l[0]['askhigh'] = agg['askhigh']
        l[0]['asklow'] = agg['asklow']
        l[0]['tickqty'] = agg['tickqty']

        return l

    def get_history(self, instrument, period, histlen, date):
        """[summary]

        Args:
            instrument ([type]): [description]
            period ([type]): [description]
            histlen ([type]): [description]
            date ([type]): [description]

        Returns:
            [type]: [description]
        """
        return list(self.db[instrument][period]
                    .find({'date': {'$lte': date}})
                    .sort([('date', -1)])
                    .limit(histlen)
                    )

    def insert_future(self, instrument, period, start, end, field='bidopen', d=12, r=2):
        """[summary]

        Args:
            instrument ([type]): [description]
            period ([type]): [description]
            start ([type]): [description]
            end ([type]): [description]
            d (int, optional): [description]. Defaults to 12.
            r (int, optional): [description]. Defaults to 2.
        """
        df = self.get_instrument(instrument, period, start, end)
        self._insert_future(df, instrument, period, d=d, r=r)

    def _insert_future(self, df, instrument, period, field='bidopen', d=12, r=2):
        gap = d - r
        win = r * 2 + 1
        for r in range(df.shape[0] - d - r):
            tmp = df.loc[[(i + r + gap) for i in range(win)], field]
            start = df.loc[r, field]
            future = round((tmp.mean() - start), 4)

            self.db[instrument][period].update_one(
                {'_id': df.loc[r, '_id']}
                , {'$set': {"future": future}}
                , upsert=False)
