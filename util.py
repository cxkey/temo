import uuid, datetime, time, json
from hashlib import md5
import re
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

if __name__ == '__main__':
     permutation([1,2,3,4])
     print gen_id()

