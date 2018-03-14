from singleton import singleton
from logger import alogger, elogger
from exchange.binan import BinanceEx
from exchange.huobi import HuobiEx
from exchange.okex import OkexEx
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.ioloop import IOLoop
import time
import threading


@singleton
class Spider:
    def __init__(self):
        self.terminate = False
        self.exchanges = [
            BinanceEx.instance(),
            #HuobiEx.instance(),
            #OkexEx.instance(),
        ]
        self.datacache = DataCache()

    @gen.coroutine
    def process(self):
        for ex in self.exchanges:
            alogger.info('spider process start %s' % ex.name)
            r = yield ex.get_symbols()
            for symbol, value in r.iteritems():
                if self.datacache.find_symbol(ex, symbol) and \
                    now - self.data[ex_name][symbol]['timestamp'] <=  self.datacache.timeout:
                    continue
                info = ex.get_depth(symbol)
                if info:
                    info['timestamp'] = time.time()
                    print ex.name, symbol, info
                    self.datacache.set_symbol(ex, symbol, info)

        end = time.time()
        print 'done, time cost:', end-begin
        IOLoop.instance().add_timeout(time.time() + 1, self.runLoop)

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

