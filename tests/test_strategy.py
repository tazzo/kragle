import datetime as dt
import pytest
import logging.config

from kragle.kdb import KragleDB
import kragle.utils as kutils
from kragle.strategy import AgentTester, BuyStrategy, SellStrategy
from kragle.utils import PIP

logging.config.fileConfig('log.cfg')

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


def _test_agent_tester(kdb):
    # Buy strategy
    start = dt.datetime(2018, 11, 27, 13, 0)
    end = dt.datetime(2018, 11, 27, 15, 47)
    at = AgentTester(kdb, BuyStrategy())
    at.test_strategy('EUR/USD', start, end)
    assert at.wallet == 1.13063 - 1.13188 - 2 * PIP
    #Sell strategy
    start = dt.datetime(2018, 11, 27, 13, 0)
    end = dt.datetime(2018, 11, 27, 14, 6)
    at = AgentTester(kdb, SellStrategy())
    at.test_strategy('EUR/USD', start, end)
    assert at.wallet == -1.13289 + 1.13188 - 2 * PIP
