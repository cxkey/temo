from singleton import singleton
from logger import alogger, elogger
import time

@singleton
class Cache:
    '''
    {
        symbol1: {
            ex1: { price: [bid1, ask1], timestamp: '' }
            ex2: { price: [bid1, ask1], timestamp: '' }
            ex3: { price: [bid1, ask1], timestamp: '' }
        },
        symbol2: {
            ex1: { price: [bid1, ask1], timestamp: '' }
            ex2: { price: [bid1, ask1], timestamp: '' }
            ex3: { price: [bid1, ask1], timestamp: '' }
            ex4: { price: [bid1, ask1], timestamp: '' }
        },
    }
    p1: {
        ex1:
        ex2:
    },
    find(p, ex)
    1 p ex exist
    2 p ex youxiao

    get(p, ex)
    return 

    set(p, ex, value)
    a[p][ex][price] = value
    a[p][ex][timestemp] = timestamp 

    '''

    def __init__(self):
        self.data = {}
        self.update_timeout = 10 # sec
        self.clean_timeout = 3600 * 24 # one day


    def find(self, symbol, exchange):
        if symbol not in self.data.keys():
            return False
        if exchange not in self.data[symbol].keys():
            return False
        ts = self.data[symbol][exchange]
        now = time.time()
        if now - ts <=  self.datacache.update_timeout:
            return True
        return False            
    
    def get(self, symbol, exchange):
        if self.find(symbol,exchange):
            return self.data[symbol][exchange]['price']
        return None         


    def setvalue(self, symbol, exchange, value):
        if symbol not in self.data:
            self.data[symbol] = {}
        if exchange not in self.data[symbol]:
            self.data[symbol][exchange] = {}
        self.data[symbol][exchange]['price'] = value
        self.data[symbol][exchange]['timestamp'] = time.time()


if __name__ == '__main__':
    pass

