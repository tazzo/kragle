import datetime as dt
import random
import pandas as pd
import logging


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


def dataset_to_dataframe_dict(ds):
    res = {}
    for name, value_list in ds['x'].items():
        res[name] = pd.DataFrame(value_list)
    return res


def prune_and_index_db(db):
    for coll_name in db.list_collection_names():
        print('Prune {}'.format(coll_name))
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
