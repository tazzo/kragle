import datetime as dt
import kragle.utils as kutils
import pytest
import pandas as pd



def test_random_date():
    start = dt.datetime(2018, 10, 22, 15,0)
    end = dt.datetime(2018, 10, 23, 15,0)
    rand = kutils.random_date(start, end) 
    print('start date: ||{}|| < rand date: ||{}|| < end date: ||{}||'.format(start, rand, end),end='')
    assert rand  <= end
    assert rand >= start
    assert rand.second == 0

def test_random_very_near_date():
    start = dt.datetime(2018, 10, 23, 15,0)
    end = dt.datetime(2018, 10, 23, 15,1)
    rand = kutils.random_date(start, end) 
    print('start date: ||{}|| < rand date: ||{}|| < end date: ||{}||'.format(start, rand, end),end='')
    assert rand  <= end
    assert rand >= start
    assert rand.second == 0

def test_aggregate():
    date1 = dt.datetime(2018, 11, 28, 22,53)
    date2 = dt.datetime(2018, 11, 28, 22,52)
    date3 = dt.datetime(2018, 11, 28, 22,51)
    val = [
        {'date':date1,  'bidopen':1,  'bidclose':2,  'bidhigh':3,   'bidlow':4,  'askopen':5,  'askclose':6,  'askhigh':7,   'asklow':8,  'tickqty':9,}
        ,{'date':date2,  'bidopen':10,  'bidclose':20,  'bidhigh':30,   'bidlow':40,  'askopen':50,  'askclose':60,  'askhigh':70,   'asklow':80,  'tickqty':90,}
        ,{'date':date3,  'bidopen':5,  'bidclose':15,  'bidhigh':35,   'bidlow':25,  'askopen':55,  'askclose':45,  'askhigh':75,   'asklow':65,  'tickqty':85,}
    ]
    
    agg = kutils.aggregate(pd.DataFrame(val))

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
    