import datetime as dt
import math
import random
from functools import reduce
import operator
from kragle.utils import MeanStdDevCalculator

EUR_USD = {
    'bidopen-mean': 1.15,
    'bidopen-stddev': 0.0012,
    'tickqty-mean': 180,
    'tickqty-stddev': 200
}


def renormalize(values, mean_stddev_calc, target_mean, target_stddev):
    res = []
    for value in values:
        new_value = (((value - mean_stddev_calc.get_mean()) / mean_stddev_calc.get_stddev())
                     * target_stddev) + target_mean
        res.append(new_value)
    return res


def fourier_reconstruction(x, an=[1], bn=[0]):
    fcos = lambda a, n: a * math.cos(2 * math.pi * x * n)
    fsin = lambda b, n: b * math.sin(2 * math.pi * x * n)
    la = map(
        fcos,
        an,
        range(len(an))
    )
    lb = map(
        fsin,
        bn,
        range(len(bn))
    )

    return reduce(operator.add, la) + reduce(operator.add, lb)


def random_dataset(n=100, dim=1):
    ds_list = []
    for j in range(dim):
        res = {'n': [], 'bidopen': [], 'date': [], 'tickqty': []}
        start = dt.datetime(2018, 11, 24, 23, 0)
        value = random.random() * 40 - 20
        tickqty = 10
        b_calc = MeanStdDevCalculator()
        t_calc = MeanStdDevCalculator()
        for i in range(n):
            res['n'].append(i)
            # value balancing
            if (value > 20) | (value < -20):
                balancer = -0.0001 * value
            else:
                balancer = 0
            value = value + (random.random() - 0.5 + balancer)
            # tickqty balancing
            if tickqty > 100:
                tickqty = tickqty * (random.random() + 0.3)
            else:
                tickqty = tickqty * (random.random() + 0.5)
            if tickqty <= 1:
                tickqty = random.random() * 20
            tickqty = int(tickqty)
            b_calc.add(value)
            res['bidopen'].append(value)
            res['date'].append(start + dt.timedelta(minutes=i))
            t_calc.add(tickqty)
            res['tickqty'].append(tickqty)
        res['bidopen'] = renormalize(res['bidopen'], b_calc, EUR_USD['bidopen-mean'], EUR_USD['bidopen-stddev'])
        res['tickqty'] = renormalize(res['tickqty'], b_calc, EUR_USD['tickqty-mean'], EUR_USD['tickqty-stddev'])

        ds_list.append(res)
    return ds_list


def fourier_dataset(n=100, delta=0.01, an=[1], bn=[0], noise_factor=1):
    res = {'n': [], 'bidopen': [], 'date': [], 'tickqty': []}
    start = dt.datetime(2018, 11, 24, 23, 0)
    noise = (random.random() - 0.5) * noise_factor
    b_calc = MeanStdDevCalculator()
    t_calc = MeanStdDevCalculator()
    for i in range(n):
        res['n'].append(i)
        value = fourier_reconstruction(i * delta, an, bn) + noise
        b_calc.add(value)
        res['bidopen'].append(value)
        res['date'].append(start + dt.timedelta(minutes=i))
        tickqty = round(random.random() * 100)
        t_calc.add(tickqty)
        res['tickqty'].append(tickqty)

        noise = noise * 0.9 + (random.random() - 0.5) * noise_factor * 0.3
    res['bidopen'] = renormalize(res['bidopen'], b_calc, EUR_USD['bidopen-mean'], EUR_USD['bidopen-stddev'])
    res['tickqty'] = renormalize(res['tickqty'], b_calc, EUR_USD['tickqty-mean'], EUR_USD['tickqty-stddev'])
    return res


def attractor(n=100, dt=0.01):
    x = 0.4
    y = -0.1
    z = 0.1
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
        if i % pj == 0:
            j = j + 1
        if i % pk == 0:
            k = k + 1
    return res
