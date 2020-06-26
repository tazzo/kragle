import datetime as dt
import random
import pandas as pd
import logging
import math
from enum import Enum


class Action(Enum):
    BUY = 1
    SELL = 2
    HOLD = 3


class Strategy():

    def __init__(self):
        pass

    def action(self, value):
        """
        value like val = {  'date': m1date,
                            'x': {
                                'm1':[1.1, 1.2, ...],
                                'm5':[1.1, 1.4, ...],
                                'tickqty':[10, 14, ...],
                                ...},
                            'y': 0.7}
        """
        raise ValueError('You must implement this method')


class BuyStrategy(Strategy):

    def action(self, value):
        return Action.BUY


class RandomStrategy(Strategy):

    def __init__(self, seed=42):
        random.seed(seed)
        self.action_list = [Action.BUY,Action.SELL]
        for i in range(20):
            self.action_list.append(Action.HOLD)

    def action(self, value):
        return self.action_list[random.randrange(len(self.action_list))]
