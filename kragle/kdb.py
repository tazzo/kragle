import datetime as dt
import logging
from random import randrange, random

import pandas as pd
from pymongo import MongoClient
import kragle.utils as kutils
import numpy
import tensorflow as tf

from kragle.utils import dot_names_to_dict


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = delta.total_seconds() / 60
    # print('int delta ', int_delta)
    random_minutes = randrange(int_delta)
    return start + dt.timedelta(minutes=random_minutes)


def get_db_names():
    client = MongoClient('localhost', 27017)
    ret = client.list_database_names()
    client.close()
    return ret


class KragleDB:

    def __init__(self, db_name='EUR_USD_raw', instrument='EUR/USD', ds_name='Datasets'):
        self.logger = logging.getLogger('kragle')
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db_name][instrument]
        self.db_name = db_name
        self.ds = self.client[ds_name]
        self.ds_name = ds_name
        self.instrument = instrument
        self.cheked = {}
        self.check_db_date_index()

    def close(self):
        self.client.close()

    # TODO add test
    def check_db_date_index(self):
        inst_and_per = self.get_instruments_and_periods()
        for instrument in inst_and_per:
            periods = inst_and_per[instrument]
            for period in periods:
                self.check_date_index(period)
                # self.db[instrument][period].create_index([('date', -1)], unique=True)

    # TODO add test
    def check_date_index(self, period):
        key = self.instrument + '.' + period
        if key not in self.cheked:
            self.logger.info('Checking "date" index for instrument [{}] period [{}]'.format(self.instrument, period))
            self.db[period].create_index([('date', -1)], unique=True)
            self.cheked[key] = True

    def get_instruments(self):
        """
        @return: list of instruments names. Example ['EUR/USD', 'JPY/EUR', 'EUR/UK']

        """
        return list(self.get_instruments_and_periods())

    def get_periods(self):
        """
        @return: list of periods names in the selected instrument
        """
        return self.get_instruments_and_periods().get(self.instrument, [])

    def get_instruments_and_periods(self):
        """
        @return: Dict with instruments as keys and a list of periods as value
         example: {'EUR/USD': ['m1', 'm5', 'm30'], 'B': ['1', '2'], 'C': ['1', '2', '3', '4']}

        """
        names = self.client[self.db_name].list_collection_names()
        return dot_names_to_dict(names)

    def get(self, period, from_date=None, to_date=None, limit=100000):
        """

        @param period: period name. Example: 'm5'
        @param from_date: filter beginning with this datetime
        @param to_date: filter stop with this datetime
        @param limit: max number of results. Default: 100000
        @return: A pandas DataFrame with filtered records found
        """
        db = self.db[period]
        date_filter = self.query_date_filter(from_date, to_date)
        data = list(db.aggregate([
            {'$match': date_filter},
            {'$sort': {'date': 1}},
            {'$limit': limit},
        ]))
        return pd.DataFrame(data)

    def get_one(self, period, date):
        """

        @param period: period name
        @param date: single datetime to find in date column
        @return: a single record selected by date column
        """
        return self.db[period].find_one({'date': date})

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

    def drop_period(self, period):
        return self.db[period].drop()

    def drop_instrument(self):
        d = self.get_instruments_and_periods()
        for period in d[self.instrument]:
            self.drop_period(period)

    def drop_db(self):
        self.client.drop_database(self.db_name)

    def fetch_dataframe(self, df, period):
        """
        Fetch the dataframe in the DB using 'date' to replace existing elements o creating a new one

        Args:
            df (pandas.DataFrame): the dataframe to fetch
            period (String): the instrument period ('m1', 'm5', 'm15' ... )
        """

        for record in df.to_dict("records"):
            self.insert(period, record)

    def insert(self, period, record):
        self.check_date_index(period)
        self.db[period].replace_one({'date': record['date']}, record, upsert=True)

    def create_dataset(self, n, from_date, to_date, periods=['m1', 'm5', 'm30', 'H2', 'H8', 'D1'],
                       history_len=10, pips=15, limit_future=180, distribution=[0.7, 0.2, 0.1]):

        ds_name = 'pips{}hist{}fut{}'.format(pips, history_len, limit_future)
        tmp_n = 0
        dsdb = self.open_dataset(ds_name)
        while True:
            try:
                rnd_date = random_date(from_date, to_date)
                sample = self.get_sample(periods, rnd_date, history_len, pips, limit_future)
                rnd = random()
                if rnd <= distribution[0]:
                    dsdb['train'].replace_one({'date': sample['date']}, sample, upsert=True)
                    tmp_n += 1
                elif rnd <= distribution[0] + distribution[1]:
                    dsdb['valid'].replace_one({'date': sample['date']}, sample, upsert=True)
                else:
                    dsdb['test'].replace_one({'date': sample['date']}, sample, upsert=True)
                if (tmp_n % 50) == 0:
                    print('Dataset len: {}/{}'.format(tmp_n, n))
                if tmp_n >= n:
                    break
            except Exception as e:
                pass
        self.check_dataset(ds_name)

    def check_dataset(self, ds_name):
        for v in self.ds[ds_name]['valid'].find({}):
            self.ds[ds_name]['train'].delete_one({'date': v['date']})
        for v in self.ds[ds_name]['test'].find({}):
            self.ds[ds_name]['train'].delete_one({'date': v['date']})
            self.ds[ds_name]['valid'].delete_one({'date': v['date']})

    def open_dataset(self, ds_name):
        self.ds[ds_name]['train'].create_index([('date', -1)], unique=True)
        self.ds[ds_name]['valid'].create_index([('date', -1)], unique=True)
        self.ds[ds_name]['test'].create_index([('date', -1)], unique=True)
        return self.ds[ds_name]

    def get_dataset(self, ds_name):
        train_set, train_labels = [], []
        valid_set, valid_labels = [], []
        test_set, test_labels = [], []

        for v in self.ds[ds_name]['train'].find({}):
            train_set.append(numpy.array(v['x']))
            train_labels.append(v['y'] + 1)
        train_dataset = (numpy.array(train_set), numpy.array(train_labels))
        for v in self.ds[ds_name]['valid'].find({}):
            valid_set.append(numpy.array(v['x']))
            valid_labels.append(v['y'] + 1)
        valid_dataset = (numpy.array(valid_set), numpy.array(valid_labels))
        for v in self.ds[ds_name]['test'].find({}):
            test_set.append(numpy.array(v['x']))
            test_labels.append(v['y'] + 1)
        test_dataset = (numpy.array(test_set), numpy.array(test_labels))
        return train_dataset, valid_dataset, test_dataset

    def get_dataset_bytype(self, ds_name, nclass=None):
        t_set, t_labels = [], []
        if nclass is not None:
            for v in self.ds[ds_name]['test'].find({}):
                if v['y'] == nclass:
                    t_set.append(numpy.array(v['x']))
                    t_labels.append(v['y'] + 1)
            t_dataset = (numpy.array(t_set), numpy.array(t_labels))
            return t_dataset
        else:
            return self.get_dataset(ds_name)

    def get_dataset_percentage(self, ds_name, type='train'):
        p = kutils.Percentage()

        for v in self.ds[ds_name][type].find({}):
            p.add(v)
        return p.get_percentage()


    def get_base_date_list(self, n, periods, from_date, to_date):
        period_0 = self.db[periods[0]]
        date_filter = self.query_date_filter(from_date, to_date)
        base_date_list = list(period_0.find(date_filter, {'date': 1, '_id': 0}))
        if len(base_date_list) < n:
            raise ValueError('Not enough data to fulfill the request in period ' + periods[0])
        return base_date_list

    def get_history_tickqty(self, period, history_len, date):
        return self.get_history_field(period, 'tickqty', history_len, date)

    def get_history_bidopen(self, period, history_len, date):
        return self.get_history_field(period, 'bidopen', history_len, date)

    def get_history_field(self, period, field, history_len, date):
        return list(self.db[period].aggregate([
            {'$match': {'date': {'$lte': date}}},
            {'$sort': {'date': -1}},
            {'$limit': history_len},
            {'$project': {'date': 1, 'value': '${}'.format(field), '_id': 0}},
        ]))

    def get_by_date(self, period, from_date, to_date):
        return self.db[period].aggregate([
            {'$match': {'date': {'$gte': from_date, '$lte': to_date}}},
            {'$sort': {'date': -1}},
        ])

    def get_candles(self, period, to_date, n):
        values = list(self.db[period].aggregate([
            {'$match': {'date': {'$lte': to_date}}},
            {'$sort': {'date': -1}},
            {'$limit': n},
        ]))

        last_candle = self.aggregate_candle(values[0]['date'], to_date)
        values[0] = last_candle
        return values

    def get_data_period(self, period, to_date, history_len, normalized=True):
        res = []
        self.logger.info(period)
        old = None
        for v in self.get_candles(period, to_date, history_len + 1):
            if normalized:
                if old != None:
                    tmpbid = (old['bidopen'] - v['bidopen']) / kutils.normalizer[period]['bidopen']
                    tmptick = v['tickqty'] / kutils.normalizer[period]['tickqty']
                    res.append([tmpbid, tmptick])
                old = v
            else:
                res.append([v['bidopen'], v['tickqty']])
        return res

    def get_data_tensor(self, periods=['m1', 'm5', 'm30', 'H2', 'H8', 'D1'], to_date=None, history_len=10, normalized=True):
        res = []
        for period in periods:
            res.append(self.get_data_period(period, to_date, history_len, normalized=normalized))
        return res

    def get_data_period_fcxm(self, period, history_len, normalized=True):
        res = []
        old = None
        self.logger.info(period)
        for v in self.fxcon.get_candles(self.instrument, period=period, number=history_len+1, with_index=False).to_dict('records')[::-1]:
            if normalized:
                if old != None:
                    tmpbid = (old['bidopen'] - v['bidopen']) / kutils.normalizer[period]['bidopen']
                    tmptick = v['tickqty'] / kutils.normalizer[period]['tickqty']
                    res.append([tmpbid, tmptick])
                old = v
            else:
                res.append([v['bidopen'], v['tickqty']])
        return res

    def get_data_tensor_fxcm(self, periods=['m1', 'm5', 'm30', 'H2', 'H8', 'D1'], history_len=10, normalized=True):
        res = []
        import fxcmpy
        self.fxcon = fxcmpy.fxcmpy(config_file='fxcm.cfg')

        for period in periods:
            res.append(self.get_data_period_fcxm(period, history_len, normalized=normalized))

        self.fxcon.close()
        return res

    def fetch_data_tensor_fxcm(self, periods=['m1', 'm5', 'm30', 'H2', 'H8', 'D1'], history_len=10, normalized=False):
        v = self.get_data_tensor_fxcm(periods=periods, history_len=history_len, normalized=normalized)


    def get_sample(self, periods=['m1', 'm5', 'm30', 'H2', 'H8', 'D1'], to_date=None, history_len=10, pips=15,
                   limit_future=30):
        res = {
            'date': to_date,
            'x': self.get_data_tensor(periods, to_date, history_len, normalized=True),
            'y': self.get_action_from_future(date=to_date, pips=pips, limit_future=limit_future).value
        }
        return res


    def get_action_from_future(self, date=None, pips=15, limit_future=60):
        res = kutils.Action.HOLD
        values = self.db['m1'].aggregate([
            {'$match': {'date': {'$gte': date}}},
            {'$sort': {'date': 1}},
            {'$limit': limit_future},
        ])
        base = values.next()
        for v in values:
            if ((v['bidhigh'] - base['bidopen']) / kutils.PIP) > pips:
                res = kutils.Action.BUY
                break
            if ((base['bidopen'] - v['bidlow']) / kutils.PIP) > pips:
                res = kutils.Action.SELL
                break
        return res

    def aggregate_candle(self, from_date, to_date):
        values = self.db['m1'].aggregate([
            {'$match': {'date': {'$gte': from_date, '$lte': to_date}}},
            {'$sort': {'date': 1}},
        ])
        v = values.next()
        res = {'date': v['date'],
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

    def get_date_list(self, period, from_date, to_date):
        date_filter = self.query_date_filter(from_date, to_date)
        return list(self.db[period].aggregate([
            {'$match': date_filter},
            {'$sort': {'date': 1}},
            {'$project': {'date': 1, '_id': 0}},
        ]))

    def duplicate_db(self, dbname, periods=['m1', 'm5', 'm30', 'H2', 'H8', 'D1'], fields=['date', 'bidopen', 'tickqty'],
                     from_date=None, to_date=None):  # date field must be present
        """
        Duplicate a instrument DB. Can be selected which periods to duplicate,
        which fields and which period of time

        @param dbname: new DB name
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
            db[self.instrument][period].drop()
            values = self.db[period].find(filter_date, filter_fields)
            val_list = []
            for value in values:
                val_list.append(value)
                if len(val_list) >= size:
                    db[self.instrument][period].insert_many(val_list)
                    val_list = []
            if len(val_list) > 0:
                db[self.instrument][period].insert_many(val_list)
        return KragleDB(dbname)

    def calc_mean_stddev(self, period, from_date, to_date):
        values = self.db[period].aggregate([
            {'$match': {'date': {'$gte': from_date, '$lte': to_date}}},
        ])
        old = None
        self.logger.info(self.instrument)
        b_calc = kutils.MeanStdDevCalculator()
        t_calc = kutils.MeanStdDevCalculator()
        tmp = 0
        for v in values:
            if old != None:
                tmp = (v['bidopen'] - old['bidopen']) / kutils.normalizer[period]['bidopen']
                b_calc.add(tmp)
                t_calc.add(v['tickqty'] / kutils.normalizer[period]['tickqty'])
            old = v
        res = {'bidopen-mean': b_calc.get_mean(),
               'bidopen-stddev': b_calc.get_stddev(),
               'tickqty-mean': t_calc.get_mean(),
               'tickqty-stddev': t_calc.get_stddev()
               }
        return res
