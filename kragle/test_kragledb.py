import datetime as dt

import pandas as pd
import pytest

from kragle import KragleDB
import kragle.utils as kutils


def __test_db_setup(db, periods, filename):
    kdb = KragleDB(db)
    kdb.client.drop_database(kdb.dbname)
    for period in periods:
        df = kdb.dataframe_read_json(r'kragle/test_data/' + period + filename + '.json')
        kdb.fetch_dataframe(df, 'EUR/USD', period)
    return kdb


def __test_db_teardown(kdb):
    kdb.client.drop_database(kdb.dbname)
    kdb.close()


@pytest.fixture(scope="module")
def kdb():
    print('>> Setup kdb << ', end='')
    dbname = 'kragle_test'
    periods = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H8']
    filename = '_test'
    kdb = __test_db_setup(dbname, periods, filename)
    yield kdb
    print(">> Teardown kdb << ", end='')
    __test_db_teardown(kdb)


@pytest.fixture(scope="module")
def kdb_future():
    print('>> Setup kdb future << ', end='')
    dbname = 'kragle_test_future'
    periods = ['m5']
    filename = '_future_test'
    kdb = __test_db_setup(dbname, periods, filename)
    yield kdb
    print(">> Teardown kdb future << ", end='')
    __test_db_teardown(kdb)


def test_create_dataset_raise_date_order(kdb):
    """test start date after end date"""
    start = dt.datetime(2018, 11, 28, 22, 50)
    end = dt.datetime(2018, 11, 27, 22, 50)
    with pytest.raises(ValueError, match=r".*before.*"):
        dataset = kdb.create_dataset(2, 'EUR/USD', ['m1', 'm5'], 4, start, end)


def test_create_dataset_raise_few_data(kdb):
    '''test start date after end date'''
    start = dt.datetime(2018, 10, 25, 22, 50)
    end = dt.datetime(2018, 10, 27, 22, 50)
    with pytest.raises(ValueError, match=r".*fulfill.*"):
        dataset = kdb.create_dataset(2, 'EUR/USD', ['m1', 'm5'], 4, start, end)


def test_create_dataset(kdb):
    start = dt.datetime(2018, 11, 27, 15, 50)
    end = dt.datetime(2018, 11, 27, 22, 50)
    dataset = kdb.create_dataset(2, 'EUR/USD', ['m1', 'm5'], 4, start, end)
    # test len dataset
    assert len(dataset) == 2
    # test keys in dataset
    assert 'date' in dataset[0]
    assert 'x' in dataset[0]
    assert 'y' in dataset[0]
    # test 0 element
    assert 'm1' in dataset[0]['x']
    assert 'm5' in dataset[0]['x']
    assert len(dataset[0]['x']['m1']) == 4
    assert len(dataset[0]['x']['m5']) == 4
    # test 1 element
    assert 'm1' in dataset[1]['x']
    assert 'm5' in dataset[1]['x']
    assert len(dataset[1]['x']['m1']) == 4
    assert len(dataset[1]['x']['m5']) == 4


def test_aggregate_dataframe(kdb):
    date1 = dt.datetime(2018, 11, 28, 22, 52)
    date2 = dt.datetime(2018, 11, 28, 22, 51)
    date3 = dt.datetime(2018, 11, 28, 22, 50)
    val = [
        {'date': date1, 'bidopen': 1, 'bidclose': 2, 'bidhigh': 3, 'bidlow': 4, 'askopen': 5, 'askclose': 6,
         'askhigh': 7, 'asklow': 8, 'tickqty': 9, }
        , {'date': date2, 'bidopen': 10, 'bidclose': 20, 'bidhigh': 30, 'bidlow': 40, 'askopen': 50, 'askclose': 60,
           'askhigh': 70, 'asklow': 80, 'tickqty': 90, }
        , {'date': date3, 'bidopen': 5, 'bidclose': 15, 'bidhigh': 35, 'bidlow': 25, 'askopen': 55, 'askclose': 45,
           'askhigh': 75, 'asklow': 65, 'tickqty': 85, }
    ]

    agg = kutils.aggregate_dataframe(pd.DataFrame(val))

    assert agg['date'] == date3
    assert agg['bidopen'] == 5
    assert agg['bidclose'] == 2
    assert agg['bidhigh'] == 35
    assert agg['bidlow'] == 4
    assert agg['askopen'] == 55
    assert agg['askclose'] == 6
    assert agg['askhigh'] == 75
    assert agg['asklow'] == 8
    assert agg['tickqty'] == 184


def test_create_value(kdb):
    m1date = dt.datetime(2018, 11, 27, 22, 0)
    val = kdb.create_value( 'EUR/USD', ['m1', 'm5'], 8, m1date)
    assert val['x']['m5'][0]['tickqty'] == 159

    m1date = dt.datetime(2018, 11, 27, 17, 26)
    val = kdb.create_value( 'EUR/USD', ['m1', 'm5'], 8, m1date)
    assert val['x']['m5'][0]['tickqty'] == 707
    assert val['x']['m5'][0]['bidopen'] == 1.12894
    assert val['x']['m5'][0]['bidclose'] == 1.12921
    assert val['x']['m5'][0]['bidhigh'] == 1.12923
    assert val['x']['m5'][0]['bidlow'] == 1.12894
    assert val['x']['m5'][0]['askopen'] == 1.12909
    assert val['x']['m5'][0]['askclose'] == 1.12935
    assert val['x']['m5'][0]['askhigh'] == 1.12937
    assert val['x']['m5'][0]['asklow'] == 1.12908


def test_create_value_hour(kdb):
    m1date = dt.datetime(2018, 11, 27, 15, 2)
    val = kdb.create_value( 'EUR/USD', ['m1', 'm5', 'H1'], 8, m1date)
    assert val['x']['m5'][0]['tickqty'] == 692
    assert val['x']['m5'][0]['bidopen'] == 1.13195
    assert val['x']['m5'][0]['bidclose'] == 1.1323
    assert val['x']['m5'][0]['bidhigh'] == 1.13233
    assert val['x']['m5'][0]['bidlow'] == 1.13192
    assert val['x']['m5'][0]['askopen'] == 1.13211
    assert val['x']['m5'][0]['askclose'] == 1.13245
    assert val['x']['m5'][0]['askhigh'] == 1.13247
    assert val['x']['m5'][0]['asklow'] == 1.1320700000000001
    # Hour test
    assert val['x']['H1'][0]['tickqty'] == 692
    assert val['x']['H1'][0]['bidopen'] == 1.13195
    assert val['x']['H1'][0]['bidclose'] == 1.1323
    assert val['x']['H1'][0]['bidhigh'] == 1.13233
    assert val['x']['H1'][0]['bidlow'] == 1.13192
    assert val['x']['H1'][0]['askopen'] == 1.13211
    assert val['x']['H1'][0]['askclose'] == 1.13245
    assert val['x']['H1'][0]['askhigh'] == 1.13247
    assert val['x']['H1'][0]['asklow'] == 1.1320700000000001


def test_insert_future(kdb_future):
    start_date = dt.datetime(2018, 11, 23, 21, 30)
    end_date = dt.datetime(2018, 11, 23, 23, 10)
    kdb_future.insert_future('EUR/USD', 'm5', start_date, end_date, field='bidopen', d=12, r=2)
    val = kdb_future.get_instrument_value('EUR/USD', 'm5', start_date)
    assert val['future'] == (13 + 14 + 15 + 16 + 17) / 5
    val = kdb_future.get_instrument_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=5))
    assert val['future'] == (14 + 15 + 16 + 17 + 0) / 5 - val['bidopen']
    val = kdb_future.get_instrument_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=10))
    assert val['future'] == (15 + 16 + 17 + 0 + 0) / 5 - val['bidopen']
    ##########
    kdb_future.insert_future('EUR/USD', 'm5', start_date, end_date, field='bidopen', d=10, r=1)
    val = kdb_future.get_instrument_value('EUR/USD', 'm5', start_date)
    assert val['future'] == (9 + 13 + 14) / 3 - val['bidopen']
    val = kdb_future.get_instrument_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=5))
    assert val['future'] == (13 + 14 + 15) / 3 - val['bidopen']
    ##########
    kdb_future.insert_future('EUR/USD', 'm5', start_date, end_date, field='bidopen', d=3, r=1)
    val = kdb_future.get_instrument_value('EUR/USD', 'm5', start_date)
    assert val['future'] == (9 + 4 + 2) / 3 - val['bidopen']


def test_calc_instruments_and_periods(kdb):
    l = ['A.1', 'A.2', 'A.3', 'B.1', 'B.2', 'C.1', 'C.2', 'C.3', 'C.4']
    res = kdb._calc_instruments_and_periods(l)
    assert res['A'] == ['1', '2', '3']
    assert res['B'] == ['1', '2']
    assert res['C'] == ['1', '2', '3', '4']
    assert list(res) == ['A', 'B', 'C']

def test_get_instrument_raise(kdb):
    with pytest.raises(ValueError, match=r".*datetime.*"):
        dataset = kdb.get_instrument( 'EUR/USD','m1', 'start', 'end')