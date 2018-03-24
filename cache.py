#encoding: utf-8
from singleton import singleton
from logger import alogger, elogger
import time

@singleton
class Cache:
    '''
    ask:卖价 bid:买价
    {
        symbol1: {
            ex1: { price: {bids:[bid1_price, bid1_amount], asks:[ask1_price, ask1_amount]}, timestamp: '' }
            ex2: { price: {bids:[bid1_price, bid1_amount], asks:[ask1_price, ask1_amount]}, timestamp: '' }
            ex3: { price: {bids:[bid1_price, bid1_amount], asks:[ask1_price, ask1_amount]}, timestamp: '' }
        },
        symbol2: {
            ex1: { price: {bids:[bid1_price, bid1_amount], asks:[ask1_price, ask1_amount]}, timestamp: '' }
            ex2: { price: {bids:[bid1_price, bid1_amount], asks:[ask1_price, ask1_amount]}, timestamp: '' }
        },
    }
    '''

    def __init__(self):
        self.data = {}
        self.update_timeout = 10 * 60 # sec
        self.clean_timeout = 3600 * 24 # one day

    def __str__(self):
        s = ''
        for k, v in self.data.items():
            s += '{}:{}\n'.format(k, v.keys())

        return s

    def stat(self):
        s = ''
        s += 'symbol length:{}\n'.format(len(self.data.keys()))
        return s

    def find(self, symbol, exchange):
        if symbol not in self.data.keys():
            return False
        if exchange not in self.data[symbol].keys():
            return False
        if not self.data[symbol][exchange] or \
            'price' not in self.data[symbol][exchange].keys() or \
            'timestamp' not in self.data[symbol][exchange].keys() :
            return False
            
        ts = self.data[symbol][exchange]['timestamp']
        if time.time() - ts <=  self.update_timeout:
            return True
        return False            
    
    def get(self, symbol, exchange):
        if self.find(symbol,exchange):
            return self.data[symbol][exchange]['price']
        return None         

    def setkey(self, symbol, exchange):
        if symbol not in self.data:
            self.data[symbol] = {}
        if exchange not in self.data[symbol]:
            self.data[symbol][exchange] = {}

    def setvalue(self, symbol, exchange, value):
        if symbol not in self.data:
            self.data[symbol] = {}
        if exchange not in self.data[symbol]:
            self.data[symbol][exchange] = {}
        self.data[symbol][exchange] = {'price': value, 'timestamp': time.time() }

if __name__ == '__main__':
    pass

