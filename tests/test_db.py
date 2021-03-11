import datetime as dt
import logging.config
import pytest
import pytz

from kragle.db import KragleDB, FutureTool
import kragle.utils as kutils
from kragle.utils import Action

logging.config.fileConfig('log.cfg')


def __test_db_setup(db, periods, filename):
    kdb = KragleDB(db)
    kdb.drop_db()
    for period in periods:
        df = kutils.dataframe_from_json(r'tests/test_data/' + period + filename + '.json')
        kdb.fetch_dataframe(df, 'EUR/USD', period)
    return kdb


def __test_db_teardown(kdb):
    kdb.drop_db()
    kdb.close()


@pytest.fixture(scope="module")
def kdb():
    print('>> Setup kdb << ', end='')
    dbname = 'kragle_test'
    periods = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H8']
    filename = '_test'
    kdb = __test_db_setup(dbname, periods, filename)
    kdb.insert_future('EUR/USD', 'm5', None, None, field='bidopen', futurelen=4, limit=4 * 0.0001)
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


@pytest.fixture(scope="function")
def dataset_setup():
    kdb = KragleDB('kragle_test_dataset')
    kdb.drop_db()
    yield ''
    kdb.drop_db()


def test_save_dataset(kdb, dataset_setup):
    start = dt.datetime(2018, 11, 27, 15, 50)
    end = dt.datetime(2018, 11, 27, 22, 50)
    dataset = kdb.create_dataset(2, 'EUR/USD', ['m1', 'm5'], 4, start, end)
    db_name = 'kragle_test_dataset'
    dataset_name = 'test_save_dataset'
    kdb.save_dataset(db_name, dataset_name, dataset)
    l = kdb.client[db_name].list_collection_names()
    assert dataset_name in l


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
    kdb_future.insert_future('EUR/USD', 'm5', start_date, end_date, field='bidopen', futurelen=4, limit=15)
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date)
    assert val['future'] == Action.HOLD.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=5))
    assert val['future'] == Action.HOLD.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=10))
    assert val['future'] == Action.BUY.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=15))
    assert val['future'] == Action.BUY.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=20))
    assert val['future'] == Action.BUY.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=25))
    assert val['future'] == Action.BUY.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=30))
    assert val['future'] == Action.BUY.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=35))
    assert val['future'] == Action.SELL.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=40))
    assert val['future'] == Action.HOLD.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=45))
    assert val['future'] == Action.HOLD.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=50))
    assert val['future'] == Action.HOLD.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=55))
    assert val['future'] == Action.HOLD.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=60))
    assert val['future'] == Action.SELL.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=65))
    assert val['future'] == Action.SELL.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=70))
    assert val['future'] == Action.SELL.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=75))
    assert val['future'] == Action.HOLD.value
    val = kdb_future.get_single_value('EUR/USD', 'm5', start_date + dt.timedelta(minutes=80))
    assert val['future'] == Action.HOLD.value


def test_get_instrument_raise(kdb):
    with pytest.raises(ValueError, match=r".*datetime.*"):
        dataset = kdb.get('EUR/USD', 'm1', 'start', 'end')


def test_futuretool1():
    l = [{'bidopen': i} for i in [0, 2, 3, 4, 5, 6, 70, 80, 88, 90]]
    fm = FutureTool(field='bidopen', future_len=3, limit=20)
    res = fm.calc_collection(l)
    assert len(res) == 7
    assert res[0][1] == Action.HOLD
    assert res[1][1] == Action.HOLD
    assert res[2][1] == Action.HOLD
    assert res[3][1] == Action.BUY
    assert res[5][1] == Action.BUY
    assert res[6][1] == Action.BUY


def test_futuretool2():
    l = [{'bidopen': i} for i in [0, 1, 0, -2, 10, -10]]
    fm = FutureTool(field='bidopen', future_len=5, limit=4)
    res = fm.calc_collection(l)
    assert len(res) == 1
    assert res[0][1] == Action.BUY
    fm = FutureTool(field='bidopen', future_len=3, limit=4)
    res = fm.calc_collection(l)
    assert len(res) == 3
    assert res[0][1].value == 0
    assert res[1][1] == Action.BUY
    assert res[2][1] == Action.BUY


def test_futuretool3():
    l = [{'bidopen': i} for i in [0, 1, 0, -2, -10, 10]]
    fm = FutureTool(field='bidopen', future_len=5, limit=4)
    res = fm.calc_collection(l)
    assert len(res) == 1
    assert res[0][1] == Action.SELL
    fm = FutureTool(field='bidopen', future_len=3, limit=4)
    res = fm.calc_collection(l)
    assert len(res) == 3
    assert res[0][1] == Action.HOLD
    assert res[1][1] == Action.SELL
    assert res[2][1] == Action.SELL


@pytest.fixture(scope="function")
def dup_setup():
    kdb = KragleDB('kragle_test_duplicate')
    kdb.drop_db()
    yield ''
    kdb.drop_db()


def test_duplicate_db(kdb, dup_setup):
    duplicate = kdb.duplicate_db('kragle_test_duplicate', periods=['m1', 'm5', 'm30'])
    assert len(duplicate.get_instruments()) == 1
    instrument = 'EUR/USD'
    assert instrument in duplicate.get_instruments()
    assert 'm1' in duplicate.get_periods(instrument)
    assert 'm5' in duplicate.get_periods(instrument)
    assert 'm30' in duplicate.get_periods(instrument)
    assert 'm15' not in duplicate.get_periods(instrument)
    assert len(duplicate.get(instrument, 'm1')) == 600
    assert len(duplicate.get(instrument, 'm5')) == 599
    assert len(duplicate.get(instrument, 'm15')) == 0
    assert len(duplicate.get(instrument, 'm30')) == 600

    assert len(duplicate.get(instrument, 'm30',
                             from_date=dt.datetime(2018, 11, 27, 22, 55, tzinfo=pytz.timezone('Europe/Rome')))) == 1
    assert len(duplicate.get(instrument, 'm30',
                             from_date=dt.datetime(2018, 11, 27, 22, 50, tzinfo=pytz.timezone('Europe/Rome')))) == 2


def test_duplicate_db_from_date(kdb, dup_setup):
    instrument = 'EUR/USD'
    from_date = dt.datetime(2018, 11, 27, 22, 50)

    duplicate = kdb.duplicate_db('kragle_test_duplicate', periods=['m1', 'm5', 'm30'], from_date=from_date)
    assert len(duplicate.get(instrument, 'm5')) == 2


def test_duplicate_db_to_date(kdb, dup_setup):
    instrument = 'EUR/USD'
    to_date = dt.datetime(2018, 11, 23, 22, 40, )

    duplicate = kdb.duplicate_db('kragle_test_duplicate', periods=['m1', 'm5', 'm30'], to_date=to_date)
    assert len(duplicate.get(instrument, 'm5')) == 3
