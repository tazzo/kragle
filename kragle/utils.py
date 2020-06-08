import random
import datetime as dt

def random_date( start, end):
    """Generate a random datetime between `start` and `end` in minutes"""
    return start + dt.timedelta(
        # Get a random amount of seconds between `start` and `end`
        minutes=random.randint(0, int((end - start).total_seconds()/60)),
    )


def aggregate(df):
    high = df[['bidhigh','askhigh']].max()
    low = df[['bidlow','asklow']].min()
    sum = df[['tickqty']].sum()
    res = {'date': df.iloc[0]['date'],  
        'bidopen': df.iloc[0]['bidopen'],  
        'bidclose': df.iloc[-1]['bidclose'],  
        'bidhigh': high['bidhigh'],   
        'bidlow': low['bidlow'],
        'askopen': df.iloc[0]['askopen'],  
        'askclose': df.iloc[-1]['askclose'],  
        'askhigh': high['askhigh'],   
        'asklow': low['asklow'],  
        'tickqty': sum['tickqty'],
    }
    return res