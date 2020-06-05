import pytest
from kragle import KragleDB
import datetime as dt
import pandas as pd


def __test_db_setup():
    kdb = KragleDB('kragle_test')
    kdb.client.drop_database(kdb.dbname)
    periods = ['m1', 'm5', 'm30', 'H2', 'H8']
    for period in periods:
        df = pd.read_json(r'kragle\\test_data\\'+ period + '_test.json', orient='records')
        kdb.fetch_dataframe(df, 'EUR/USD', period)
    return kdb
    


def __test_db_teardown(kdb):
    kdb.client.drop_database(kdb.dbname)
    kdb.close()

@pytest.fixture(scope="module")
def kdb():
    print('>> Setup <<')
    kdb = __test_db_setup()
    yield kdb
    print(">> Teardown <<")
    __test_db_teardown(kdb)


def test_file1_method1(kdb):

    x=5
    y=6
    assert x+1 == y,"test_file1_method1 1"
	

def test_file1_method2(kdb):
	x=1
	y=9
	assert x+8 == y,"test_file1_method2 1"

def test_uppercase():
    assert "loud noises".upper() == "LOUD NOISES"

def test_reversed():
    assert list(reversed([1, 2, 3, 4])) == [4, 3, 2, 1]

def test_some_primes():
    assert 13 in {
        num
        for num in range(1, 50)
        if num != 1 and not any([num % div == 0 for div in range(2, num)])
    }