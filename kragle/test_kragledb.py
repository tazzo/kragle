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
    print('>> Setup kdb << ', end='')
    kdb = __test_db_setup()
    yield kdb
    print(">> Teardown kdb << ", end='')
    __test_db_teardown(kdb)

def test_create_dataset_raise_date_order(kdb):
    '''test start date after end date'''
    start = dt.datetime(2018, 11, 28, 22,50)
    end = dt.datetime(2018, 11, 27, 22,50)
    with pytest.raises(ValueError, match=r".*before.*"):
        dataset = kdb.create_dataset(2, 'EUR/USD', ['m1','m5'], 4, start, end )

def test_create_dataset_raise_few_data(kdb):
    '''test start date after end date'''
    start = dt.datetime(2018, 10, 25, 22,50)
    end = dt.datetime(2018, 10, 27, 22,50)
    with pytest.raises(ValueError, match=r".*fulfill.*"):
        dataset = kdb.create_dataset(2, 'EUR/USD', ['m1','m5'], 4, start, end )
    
   

def test_create_dataset(kdb):
    start = dt.datetime(2018, 11, 27, 15,50)
    end = dt.datetime(2018, 11, 27, 22,50)
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
    assert 'm1' in dataset[1]['x']
    assert 'm5' in dataset[1]['x']
    assert len(dataset[1]['x']['m1'])==4
    assert len(dataset[1]['x']['m5'])==4


