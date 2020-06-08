import pytest
from kragle import KragleDB
import datetime as dt
import pandas as pd


def __test_db_setup():
    kdb = KragleDB('kragle_test')
    kdb.client.drop_database(kdb.dbname)
    periods = ['m1', 'm5', 'm30', 'H2', 'H8']
    for period in periods:
        df = kdb.dataframe_read_json(r'kragle/test_data/'+ period + '_test.json')
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
    assert 'date' in dataset[0]
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

def test_aggregate_dataframe(kdb):
    date1 = dt.datetime(2018, 11, 28, 22,53)
    date2 = dt.datetime(2018, 11, 28, 22,52)
    date3 = dt.datetime(2018, 11, 28, 22,51)
    val = [
        {'date':date1,  'bidopen':1,  'bidclose':2,  'bidhigh':3,   'bidlow':4,  'askopen':5,  'askclose':6,  'askhigh':7,   'asklow':8,  'tickqty':9,}
        ,{'date':date2,  'bidopen':10,  'bidclose':20,  'bidhigh':30,   'bidlow':40,  'askopen':50,  'askclose':60,  'askhigh':70,   'asklow':80,  'tickqty':90,}
        ,{'date':date3,  'bidopen':5,  'bidclose':15,  'bidhigh':35,   'bidlow':25,  'askopen':55,  'askclose':45,  'askhigh':75,   'asklow':65,  'tickqty':85,}
    ]
    
    agg = kdb.aggregate_dataframe(pd.DataFrame(val))

    assert agg['date'] == date1
    assert agg['bidopen'] == 1
    assert agg['bidclose'] == 15
    assert agg['bidhigh'] == 35
    assert agg['bidlow'] == 4
    assert agg['askopen'] == 5
    assert agg['askclose'] == 45
    assert agg['askhigh'] == 75
    assert agg['asklow'] == 8
    assert agg['tickqty'] == 184
    

# def test_foo(kdb):
#     start = dt.datetime(2018, 11, 27, 15,50)
#     end = dt.datetime(2018, 11, 27, 22,50)
#     dataset = kdb.create_dataset(2, 'EUR/USD', ['m1','m5'], 4, start, end )
#     print(' ')
#     print(pd.DataFrame(dataset[0]['x']['m1']).info())
#     print(' ')
#     print(pd.DataFrame(dataset[0]['x']['m1']).head())
#     assert True
