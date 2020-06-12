import random
import datetime as dt
import math
from functools import reduce


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


def fourier(x, L, an = [0], bn = []):
    l = map(
        lambda a, b, n: a *math.sin(2 * math.pi * x * n/L) + b *math.sin(2 * math.pi * x * n/L), 
        an, 
        bn, 
        range(len(an))
    )
    return reduce(lambda a, b: a + b, l)

def fourier_01(n=100, dt=0.01):
    L = 8
    an = [6.749, 0.6666, 0.1156, -0.4625, 0, 0.1478, -0.1286, -0.2937, 0, 0.1941, 0.05555]
    bn = [0, -0.2336, -2.705, 0.7626, 0.4774, 0.3278, -0.9018, 0.1651, 0.07957, 0.09412, -0.5411]
    res = {'x':[], 'y':[]}

    for i in range(n):
        res['x'].append(i)
        res['y'].append( fourier(i * dt, L, an, bn))
    return res


def attractor(n=100, dt=0.01):
    x=0.4
    y=-0.1
    z=0.1
    dx=0
    dy=0
    dz=0
    res = {'i':[], 'x':[], 'y':[], 'z':[], 'xyz':[]}
    j=0
    k=0
    di = .5
    pj = 30
    dj = 2
    pk = 40
    dk = 4
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
        res['xyz'].append((di * x + dj  * res['x'][j]) + dk * res['x'][k])
        if i % pj == 0: j =  j + 1
        if i % pk == 0: k =  k + 1
    return res

