import datetime as dt
import math
import random
from enum import Enum

from _plotly_utils.colors import n_colors
from dash import dash_table
import pandas as pd
import logging
import numpy as np
import tensorflow as tf

logger = logging.getLogger('kragle')
instruments = ['USD/SEK', 'EUR/USD',
               'USD/NOK', 'USD/MXN', 'USD/ZAR', 'USD/HKD', 'USD/TRY',
               'USD/ILS', 'USD/CNH', 'XAU/USD',
               'XAG/USD', 'BTC/USD', 'BCH/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD']

periods = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'D1']

normalizer = {
    'm1': {'bidopen': 0.00020, 'tickqty': 400},
    'm5': {'bidopen': 0.00030, 'tickqty': 2000},
    'm30': {'bidopen': 0.00075, 'tickqty': 12_000},
    'H2': {'bidopen': 0.0015, 'tickqty': 40_000},
    'H8': {'bidopen': 0.0030, 'tickqty': 160_000},
    'D1': {'bidopen': 0.0045, 'tickqty': 400_000},
}

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

# EUR/USD pip
PIP = .0001
FIELDS = ['date', 'bidopen', 'bidclose', 'bidhigh', 'bidlow', 'askopen', 'askclose', 'askhigh', 'asklow', 'tickqty']


class Action(Enum):
    BUY = 2
    SELL = 0
    HOLD = 1


# TODO: maybe remove this function
def random_date(start, end):
    """Generate a random datetime between `start` and `end` in minutes"""
    return start + dt.timedelta(
        # Get a random amount of seconds between `start` and `end`
        minutes=random.randint(0, int((end - start).total_seconds() / 60)),
    )


def aggregate_dataframe(df):
    tmp_sum = df[['tickqty']].sum()
    res = {'date': df.iloc[-1]['date'],
           'bidopen': df.iloc[-1]['bidopen'],
           'tickqty': tmp_sum['tickqty'],
           }
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


class Percentage:

    def __init__(self):
        self.total = 0
        self.sell = 0
        self.hold = 0
        self.buy = 0

    def add(self, value):
        if value['y'] == 0:
            self.sell += 1
        if value['y'] == 1:
            self.hold += 1
        if value['y'] == 2:
            self.buy += 1
        self.total += 1

    def get_percentage(self):
        return (self.sell / self.total, self.hold / self.total, self.buy / self.total)


def dataset_to_dataframe_dict(ds):
    res = {}
    for name, value_list in ds['x'].items():
        res[name] = pd.DataFrame(value_list)
    return res


class MeanStdDevCalculator:

    def __init__(self):
        self.n = 0
        self.mean = 0
        self.stddev = 0

    def add(self, value):
        self.n = self.n + 1
        self.mean += value
        self.stddev += value * value

    def get_mean(self):
        return self.mean / self.n

    def get_stddev(self):
        return math.sqrt(self.stddev / self.n - self.get_mean() * self.get_mean())


def calc_mean_stddev_on_m1(db):
    """
    Calc mean and stddev on bidopen and tickqty on m1 period
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
        style_table={'height': '150px', 'overflow': 'auto'}

    )


def get_fired_input_id(ctx):
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    return button_id


def dataframe_to_json(df, path):
    """
    Write the dataframe to a file (specified with path) in 'records' format
    while eliminating '_id' column derived from mongoDB

    Args:
        df (DataFrame): A Pandas DataFrame to write
        path ([type]): Path to file
    """
    df.drop('_id', axis=1).to_json(path, orient='records', date_format='iso')


def dot_names_to_dict(name_list):
    """
    given a list like ['A.1', 'A.2', 'A.3', 'B.1', 'B.2', 'C.1', 'C.2', 'C.3', 'C.4']
    return a dict {'A': ['1', '2', '3'], 'B': ['1', '2'], 'C': ['1', '2', '3', '4']}

    """
    res = {}
    for name in name_list:
        try:
            l = name.split('.')
            if len(l) == 2:
                val = res.get(l[0], [])
                val.append(l[1])
                res[l[0]] = val
        except:
            pass
    return res

n_classes = 3
class AccuracyCallback(tf.keras.callbacks.Callback):

    def __init__(self, test_data):
        self.test_data = test_data


    def on_epoch_end(self, epoch, logs=None):
        x_data, y_data = self.test_data

        correct = 0
        incorrect = 0

        x_result = self.model.predict(x_data, verbose=0)
        x_numpy = []

        class_correct = [0] * n_classes
        class_incorrect = [0] * n_classes

        for i in range(len(x_data)):
            x = x_data[i]
            y = y_data[i]

            res = x_result[i]


            pred_label = np.argmax(res)

            if(pred_label == y):
                x_numpy.append(["cor:", str(y), str(res), str(pred_label)])
                class_correct[y] += 1
                correct += 1
            else:
                x_numpy.append(["inc:", str(y), str(res), str(pred_label)])
                class_incorrect[y] += 1
                incorrect += 1

        print("")
        print("\tCorrect: %d" %(correct))
        print("\tIncorrect: %d" %(incorrect))

        for i in range(n_classes):
            tot = float(class_correct[i] + class_incorrect[i])
            class_acc = -1
            if (tot > 0):
                class_acc = float(class_correct[i]) / tot

            print("\t%s: %.3f" %(i, class_acc))

        acc = float(correct) / float(correct + incorrect)

        print("\tCurrent Network Accuracy: %.3f" %(acc))