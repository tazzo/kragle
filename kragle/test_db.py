import datetime as dt
import pytest
from kragle.db import KragleDB
import kragle.utils as kutils


def __test_db_setup(db, periods, filename):
    kdb = KragleDB(db)
    kdb.client.drop_database(kdb.dbname)
    for period in periods:
        df = kutils.dataframe_from_json(r'kragle/test_data/' + period + filename + '.json')
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
    start = dt.datetime(2018, 10, 25, 22, 50)
    end = dt.datetime(2018, 10, 27, 22, 50)
    with pytest.raises(ValueError, match=r".*fulfill.*"):
        dataset = kdb.create_dataset(2, 'EUR/USD', ['m1', 'm5'], 4, start, end)


def test_create_dataset_raise_few_data2(kdb):
    start = dt.datetime(2018, 11, 27, 17, 0)
    end = dt.datetime(2018, 11, 27, 17, 4)
    with pytest.raises(ValueError, match=r".*fulfill.*m1.*"):
        kdb.create_dataset(10, 'EUR/USD', ['m1', 'm5'], 4, start, end)
    with pytest.raises(ValueError, match=r".*fulfill.*m1.*"):
        kdb.create_dataset(6, 'EUR/USD', ['m1', 'm5'], 4, start, end)
    kdb.create_dataset(5, 'EUR/USD', ['m1', 'm5'], 4, start, end)


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
    assert 'tickqty' in dataset[0]['x']
    assert len(dataset[0]['x']['m1']) == 4
    assert len(dataset[0]['x']['m5']) == 4
    assert len(dataset[0]['x']['tickqty']) == 4
    # test 1 element
    assert 'm1' in dataset[1]['x']
    assert 'm5' in dataset[1]['x']
    assert 'tickqty' in dataset[1]['x']
    assert len(dataset[1]['x']['m1']) == 4
    assert len(dataset[1]['x']['m5']) == 4
    assert len(dataset[1]['x']['tickqty']) == 4


def test_create_train_value_raise_date_period(kdb):
    with pytest.raises(ValueError, match=r".*Date.*not in requested period.*"):
        date_start = dt.datetime(2018, 11, 27, 23, 0)
        kdb.create_train_value('EUR/USD', ['m1', 'm5'], 8, date_start)
    with pytest.raises(ValueError, match=r".*Date.*not in requested period.*"):
        date_start = dt.datetime(2018, 11, 27, 23, 20)
        kdb.create_train_value('EUR/USD', ['m1', 'm5'], 8, date_start)
    with pytest.raises(ValueError, match=r".*Date.*not in requested period.*"):
        date_start = dt.datetime(2018, 11, 27, 23, 30)
        kdb.create_train_value('EUR/USD', ['m1', 'm5'], 8, date_start)
    date_start = dt.datetime(2018, 11, 27, 22, 59)
    kdb.create_train_value('EUR/USD', ['m1', 'm5'], 8, date_start)


def test_create_train_value(kdb):
    m1date = dt.datetime(2018, 11, 27, 17, 26)
    val = kdb.create_train_value('EUR/USD', ['m1', 'm5'], 8, m1date)
    assert val['x']['m5'][0]['value'] == 1.12894


def test_create_train_value_hour(kdb):
    m1date = dt.datetime(2018, 11, 27, 15, 2)
    val = kdb.create_train_value('EUR/USD', ['m1', 'm5', 'H1'], 8, m1date)
    assert val['x']['m5'][0]['value'] == 1.13195

    # Hour test
    assert val['x']['H1'][0]['value'] == 1.13195


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


def test_get_instrument_raise(kdb):
    with pytest.raises(ValueError, match=r".*datetime.*"):
        dataset = kdb.get_instrument('EUR/USD', 'm1', 'start', 'end')
