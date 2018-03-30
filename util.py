import uuid, datetime, time, json
from hashlib import md5
import re
import datetime
from decimal import Decimal

def gen_md5(fp):
    m = md5()    
    m.update(fp)
    return m.hexdigest()

def permutation(array):
    perm_list = []
    for i in range(0, len(array)):
        for j in range(i+1, len(array)):
            perm_list.append([array[i],array[j]])
    return perm_list                

def profit_rate(price1, price2):
    return abs(Decimal(price1) - Decimal(price2)) / Decimal(price1)

def gen_id():
    s = str(uuid.uuid3(uuid.uuid1(), gen_md5(time.ctime()))).replace('-', '')
    return '%s_%s' % (datetime.datetime.now().strftime('%Y%m%d%H%M%S'), s)

def get_time_ten_min_align(t=None):
    if not t:
        t = datetime.datetime.now()
    for i in range(10, 70, 10):
        if t.minute < i:
            return t.replace(minute=i-10, second=0, microsecond=0)
 
if __name__ == '__main__':
     permutation([1,2,3,4])
     print gen_id()
     print get_time_ten_min_align()
     print '{0:g}'.format(float('0.00110000'))
     print Decimal('{0:g}'.format(float('0.00110000')))

     amount = '98.73329392323'
     amount = Decimal(amount).quantize(Decimal('{0:g}'.format(float('0.00010000'))))
     print amount


