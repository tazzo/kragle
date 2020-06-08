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


def test_datetime_period_raise():
    #test wrong period raise exception
    date = dt.datetime(2018, 10, 23, 15, 37, 12)
    with pytest.raises(ValueError, match=r".*not defined.*"):
        kutils.datetime_period(date, 'm6')


def test_datetime_period_m5():
    expect = dt.datetime(2018, 10, 23, 15, 35, 0)
    
    #test date with seconds
    date = dt.datetime(2018, 10, 23, 15, 37, 12)
    newdate = kutils.datetime_period(date, 'm5')
    assert newdate == expect

    #test no change date
    date = dt.datetime(2018, 10, 23, 15, 35)
    newdate = kutils.datetime_period(date, 'm5')
    assert newdate == expect

def test_datetime_period_m15():
    ############ Expected datetime #################
    expect = dt.datetime(2018, 10, 23,   15, 30)

    #test date with seconds
    date = dt.datetime(2018, 10, 23, 15, 37, 12)
    newdate = kutils.datetime_period(date, 'm15')
    assert newdate == expect

    #test no change date
    date = dt.datetime(2018, 10, 23, 15, 30)
    newdate = kutils.datetime_period(date, 'm15')
    assert newdate == expect

    ############ Expected datetime #################
    expect = dt.datetime(2018, 10, 23, 14, 0)

    #test date with seconds
    date = dt.datetime(2018, 10, 23, 14, 2, 1)
    newdate = kutils.datetime_period(date, 'm15')
    assert newdate == expect

    #test no change date
    date = dt.datetime(2018, 10, 23, 14)
    newdate = kutils.datetime_period(date, 'm15')
    assert newdate == expect

    #test no change date
    date = dt.datetime(2018, 10, 23, 14 , 14, 59, 99)
    newdate = kutils.datetime_period(date, 'm15')
    assert newdate == expect

def test_datetime_period_m30():
    ############ Expected datetime #################
    expect = dt.datetime(2018, 10, 23,   15, 30)

    #test date with seconds
    date = dt.datetime(2018, 10, 23, 15, 37, 12)
    newdate = kutils.datetime_period(date, 'm30')
    assert newdate == expect

    #test no change date
    date = dt.datetime(2018, 10, 23, 15, 30)
    newdate = kutils.datetime_period(date, 'm30')
    assert newdate == expect

    ############ Expected datetime #################
    expect = dt.datetime(2018, 10, 23,   15, 0)
    #test date with seconds
    date = dt.datetime(2018, 10, 23, 15, 0, 0)
    newdate = kutils.datetime_period(date, 'm30')
    assert newdate == expect

def test_datetime_period_H1():
    ############ Expected datetime #################
    expect = dt.datetime(2018, 10, 23,   15)

    #test date with seconds
    date = dt.datetime(2018, 10, 23, 15, 37, 12)
    newdate = kutils.datetime_period(date, 'H1')
    assert newdate == expect

    #test no change date
    date = dt.datetime(2018, 10, 23, 15, 0)
    newdate = kutils.datetime_period(date, 'H1')
    assert newdate == expect

    #test date with seconds
    date = dt.datetime(2018, 10, 23, 15, 0, 0)
    newdate = kutils.datetime_period(date, 'H1')
    assert newdate == expect
