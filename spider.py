from singleton import singleton
from logger import alogger, elogger
from exchange.binan import BinanceEx
from exchange.huobi import HuobiEx
from exchange.okex import OkexEx
from tornado.ioloop import IOLoop
import time

class DataCache:
    def __init__(self):
        self.data={}
        self.timeout = 10

    def find_exchange(self,exchange_name):
        if exchange_name in self.data.keys():
            return True
        return False

    def exchanges(self): 
        return self.data.keys()

    def find_symbol(self,exchange_name,symbol):
        if not self.find_exchange(exchange_name):
            return False
        if symbol in self.data[exchange_name].keys():
            return True
        return False            


    def set_symbol(self,exchange_name,symbol,value):
        if self.find_symbol(exchange_name,symbol):
            self.data[exchange_name][symbol] = value

    def get_symbol(self,exchange_name,symbol):
        if self.find_symbol(exchange_name,symbol):
            return self.data[exchange_name][symbol]
        return None            

    def symbols(self,exchange_name):
        if find_exchange(exchange_name):
            return self.data[exchange_name].keys()




@singleton
class Spider:
    def __init__(self):
        self.terminate = False
        self.exchanges = [
            BinanceEx.instance(),
            HuobiEx.instance(),
            OkexEx.instance(),
        ]
        self.datacache = DataCache()

    def a(self):
        for exchange in self.exchanges:
            pass

    def runLoop(self):
        if self.terminate:
            logger.info('spider is terminated')
            tornado.ioloop.IOLoop.instance().stop()
            return
        
        begin = time.time()
        for exchange in self.exchanges:
            print exchange.name
            r = exchange.get_symbols()
            for symbol, value in r.iteritems():
                if self.datacache.find_symbol(exchange, symbol) and \
                    now - self.data[exchange_name][symbol]['timestamp'] <=  self.datacache.timeout:
                    continue
                info = exchange.get_depth(symbol)
                if info:
                    info['timestamp'] = time.time()
                    print exchange.name, symbol, info
                    self.datacache.set_symbol(exchange, symbol, info)

        end = time.time()
        print 'done, time cost:', end-begin
        IOLoop.instance().add_timeout(time.time() + 1, self.runLoop)


    def start(self):
        #tornado.ioloop.PeriodicCallback(self.aaa, 3600000).start()
        IOLoop.instance().add_timeout(time.time() + 0.01, self.runLoop)
        IOLoop.instance().start() 

if __name__ == '__main__':
    Spider.instance().start()

