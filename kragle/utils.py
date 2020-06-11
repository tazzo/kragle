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



def attractor(n=100, dt=0.01):
    x=0.4
    y=-0.1
    z=0.1
    dx=0
    dy=0
    dz=0
    res = {'i':[], 'x':[], 'y':[], 'z':[], 'xyz':[]}
    
    for i in range(n):

        dx =  x - y*z
        dy = x - y + x*z
        dz = -3*z + x*y

        x= x + dx * dt
        y= y + dy * dt
        z= z + dz * dt
        res['i'].append((i))
        res['x'].append((x))
        res['y'].append((y))
        res['z'].append((z))
        res['xyz'].append((x+y+z))
    return res

