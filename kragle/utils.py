import datetime as dt
import random
import pandas as pd


def random_date(start, end):
    """Generate a random datetime between `start` and `end` in minutes"""
    return start + dt.timedelta(
        # Get a random amount of seconds between `start` and `end`
        minutes=random.randint(0, int((end - start).total_seconds() / 60)),
    )


def aggregate_dataframe(df):
    high = df[['bidhigh', 'askhigh']].max()
    low = df[['bidlow', 'asklow']].min()
    sum = df[['tickqty']].sum()
    res = {'date': df.iloc[-1]['date'],
           'bidopen': df.iloc[-1]['bidopen'],
           'bidclose': df.iloc[0]['bidclose'],
           'bidhigh': high['bidhigh'],
           'bidlow': low['bidlow'],
           'askopen': df.iloc[-1]['askopen'],
           'askclose': df.iloc[0]['askclose'],
           'askhigh': high['askhigh'],
           'asklow': low['asklow'],
           'tickqty': sum['tickqty'],
           }
    return res


def dot_names_to_dict(name_list):
    res = {}
    for name in name_list:
        try:
            l = name.split('.')
            val = res.get(l[0], [])
            if len(l)==2:
                val.append(l[1])
                res[l[0]] = val
        except:
            pass
    return res


def dataframe_read_json(path):
    """
    Pandas read_json with orient='records'

    Args:
        path (String): path to file

    Returns:
        [DataFrame]: pandas dataframe
    """
    return pd.read_json(path, orient='records')