import pytest
from kragle import KragleDB
import datetime as dt
import pandas as pd


def __test_db_setup():
    kdb = KragleDB('kragle_test')
    kdb.client.drop_database(kdb.dbname)
    periods = ['m1', 'm5', 'm30', 'H2', 'H8']
    for period in periods:
        df = kdb.dataframe_read_json(r'kragle\\test_data\\'+ period + '_test.json')
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


def test_create_dataset(kdb):
    start = dt.datetime(2018, 10, 22, 15,0)
    end = dt.datetime(2018, 10, 23, 15,0)
    dataset = kdb.create_dataset(2, 'EUR/USD', ['m1','m5'], 4, start, end )
    #test len dataset
    assert len(dataset) ==2
    #test keys in dataset
    assert 'x' in dataset[0]
    assert 'y' in dataset[0]
    #test 0 element
    assert 'm1' in dataset[0]['x']
    assert 'm5' in dataset[0]['x']
    assert len(dataset[0]['x']['m1'])==4
    assert len(dataset[0]['x']['m5'])==4
    #test 1 element
    # assert 'm1' in dataset[1]['x']
    # assert 'm5' in dataset[1]['x']
    # assert len(dataset[1]['x']['m1'])==4
    # assert len(dataset[1]['x']['m5'])==4

	

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