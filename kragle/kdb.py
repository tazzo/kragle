import random
import datetime as dt
import logging
from collections import deque

import pandas as pd
from pymongo import MongoClient
import kragle.utils as kutils


from kragle.utils import PIP
from kragle.utils import dot_names_to_dict


def get_db_names():
    client = MongoClient('localhost', 27017)
    ret = client.list_database_names()
    client.close()
    return ret


class KragleDB:

    def __init__(self, db_name='EUR_USD_raw'):
        self.logger = logging.getLogger('kragle')
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db_name]
        self.db_name = db_name
        self.cheked = {}
        self.dataset_suffix = '__dataset'
        self.check_db_date_index()

    def close(self):
        self.client.close()

    # TODO add test
    def check_db_date_index(self):
        inst_and_per = self.get_instruments_and_periods()
        for instrument in inst_and_per:
            periods = inst_and_per[instrument]
            for period in periods:
                self.check_date_index(instrument, period)
                # self.db[instrument][period].create_index([('date', -1)], unique=True)

    # TODO add test
    def check_date_index(self, instrument, period):
        key = instrument + '.' + period
        if key not in self.cheked:
            self.logger.info('Checking "date" index for instrument [{}] period [{}]'.format(instrument, period))
            self.db[instrument][period].create_index([('date', -1)], unique=True)
            self.cheked[key] = True

    def get_instruments(self):
        """
        @return: list of instruments names. Example ['EUR/USD', 'JPY/EUR', 'EUR/UK']

        """
        return list(self.get_instruments_and_periods())

    def get_periods(self, instrument='EUR/USD'):
        """
        @return: list of periods names in the selected instrument
        """
        return self.get_instruments_and_periods().get(instrument, [])

    def get_instruments_and_periods(self):
        """
        @return: Dict with instruments as keys and a list of periods as value
         example: {'EUR/USD': ['m1', 'm5', 'm30'], 'B': ['1', '2'], 'C': ['1', '2', '3', '4']}

        """
        names = self.db.list_collection_names()
        return dot_names_to_dict(names)

    def get(self, instrument, period, from_date=None, to_date=None, limit=100000):
        """

        @param instrument: instrument name. Example: 'EUR/USD'
        @param period: period name. Example: 'm5'
        @param from_date: filter beginning with this datetime
        @param to_date: filter stop with this datetime
        @param limit: max number of results. Default: 100000
        @return: A pandas DataFrame with filtered records found
        """
        db = self.db[instrument][period]
        date_filter = self.query_date_filter(from_date, to_date)
        data = list(db.aggregate([
            {'$match': date_filter},
            {'$sort': {'date': 1}},
            {'$limit': limit},
        ]))
        return pd.DataFrame(data)

    def get_one(self, instrument, period, date):
        """

        @param instrument: instrument name
        @param period: period name
        @param date: single datetime to find in date column
        @return: a single record selected by date column
        """
        return self.db[instrument][period].find_one({'date': date})

    def query_date_filter(self, from_date, to_date):
        """
        @param from_date: filter beginning with this date
        @param to_date: filter beginning with this date
        @return: a mongodb query for a date field.
        Example {'date': {'$gte': from_date, '$lte': to_date}} or {} if no date given
        """
        date_filter = {}
        inner = {}
        if (from_date is not None) and (type(from_date) is not dt.datetime):
            raise ValueError('from_date must be None or a datetime.datetime not {} '.format(type(from_date)))
        if (to_date is not None) and (type(to_date) is not dt.datetime):
            raise ValueError('to_date must be None or a datetime.datetime not {} '.format(type(to_date)))
        if from_date is not None:
            inner['$gte'] = from_date
        if to_date is not None:
            inner['$lte'] = to_date
        if inner != {}:
            date_filter['date'] = inner
        return date_filter

    def drop_period(self, instrument, period):
        return self.db[instrument][period].drop()

    def drop_instrument(self, instrument):
        d = self.get_instruments_and_periods()
        for period in d[instrument]:
            self.drop_period(instrument, period)

    def drop_db(self):
        self.client.drop_database(self.db_name)

    def fetch_dataframe(self, df, instrument, period):
        """
        Fetch the dataframe in the DB using 'date' to replace existing elements o creating a new one

        Args:
            df (pandas.DataFrame): the dataframe to fetch
            instrument (String): the forex instrument ('EUR/USD', 'EUR/JPY' ... )
            period (String): the instrument period ('m1', 'm5', 'm15' ... )
        """

        for record in df.to_dict("records"):
            self.insert(instrument, period, record)

    def insert(self, instrument, period, record):
        self.check_date_index(instrument, period)
        self.db[instrument][period].replace_one({'date': record['date']}, record, upsert=True)

    def create_dataset(self, n, instrument, periods, history_len, from_date, to_date):

        return []

    def save_dataset(self, dataset_name, dataset):
        if not dataset_name.endswith(self.dataset_suffix):
            dataset_name += self.dataset_suffix
        db = self.client[self.db_name]
        db.drop_collection(dataset_name)
        db[dataset_name].create_index([('date', -1)], unique=True)
        db[dataset_name].insert_many(dataset)



    def get_base_date_list(self, n, instrument, periods, from_date, to_date):
        period_0 = self.db[instrument][periods[0]]
        date_filter = self.query_date_filter(from_date, to_date)
        base_date_list = list(period_0.find(date_filter, {'date': 1, '_id': 0}))
        if len(base_date_list) < n:
            raise ValueError('Not enough data to fulfill the request in period ' + periods[0])
        return base_date_list

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

    def get_by_date(self, instrument, period,  from_date, to_date):
        return self.db[instrument][period].aggregate([
            {'$match': {'date': {'$gte': from_date, '$lte': to_date}}},
            {'$sort': {'date': -1}},
        ])

    def get_candles(self, instrument, period,  to_date, n):
        values =  list(self.db[instrument][period].aggregate([
            {'$match': {'date': {'$lte': to_date}}},
            {'$sort': {'date': -1}},
            {'$limit': n},
        ]))

        last_candle = self.aggregate_candle( instrument,  values[0]['date'], to_date)
        values[0] = last_candle
        return values

    def get_normalized_period(self, instrument, period,  to_date, n):
        res = []
        old = None
        self.logger.info(period)
        for v in self.get_candles(instrument, period, to_date, n + 1):
            if old != None:
                tmpbid = (v['bidopen'] - old['bidopen']) / kutils.normalizer[period]['bidopen']
                tmptick = v['tickqty'] / kutils.normalizer[period]['tickqty']
                res.append([tmpbid, tmptick])
            old = v
        return res

    def get_normalized_periods(self, instrument='EUR/USD', periods = ['m1', 'm5', 'm30', 'H2', 'H8', 'D1'],  to_date=None, n=10):
        res = []
        for period in periods:
            res.append(self.get_normalized_period(instrument, period, to_date, n))

        return res

    def get_sample(self, instrument='EUR/USD', periods = ['m1', 'm5', 'm30', 'H2', 'H8', 'D1'],  to_date=None, n=10, pips=15):
        res = {
            'date': to_date,
            'x': self.get_normalized_periods(instrument, periods, to_date, n),
            'y': self.get_action_from_future(instrument=instrument, date=to_date, pips=pips)
        }
        return res

    def get_action_from_future(self, instrument='EUR/USD',  date=None, pips=15, limit=60):
        res = kutils.Action.HOLD.value
        values = self.db[instrument]['m1'].aggregate([
            {'$match': {'date': {'$gte': date}}},
            {'$sort': {'date': 1}},
            {'$limit': limit},
        ])
        base = values.next()
        for v in values:
            if ((v['bidhigh']-base['bidopen']) / kutils.PIP) > pips:
                res = kutils.Action.BUY.value
                break
            if ((base['bidopen']-v['bidlow']) / kutils.PIP) > pips:
                res = kutils.Action.SELL.value
                break
        return res

    def aggregate_candle(self, instrument,  from_date, to_date):
        values = self.db[instrument]['m1'].aggregate([
            {'$match': {'date': {'$gte': from_date, '$lte': to_date}}},
            {'$sort': {'date': 1}},
        ])
        v = values.next()
        res = { 'date': v['date'],
                'bidopen': v['bidopen'],
                'bidclose': v['bidclose'],
                'bidhigh': v['bidhigh'],
                'bidlow': v['bidlow'],
                'askopen': v['askopen'],
                'askclose': v['askclose'],
                'askhigh': v['askhigh'],
                'asklow': v['asklow'],
                'tickqty': v['tickqty']}
        for v in values:
            res['bidclose'] = v['bidclose']
            res['askclose'] = v['askclose']
            res['tickqty'] += v['tickqty']
            if res['bidhigh'] < v['bidhigh']:
                res['bidhigh'] = v['bidhigh']
            if res['askhigh'] < v['askhigh']:
                res['askhigh'] = v['askhigh']
            if res['bidlow'] > v['bidlow']:
                res['bidlow'] = v['bidlow']
            if res['asklow'] > v['asklow']:

                res['asklow'] = v['asklow']

        return res;

    def get_date_list(self, instrument, period, from_date, to_date):
        date_filter = self.query_date_filter(from_date, to_date)
        return list(self.db[instrument][period].aggregate([
            {'$match': date_filter},
            {'$sort': {'date': 1}},
            {'$project': {'date': 1, '_id': 0}},
        ]))


    def duplicate_db(self,
                     dbname,
                     instrument='EUR/USD',
                     periods=['m1', 'm5', 'm30', 'H2', 'H8'],
                     fields=['date', 'bidopen', 'tickqty'],
                     from_date=None,
                     to_date=None):  # date field must be present
        """
        Duplicate a instrument DB. Can be selected which periods to duplicate,
        which fields and which period of time

        @param dbname: new DB name
        @param instrument: instrument name. Default: EUR/USD
        @param periods: list of periods to duplicate. Default: ['m1', 'm5', 'm30', 'H2', 'H8']
        @param fields: list of fields to duplicate. Default: ['date', 'bidopen', 'tickqty']
        @param from_date: duplicate from this datetime
        @param to_date: duplicate to this datetime
        @return: new duplicated KragleDB
        """
        client = MongoClient('localhost', 27017)
        db = client[dbname]
        size = 100
        filter_date = self.query_date_filter(from_date, to_date)
        filter_fields = {'_id': 0, 'date': 1}
        for field in fields:
            filter_fields[field] = 1
        for period in periods:
            self.logger.info('Duplicating period {}'.format(period))
            db[instrument][period].drop()
            values = self.db[instrument][period].find(filter_date, filter_fields)
            val_list = []
            for value in values:
                val_list.append(value)
                if len(val_list) >= size:
                    db[instrument][period].insert_many(val_list)
                    val_list = []
            if len(val_list) > 0:
                db[instrument][period].insert_many(val_list)
        return KragleDB(dbname)

    def calc_mean_stddev(self, instrument, period,  from_date, to_date):
        values = self.db[instrument][period].aggregate([
            {'$match': {'date': {'$gte': from_date, '$lte': to_date}}},
        ])
        old = None
        self.logger.info(instrument)
        b_calc = kutils.MeanStdDevCalculator()
        t_calc = kutils.MeanStdDevCalculator()
        tmp = 0
        for v in values:
            if old != None:
                tmp = (v['bidopen']-old['bidopen'])/kutils.normalizer[period]['bidopen']
                b_calc.add(tmp)
                t_calc.add(v['tickqty']/kutils.normalizer[period]['tickqty'])
            old = v
        res = {}
        res['bidopen-mean'] = b_calc.get_mean()
        res['bidopen-stddev'] = b_calc.get_stddev()
        res['tickqty-mean'] = t_calc.get_mean()
        res['tickqty-stddev'] = t_calc.get_stddev()
        return res
