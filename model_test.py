import kragle.kdb as kdb
import time
import kragle.kdb as kdb
import pprint as pp
import numpy
from tensorflow import keras
import fxcmpy
import time

sleep_time = 1200
while True:
    print('connecting...')
    fxcon = fxcmpy.fxcmpy(config_file='fxcm.cfg')

    db = kdb.KragleDB(db_name='TensorSave', instrument='EUR/USD', ds_name='Datasets')

    print('get_data_tensor_fxcm...')
    t = db.get_data_tensor_fxcm(periods=['m1', 'm5', 'm30', 'H2', 'H8', 'D1'], history_len=10, fxcon=fxcon, close=False)
    #pp.pprint('Tensor: {}'.format(t))

    model = keras.models.load_model('models/pips15hist10fut800')
    res = model.predict(numpy.expand_dims(t[0], axis=0))

    print('Predict')
    pp.pprint(res)

    tmp = 0
    action = 1  # HOLD
    for n in range(len(res[0])):
        print('res[0][n] {}  tmp {}   n {}'.format(res[0][n],tmp, n))
        if res[0][n] > tmp:
            tmp = res[0][n]
            action = n

    print('n {}'.format(action))
    is_buy = None
    if action == 0:
        is_buy = False
    if action == 2:
        is_buy = True
    print('is_buy: {}'.format(is_buy))

    if is_buy is not None :
#    if False:
        fxcon.open_trade(symbol='EUR/USD',
                                 is_buy=is_buy,
                                 amount=1,
                                 time_in_force='GTC',
                                 order_type='AtMarket',
                                 limit=15,
                                 is_in_pips=True,
                                 stop=-15)

    print('closing....')
    fxcon.close()
    print('spleeping....')
    time.sleep(sleep_time)