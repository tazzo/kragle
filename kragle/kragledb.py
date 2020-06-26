import random
import datetime as dt
import pandas as pd
from pymongo import MongoClient
import logging
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


def check_date_index_db(db):
    for coll_name in db.list_collection_names():
        db[coll_name].create_index([('date', -1)], unique=True)


def check_date_index_collection(db):
    db.create_index([('date', -1)], unique=True)


class KragleDB:

    def __init__(self, dbname='forex_raw'):

        self.client = MongoClient('localhost', 27017)
        self.db = self.client[dbname]
        self.dbname = dbname
        check_date_index_db(self.db)

    def close(self):
        self.client.close()

    def get_instruments(self):
        return list(self.get_instruments_and_periods())

    def get_periods(self, instrument):
        return self.getInstrumentsAndPeriods()[instrument]

    def get_instruments_and_periods(self):
        names = self.db.collection_names()
        return kutils.dot_names_to_dict(names)

    def get_instrument(self, instrument, period='m1', start=None, end=None, limit=100000):

        db = self.db[instrument][period]

        if type(start) is not dt.datetime:
            raise ValueError('Start date must be a datetime.datetime not {} '.format(type(start)))
        elif type(end) is not dt.datetime:
            raise ValueError('End date must be a datetime.datetime not {} '.format(type(end)))
        else:
            data = list(db.aggregate([
                {'$match': {'date': {'$gte': start, '$lte': end}}},
                {'$sort': {'date': 1}},
                {'$limit': limit},
            ]))
        return pd.DataFrame(data)

    def get_instrument_value(self, instrument, period, date):
        db = self.db[instrument][period]
        return db.find_one({'date': date})

    def drop(self, instrument):
        return self.db[instrument].drop()

    # TODO: add a test
    def fetch_dataframe(self, df, instrument, period):
        """
        Fetch the dataframe in the DB using 'date' to replace existing elements o creating a new one

        Args:
            df (pandas.DataFrame): the dataframe to fetch
            instrument (String): the forex instrument ('EUR/USD', 'EUR/JPY' ... )
            period (String): the instrument period ('m1', 'm5', 'm15' ... )
        """
        check_date_index_collection(self.db[instrument][period])

        for record in df.to_dict("records"):
            self.db[instrument][period].replace_one({'date': record['date']}, record, upsert=True)


    def dataframe_to_json(self, df, path):
        """
        Write the dataframe to a file (specified with path) in 'records' format
        while eliminating '_id' column derived from mongoDB

        Args:
            df (DataFrame): A Pandas DataFrame to write
            path ([type]): Path to file
        """
        df.drop('_id', axis=1).to_json(path, orient='records', date_format='iso')

    # TODO: create a test
    def create_dataset(self, n, instrument, periods, histlen, date_start, date_end):
        if date_start >= date_end:
            raise ValueError('Date error, start date must be before end date.')
        base_date_list = self.get_base_date_list(n, instrument, periods, date_start, date_end)
        ret = []
        for i in range(n):
            tmp = base_date_list.pop(random.randrange(len(base_date_list)))
            ret.append(self.create_train_value(instrument, periods, histlen, tmp['date']))
        return ret

    def get_base_date_list(self, n, instrument, periods, date_start, date_end):
        db = self.db[instrument][periods[0]]
        base_date_list = list(db.find(
            {'date': {'$gte': date_start, '$lte': date_end}},
            {'date': 1, '_id': 0}
        ))
        if len(base_date_list) < n :
            raise ValueError('Not enough data to fulfill the request in period ' + periods[0])
        return base_date_list

    def create_train_value(self, instrument, periods, history_len, m1date):
        #TODO: fix y
        val = {'date': m1date, 'x': {}, 'y': random.random()}
        for period in periods:
            l = self.get_history_bidopen(instrument, period, history_len, m1date)
            if len(l) < history_len:
                raise ValueError('Not enough data to fulfill the request in period ' + period)
            if (period == 'm1') & (l[0]['date'] != m1date):
                raise ValueError('Date {} not in requested period'.format(m1date))

            val['x'][period] = l

            # tickqty
            if period == periods[0]:
                l = self.get_history_tickqty(instrument, period, history_len, m1date)
                val['x']['tickqty'] = l
        return val

    def get_history_tickqty(self, instrument, period, history_len, date):
        return self.get_history_field(instrument, period, 'tickqty', history_len, date)

    def get_history_bidopen(self, instrument, period, history_len, date):
        return self.get_history_field(instrument, period, 'bidopen', history_len, date)

    def get_history_field(self, instrument, period, field, history_len, date):
        return list(self.db[instrument][period].aggregate([
            {'$match': {'date': {'$lte': date}}},
            {'$sort': {'date': -1}},
            {'$limit': history_len},
            {'$project': {'date': 1, 'value': '${}'.format(field), '_id': 0}},
        ]))

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
            id = df.loc[r, '_id']
            self.db[instrument][period].update_one(
                {'_id': id},
                {'$set': {"future": future}},
                upsert=False)


