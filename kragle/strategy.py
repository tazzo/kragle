import datetime as dt
import random
import pandas as pd
import logging
import math
from enum import Enum

PIP = .0001


class Action(Enum):
    BUY = 1
    SELL = 2
    HOLD = 3


class AgentTester:

    def __init__(self, kdb, strategy):
        self.kdb = kdb
        self.strategy = strategy
        self.wallet = 0
        self.price = 0
        self.stop_loss = 10 * PIP
        self.take_profit = 20 * PIP
        # test
        self.periods = ['m1', 'm5', 'm15', 'H1']
        self.hist_len = 1
        self.action = Action.HOLD
        self.df = None

    def test_strategy(self, instrument, date_start, date_end):
        self.df = pd.DataFrame(columns=['date', 'bidopen', 'action', 'color',  'wallet'])
        date_list = self.kdb.get_date_list(instrument, 'm1', date_start, date_end)
        for date_value in date_list:
            df_value = {}

            tvalue = self.kdb.create_train_value(instrument, self.periods, self.hist_len, date_value['date'])
            value = tvalue['x']['m1'][0]['value']
            action = self.strategy.action(tvalue)

            if self.action == Action.HOLD:
                if action == Action.HOLD:
                    continue
                else:
                    self.action = action
                    self.price = value
            elif self.action == Action.BUY:
                if (value > self.price + self.take_profit) | (value < self.price - self.stop_loss):
                    self.wallet = self.wallet + value - self.price - 2 * PIP
                    self.action = Action.HOLD
            else:  # self.action == Action.SELL
                if (value < self.price - self.take_profit) | (value > self.price + self.stop_loss):
                    self.wallet = self.wallet - value + self.price - 2 * PIP
                    self.action = Action.HOLD

            # create df_value
            df_value['date'] = date_value['date']
            df_value['bidopen'] = tvalue['x']['m1'][0]['value']
            df_value['action'] = action
            df_value['color'] = action.value * 10
            df_value['wallet'] = self.wallet
            self.df = self.df.append(df_value, ignore_index=True)


class Strategy:

    def __init__(self):
        pass

    def action(self, value):
        """
        value like val = {  'date': m1date,
                            'x': {
                                'm1':[],
                                'm5':[],
                                'tickqty':[],
                                ...},
                            'y': 0.7}
        """
        raise ValueError('You must implement this method')


class BuyStrategy(Strategy):

    def __init__(self):
        super().__init__()

    def action(self, value):
        return Action.BUY


class SellStrategy(Strategy):

    def __init__(self):
        super().__init__()

    def action(self, value):
        return Action.SELL


class RandomStrategy(Strategy):

    def __init__(self, seed=42):
        super().__init__()
        random.seed(seed)
        self.action_list = [Action.BUY, Action.SELL]
        for i in range(20):
            self.action_list.append(Action.HOLD)

    def action(self, value):
        return self.action_list[random.randrange(len(self.action_list))]