from singleton import singleton
from logger import alogger, elogger
from cache import Cache
from copy import deepcopy
from tornado.ioloop import IOLoop
import time

@singleton
class Druid:
    def __init__(self):
        self.terminate = False
        self.handlers = []
        self.data = None
        self.data_timeout = 60 * 10

    def start(self):
        IOLoop.instance().add_timeout(time.time() + 300, self.scanSymbol)

    def profit(self, price1, price2):
        return abs(price1-price2)/price1 


    def diff(self, price1,price2):
        bid = price1['bids'][0]
        ask = price2['asks'][0]
        print bid, ask, self.profit(bid,ask)
        if self.profit(bid,ask) >= 0.1:
            return True
        else:
            return False

    def permutation(self, array):
        perm_list = []
        for i in range(0, len(array)):
            for j in range(i+1, len(array)):
                perm_list.append([array[i],array[j]])
        return perm_list                


    def scanSymbol(self):
        self.data = Cache.instance()
        #self.data = {
        #    'r_usdt':{'okex':{'bids': [0.9724, 265.75107117], 'asks': [1.1, 48.2973]},
        #              'binan':{'bids': [0.9824, 265.75107117], 'asks': [1.3, 48.2973]},
        #              'huobi':{'bids': [0.9624, 265.75107117], 'asks': [1.2, 48.2973]}
        #             }
        #}
        print 'scan symbol start'
        for symbol, value in self.data.data.iteritems():
            exs = self.data.data[symbol].keys()
            perm_list = self.permutation(exs)
            for item in perm_list:
                try:
                    price1 = self.data.get(symbol,item[0])
                    price2 = self.data.get(symbol,item[1])
                    
                    if self.diff(price1,price2):
                        print symbol, item, 'can trade'
                    else:
                        print symbol, item, 'can not trade'
                except Exception as e:
                    continue
        print 'scan symbol end'
        #IOLoop.instance().add_timeout(time.time() + 1, self.scanSymbol)                    
   
        

if __name__ == '__main__':
    Druid.instance().start()
    IOLoop.instance().start()

