import random
import datetime as dt
import math



def random_date( start, end):
    """Generate a random datetime between `start` and `end` in minutes"""
    return start + dt.timedelta(
        # Get a random amount of seconds between `start` and `end`
        minutes=random.randint(0, int((end - start).total_seconds()/60)),
    )

def aggregate_dataframe( df):
    high = df[['bidhigh','askhigh']].max()
    low = df[['bidlow','asklow']].min()
    sum = df[['tickqty']].sum()
    res = {'date': df.iloc[-1]['date'],  
        'bidopen': df.iloc[-1]['bidopen'],  
        'bidclose': df.iloc[0]['bidclose'],  
        'bidhigh': high['bidhigh'],   
        'bidlow': low['bidlow'],
        'askopen': df.iloc[-1]['askopen'],  
        'askclose': df.iloc[0]['askclose'],  
        'askhigh': high['askhigh'],   
        'asklow': low['asklow'],  
        'tickqty': sum['tickqty'],
    }
    return res

def datetime_period(date, period = 'm5'):
    if period == 'm5':
        newmin = math.floor(date.minute /5) *5
        newdate = date.replace(minute = newmin, second = 0, microsecond = 0)
        return newdate
    if period == 'm15':
        newmin = math.floor(date.minute /15) *15
        newdate = date.replace(minute = newmin, second = 0, microsecond = 0)
        return newdate
    if period == 'm30':
        newmin = math.floor(date.minute /30) *30
        newdate = date.replace(minute = newmin, second = 0, microsecond = 0)
        return newdate
    if period == 'H1':
        newdate = date.replace(minute = 0, second = 0, microsecond = 0)
        return newdate
    else:
        raise ValueError('Period {} not defined.'.format(period) )