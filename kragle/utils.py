import datetime as dt
import random
import pandas as pd


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


def dataframe_read_json(path):
    """
    Pandas read_json with orient='records'

    Args:
        path (String): path to file

    Returns:
        [DataFrame]: pandas dataframe
    """
    return pd.read_json(path, orient='records')


def dataset_to_dataframe(ds):
    res = {}
    periods = list(ds['x'])
    for period in periods:
        value_list = ds['x'][period]
        for val in value_list:
            d = res.get(val['date'], {})
            d['date'] = val['date']
            d[period] = val['bidopen']
            if period == 'm1':
                d['tickqty'] = val['tickqty']
            res[val['date']] = d
    return pd.DataFrame(res.values())
