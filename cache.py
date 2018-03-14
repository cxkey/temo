
from singleton import singleton
from logger import alogger, elogger
from exchange.binan import BinanceEx
from exchange.huobi import HuobiEx

@singleton
class Cache:
    '''
    {
        ex1: {
            p1: { price: [bid1, ask1], timestamp: '' }
            p2: { price: [bid1, ask1], timestamp: '' }
            p3: { price: [bid1, ask1], timestamp: '' }
        },
        ex2: {
            p1: { price: [bid1, ask1], timestamp: '' }
            p2: { price: [bid1, ask1], timestamp: '' }
            p3: { price: [bid1, ask1], timestamp: '' }
            p4: { price: [bid1, ask1], timestamp: '' }
        },
    }
    '''
    def __init__(self):
        self.data = {}
        self.timeout = 10 # sec

    def find_exchange(self, exchange_name):
        if exchange_name in self.data.keys():
            return True
        return False

    def find_symbol(self, exchange_name, symbol):
        if not self.find_exchange(exchange_name):
            return False
        if symbol in self.data[exchange_name].keys():
            return True
        return False            

    def set(self, exchange_name, symbol, value):
        if not value:

        if self.find_symbol(exchange_name, symbol):
            self.data[exchange_name][symbol] = value

    def get_symbol(self, exchange_name, symbol):
        if self.find_symbol(exchange_name, symbol):
            return self.data[exchange_name][symbol]
        return None            

    def exchanges(self): 
        return self.data.keys()

    def symbols(self, exchange_name):
        if find_exchange(exchange_name):
            return self.data[exchange_name].keys()

if __name__ == '__main__':
    pass

