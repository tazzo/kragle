import datetime as dt

import kragle.utils as kutils


def test_random_date():
    start = dt.datetime(2018, 10, 22, 15, 0)
    end = dt.datetime(2018, 10, 23, 15, 0)
    rand = kutils.random_date(start, end)
    print('start date: ||{}|| <= rand date: ||{}|| <= end date: ||{}||'.format(start, rand, end), end='')
    assert rand <= end
    assert rand >= start
    assert rand.second == 0


def test_random_very_near_date():
    start = dt.datetime(2018, 10, 23, 15, 0)
    end = dt.datetime(2018, 10, 23, 15, 1)
    rand = kutils.random_date(start, end)
    print('start date: ||{}|| <= rand date: ||{}|| <= end date: ||{}||'.format(start, rand, end), end='')
    assert rand <= end
    assert rand >= start
    assert rand.second == 0
