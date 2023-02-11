import kragle.kdb as kdb
import time
db = kdb.KragleDB(db_name='TensorSave', instrument='EUR/USD', ds_name='Datasets')
for n in range(60):
    db.fetch_data_tensor_fxcm(periods=['m1', 'm5', 'm30', 'H2', 'H8', 'D1'], history_len=10)
    print('Loop n:{}'.format(n))
    time.sleep(600)





