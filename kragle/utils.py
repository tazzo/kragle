import datetime as dt
import math
import random
import json

from pymongo import MongoClient
import dash_table
import pandas as pd
import logging
import fxcmpy

from kragle.db import KragleDB

logger = logging.getLogger('kragle')
instruments = ['USD/SEK', 'EUR/USD',
               'USD/NOK', 'USD/MXN', 'USD/ZAR', 'USD/HKD', 'USD/TRY',
               'USD/ILS', 'USD/CNH', 'XAU/USD',
               'XAG/USD', 'BTC/USD', 'BCH/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD']

periods = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'D1']

time_in_force = ['IOC', 'GTC', 'FOK', 'DAY']

period_to_minutes = {
    'm1': 1,
    'm5': 5,
    'm15': 15,
    'm30': 30,
    'H1': 60,
    'H2': 120,
    'H3': 180,
    'H4': 240,
    'H6': 360,
    'H8': 480,
    'D1': 1440
}


# TODO: maybe remove this function
def random_date(start, end):
    """Generate a random datetime between `start` and `end` in minutes"""
    return start + dt.timedelta(
        # Get a random amount of seconds between `start` and `end`
        minutes=random.randint(0, int((end - start).total_seconds() / 60)),
    )


def aggregate_dataframe(df):
    sum = df[['tickqty']].sum()
    res = {'date': df.iloc[-1]['date'],
           'bidopen': df.iloc[-1]['bidopen'],
           'tickqty': sum['tickqty'],
           }
    return res


def dot_names_to_dict(name_list):
    """
    given a list like ['A.1', 'A.2', 'A.3', 'B.1', 'B.2', 'C.1', 'C.2', 'C.3', 'C.4']
    return a dict {'A': ['1', '2', '3'], 'B': ['1', '2'], 'C': ['1', '2', '3', '4']}

    """
    res = {}
    for name in name_list:
        try:
            l = name.split('.')
            val = res.get(l[0], [])
            if len(l) == 2:
                val.append(l[1])
                res[l[0]] = val
        except:
            pass
    return res


def dataframe_from_json(path):
    """
    Pandas read_json with orient='records'

    Args:
        path (String): path to file

    Returns:
        [DataFrame]: pandas dataframe
    """
    return pd.read_json(path, orient='records')


def dataset_to_dataframe_dict(ds):
    res = {}
    for name, value_list in ds['x'].items():
        res[name] = pd.DataFrame(value_list)
    return res


def prune_and_index_db(db):
    for coll_name in db.list_collection_names():
        logger.info('Prune {}'.format(coll_name))
        l = list(db[coll_name]
            .aggregate([
            {"$group": {'_id': {"date": '$date'}, "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}},
            {'$sort': {"_id": 1}},

        ]))
        for val in l:
            one = db[coll_name].find_one({'date': val['_id']['date']})
            db[coll_name].delete_one({'_id': one['_id']})
        db[coll_name].create_index([('date', -1)], unique=True)


class MeanStdDevCalculator:

    def __init__(self):
        self.n = 0
        self.mean = 0
        self.stddev = 0

    def add(self, value):
        self.n = self.n + 1
        self.mean = self.mean + value
        self.stddev = self.stddev + value * value

    def get_mean(self):
        return self.mean / self.n

    def get_stddev(self):
        return math.sqrt(self.stddev / self.n - self.get_mean() * self.get_mean())


def calc_mean_stddev_on_m1(db):
    """
    Calc mean and stddev on bidopen and tickqty on H1 period
    """
    d = dot_names_to_dict(db.list_collection_names())
    res = {}
    for instrument in list(d):
        logger.info(instrument)
        res[instrument] = {}
        period = 'm1'
        b_calc = MeanStdDevCalculator()
        t_calc = MeanStdDevCalculator()
        for v in db[instrument][period].find({}):
            b_calc.add(v['bidopen'])
            t_calc.add(v['tickqty'])

        res[instrument]['bidopen-mean'] = b_calc.get_mean()
        res[instrument]['bidopen-stddev'] = b_calc.get_stddev()
        res[instrument]['tickqty-mean'] = t_calc.get_mean()
        res[instrument]['tickqty-stddev'] = t_calc.get_stddev()
    return res


def table_from_dataframe(df):
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        style_table={'height': '200px', 'overflow': 'auto'}

    )


def get_fired_input_id(ctx):
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    return button_id


def fetch_candles(start, end, kdb, fxcon, instrument='EUR/USD', period='m1'):
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
        df = fxcon.get_candles(instrument, period=period, start=tmpstart, end=tmpend, with_index=False)
        print('instrument: ' + instrument + ' period: ' + period + ' delta: ' + str(delta) + ' from: ' + str(
            tmpstart) + ' to:' + str(tmpend) + ' n: ' + str(df.size))
        # if df.size > 0:
        #     df_json = df.T.to_json()
        #     df_json_list = json.loads(df_json).values()
        #     l = list(df_json_list)
        #     for tmp in l:
        #         tmp['date'] = dt.datetime.fromtimestamp(tmp['date'] / 1e3)
        #     db[instrument][period].insert_many(df_json_list)
        kdb.fetch_dataframe(df, instrument, period)

        if tmpend == end:
            loop = False
        else:
            tmpstart = tmpstart + dt.timedelta(delta)
            tmpend = tmpstart + dt.timedelta(delta)
            if tmpend > end:
                tmpend = end
        print('enf loop')



def fetch_instrument(start, end, instrument='EUR/USD', config_file='fxcm.cfg', dbname='tmp'):
    kdb = KragleDB('tmp')
    fxcon = fxcmpy.fxcmpy(config_file='fxcm.cfg')
    for p in periods:
        print('Fetching ' + instrument + ' period ' + p)
        fetch_candles(start, end, kdb, fxcon, instrument=instrument, period=p)
    fxcon.close()
