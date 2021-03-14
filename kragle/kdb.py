import random
import datetime as dt
import logging
from collections import deque

import pandas as pd
from pymongo import MongoClient
import kragle.utils as kutils

from kragle.utils import PIP
from utils import dot_names_to_dict


def get_db_names():
    client = MongoClient('localhost', 27017)
    ret = client.list_database_names()
    client.close()
    return ret


class KragleDB:

    def __init__(self, db_name='forex_raw'):
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

    def get_periods(self, instrument):
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

    def get_datasets(self):
        """
        @return: a list of dataset name
        """
        names = self.db.list_collection_names()
        ret = []
        for name in names:
            if name.endswith(self.dataset_suffix):
                ret.append(name.removesuffix(self.dataset_suffix))
        return ret

    def get_dataset(self, ds_name):
        """
        @param ds_name: dataset name
        @return: a dataset as a list of values
        example [{'date': ..., 'x':{'m1':[{'date': ..., 'value': 1.1212},...], 'm5':[...]}, 'y':0 }, ...]
        """
        if not ds_name.endswith(self.dataset_suffix):
            ds_name += self.dataset_suffix
        return list(self.db[ds_name].find({}))

    def create_dataset(self, n, instrument, periods, history_len, from_date, to_date):
        if from_date >= to_date:
            raise ValueError('Date error, start date must be before end date.')
        base_date_list = self.get_base_date_list(n, instrument, periods, from_date, to_date)
        ret = []
        for i in range(n):
            tmp = base_date_list.pop(random.randrange(len(base_date_list)))
            ret.append(self.create_train_value(instrument, periods, history_len, tmp['date']))
        return ret

    def save_dataset(self, dataset_name, dataset):
        if not dataset_name.endswith(self.dataset_suffix):
            dataset_name += self.dataset_suffix
        db = self.client[self.db_name]
        db.drop_collection(dataset_name)
        db[dataset_name].create_index([('date', -1)], unique=True)
        db[dataset_name].insert_many(dataset)

    def create_and_save_dataset(self, dataset_name, n, instrument, periods, history_len, from_date, to_date):
        dataset = self.create_dataset(n, instrument, periods, history_len, from_date, to_date)
        self.save_dataset(dataset_name, dataset)

    def get_base_date_list(self, n, instrument, periods, from_date, to_date):
        period_0 = self.db[instrument][periods[0]]
        date_filter = self.query_date_filter(from_date, to_date)
        base_date_list = list(period_0.find(date_filter, {'date': 1, '_id': 0}))
        if len(base_date_list) < n:
            raise ValueError('Not enough data to fulfill the request in period ' + periods[0])
        return base_date_list

    def create_train_value(self, instrument, periods, history_len, m1date, future_period='m5'):
        train_value = {'date': m1date, 'x': {}, 'y': None}
        for period in periods:
            history_list = self.get_history_bidopen(instrument, period, history_len, m1date)
            if len(history_list) < history_len:
                raise ValueError('Not enough data to fulfill the request in date {} - period {}'.format(m1date, period))
            if (period == 'm1') & (history_list[0]['date'] != m1date):
                raise ValueError('Date {} not in requested instrument {} period {}'.format(m1date, instrument, period))
            # future

            train_value['x'][period] = history_list
            # tickqty
            if period == periods[0]:
                train_value['x']['tickqty'] = self.get_history_tickqty(instrument, period, history_len, m1date)
            if period == future_period:
                val = self.get_one(instrument, period, history_list[0]['date'])
                if 'future' in val:
                    train_value['y'] = val['future']
                else:
                    raise ValueError(
                        'Future not present in date {} instrument {} period {}'.format(history_list[0]['date'],
                                                                                       instrument,
                                                                                       period))
        return train_value

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

    def get_date_list(self, instrument, period, from_date, to_date):
        date_filter = self.query_date_filter(from_date, to_date)
        return list(self.db[instrument][period].aggregate([
            {'$match': date_filter},
            {'$sort': {'date': 1}},
            {'$project': {'date': 1, '_id': 0}},
        ]))

    def insert_future(self, instrument, period, from_date=None, to_date=None, field='bidopen', future_len=50,
                      limit=15 * PIP):
        """ insert calculated future value column in the selected instrument.period
        
        @param instrument: 
        @param period: 
        @param from_date: 
        @param to_date: 
        @param field: Defaults to bidopen.
        @param future_len: Defaults to 50.
        @param limit: Defaults to 15 PIP.
        @return: 
        """
        date_filter = self.query_date_filter(from_date, to_date)
        values = self.db[instrument][period].aggregate([
            {'$match': date_filter},
            {'$sort': {'date': 1}},
        ])
        ft = FutureTool(field=field, future_len=future_len, limit=limit)
        for value in values:
            oldvalue_future = ft.calc(value)
            if oldvalue_future is not None:
                old_value, future = oldvalue_future
                self.db[instrument][period].update_one(
                    {'_id': old_value['_id']},
                    {'$set': {"future": future.value}},
                    upsert=False)

    def duplicate_db(self,
                     dbname,
                     instrument='EUR/USD',
                     periods=['m1', 'm5', 'm30', 'H2', 'H8'],
                     fields=['date', 'bidopen', 'tickqty', 'future'],
                     from_date=None,
                     to_date=None):  # date field must be present
        """
        Duplicate a instrument DB. Can be selected which periods to duplicate,
        which fields and which period of time

        @param dbname: new DB name
        @param instrument: instrument name. Default: EUR/USD
        @param periods: list of periods to duplicate. Default: ['m1', 'm5', 'm30', 'H2', 'H8']
        @param fields: list of fields to duplicate. Default: ['date', 'bidopen', 'tickqty', 'future']
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


class FutureTool:

    def __init__(self, field='bidopen', future_len=50, limit=15):
        """
        Tool Class for future calculation

        @param field: column key name field to use for future calculation
        @param future_len: number of value tu use for future calculation
        @param limit:
        """
        self.field = field
        self.future_len = future_len
        self.limit = limit
        self.deque = deque()

    def calc_collection(self, coll):
        res = []
        for record in coll:
            tuple_value_future = self.calc(record)
            if tuple_value_future is not None:
                res.append(tuple_value_future)
        return res

    def calc(self, record):
        """
        add a record in the internal queue and return a record with future calculated (only if the number of inserted
        records is at least self.future_len else None)
        @param record: add a record in the internal queue
        @return: return a value with future calculated e column added but only if the number of inserted records
        is at least self.future_len else None
        """
        self.deque.append(record)
        ret = None
        if len(self.deque) > self.future_len:
            ret = self._calc()
        return ret

    def _calc(self):
        action = kutils.Action.HOLD
        record = self.deque.popleft()
        field_value = record[self.field]
        for v in self.deque:
            if (v[self.field] - field_value) >= self.limit:
                action = kutils.Action.BUY
                break
            if (v[self.field] - field_value) <= (-1 * self.limit):
                action = kutils.Action.SELL
                break
        return record, action


