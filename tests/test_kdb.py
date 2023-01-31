import datetime as dt
import logging.config
import pytest
import pytz

from kragle.kdb import KragleDB
import kragle.utils as kutils
from kragle.utils import Action, PIP

logging.config.fileConfig('log.cfg')


def load_test_period(instrument, periods, kdb, suffix='_test'):
    for period in periods:
        df = kutils.dataframe_from_json(r'tests/test_data/{}{}.json'.format(period, suffix))
        kdb.fetch_dataframe(df, period)


@pytest.fixture(scope="module")
def kdb():
    print('>> Setup kdb << ', end='')
    dbname = 'kragle_test'
    periods = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H8']
    kdb = KragleDB(dbname)
    kdb.drop_db()
    load_test_period('EUR/USD', periods, kdb)
    yield kdb
    print(">> Teardown kdb << ", end='')
    kdb.drop_db()
    kdb.close()

@pytest.fixture(scope="module")
def kdb_future():
    print('>> Setup kdb future << ', end='')
    dbname = 'kragle_test_future'
    periods = ['m1']
    filename = '_future_test'
    kdb = KragleDB(dbname)
    kdb.drop_db()
    load_test_period('EUR/USD', periods, kdb, suffix='_future_test')
    yield kdb
    print(">> Teardown kdb future << ", end='')
    kdb.drop_db()
    kdb.close()

@pytest.fixture(scope="function")
def kdb_void():
    db_name = 'kragle_test_void'
    kdb = KragleDB(db_name)
    kdb.drop_db()
    yield kdb
    kdb.drop_db()
    kdb.close()


def test_fetch_dataframe(kdb_void):
    instrument = 'EUR/USD'
    period = 'm1'
    load_test_period(instrument, [period], kdb_void)

    assert instrument in kdb_void.get_instruments()
    assert period in kdb_void.get_periods()
    assert len(kdb_void.get(period)) == 600


def test_drop_period(kdb_void):
    instrument = 'EUR/USD'
    period1 = 'm1'
    period2 = 'm5'
    load_test_period(instrument, [period1, period2], kdb_void)
    kdb_void.drop_period(period1)
    assert instrument in kdb_void.get_instruments()
    assert period1 not in kdb_void.get_periods()
    assert period2 in kdb_void.get_periods()
    assert len(kdb_void.get(period1)) == 0
    assert len(kdb_void.get(period2)) == 599



def test_drop_instrument(kdb_void):
    df = kutils.dataframe_from_json(r'tests/test_data/m1_test.json')
    instrument = 'EUR/USD'
    period1 = 'm1'
    period2 = 'm5'
    kdb_void.fetch_dataframe(df, period1)
    df = kutils.dataframe_from_json(r'tests/test_data/m5_test.json')
    kdb_void.fetch_dataframe(df, period2)
    kdb_void.drop_instrument()
    assert instrument not in kdb_void.get_instruments()
    assert period1 not in kdb_void.get_periods()
    assert period2 not in kdb_void.get_periods()
    assert len(kdb_void.get(period1)) == 0
    assert len(kdb_void.get(period2)) == 0

def test_get_instrument_raise(kdb):
    with pytest.raises(ValueError, match=r".*datetime.*"):
        dataset = kdb.get('m1', 'start', 'end')

@pytest.fixture(scope="function")
def dup_setup():
    kdb = KragleDB('kragle_test_duplicate')
    kdb.drop_db()
    yield ''
    kdb.drop_db()
    kdb.close()


def test_duplicate_db(kdb, dup_setup):
    duplicate = kdb.duplicate_db('kragle_test_duplicate', periods=['m1', 'm5', 'm30'])
    assert len(duplicate.get_instruments()) == 1
    instrument = 'EUR/USD'
    assert instrument in duplicate.get_instruments()
    assert 'm1' in duplicate.get_periods()
    assert 'm5' in duplicate.get_periods()
    assert 'm30' in duplicate.get_periods()
    assert 'm15' not in duplicate.get_periods()
    assert len(duplicate.get('m1')) == 600
    assert len(duplicate.get('m5')) == 599
    assert len(duplicate.get('m15')) == 0
    assert len(duplicate.get('m30')) == 600

    assert len(
        duplicate.get('m30', from_date=dt.datetime(2018, 11, 27, 22, 55, tzinfo=pytz.timezone('Europe/Rome')))) == 1
    assert len(
        duplicate.get('m30', from_date=dt.datetime(2018, 11, 27, 22, 50, tzinfo=pytz.timezone('Europe/Rome')))) == 2


def test_duplicate_db_from_date(kdb, dup_setup):
    instrument = 'EUR/USD'
    from_date = dt.datetime(2018, 11, 27, 22, 50)

    duplicate = kdb.duplicate_db('kragle_test_duplicate', periods=['m1', 'm5', 'm30'], from_date=from_date)
    assert len(duplicate.get('m5')) == 2


def test_duplicate_db_to_date(kdb, dup_setup):
    instrument = 'EUR/USD'
    to_date = dt.datetime(2018, 11, 23, 22, 40, )

    duplicate = kdb.duplicate_db('kragle_test_duplicate', periods=['m1', 'm5', 'm30'], to_date=to_date)
    assert len(duplicate.get('m5')) == 3


def test_get_action_from_future(kdb_future):
    instrument = 'EUR/USD'
    from_date = dt.datetime(2018, 11, 27, 13, 0)

    action = kdb_future.get_action_from_future(from_date, pips=15, limit_future=30)
    assert action == kutils.Action.HOLD

    action = kdb_future.get_action_from_future(from_date, pips=15, limit_future=50)
    assert action == kutils.Action.BUY

    action = kdb_future.get_action_from_future(from_date, pips=2, limit_future=30)
    assert action == kutils.Action.SELL

    action = kdb_future.get_action_from_future(from_date, pips=7, limit_future=30)
    assert action == kutils.Action.BUY
