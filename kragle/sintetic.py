import datetime as dt
import math
import random
from functools import reduce
import operator


def fourier(x,  an=[1], bn=[0]):
    fcos = lambda a, n: a * math.cos(2 * math.pi * x * n )
    fsin = lambda b, n: b * math.sin(2 * math.pi * x * n )
    la = map(
        fcos,
        an,
        range(len(an))
    )
    lb = map(
        fsin ,
        bn,
        range(len(bn))
    )

    return (reduce(operator.add, la)+reduce(operator.add, lb))


def fourier_01(n=100, delta=0.01, an = [1], bn = [0]):
    res = {'n': [], 'bidopen': [], 'date': [], 'tickqty': []}
    start = dt.datetime(2018, 11, 24, 23, 0)
    noise = random.random() - 0.5
    for i in range(n):
        res['n'].append(i)
        res['bidopen'].append(fourier(i * delta, an, bn) + noise)
        res['date'].append(start + dt.timedelta(minutes=i))
        res['tickqty'].append(round(random.random() * 100))

        noise = noise * 0.9 + (random.random() - 0.5) * 0.3
    return res


def attractor(n=100, dt=0.01):
    x = 0.4
    y = -0.1
    z = 0.1
    dx = 0
    dy = 0
    dz = 0
    res = {'i': [], 'x': [], 'y': [], 'z': [], 'xyz': []}
    j = 0
    k = 0
    di = .5
    pj = 20
    dj = 2
    pk = 30
    dk = 4
    for i in range(n):

        dx = x - y * z
        dy = x - y + x * z
        dz = -3 * z + x * y

        x = x + dx * dt
        y = y + dy * dt
        z = z + dz * dt
        res['i'].append(i)
        res['x'].append(x)
        res['y'].append(y)
        res['z'].append(z)
        res['xyz'].append((di * x + dj * res['x'][j]) + dk * res['x'][k])
        if i % pj == 0: j = j + 1
        if i % pk == 0: k = k + 1
    return res
