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
from datetime import datetime
from cache import Cache
import tornado
from druid import *

SCAN_TIMEOUT_INTERVAL = 3600 *1000 * 6

@singleton
class Spider:
    def __init__(self):
        self.terminate = False
        self.exchanges = [
            BinanceEx.instance(),
            HuobiEx.instance(),
            OkexEx.instance(),
        ]
        self.datacache = Cache.instance()

    @gen.coroutine
    def process(self):
        print 'spider process start'
        begin = time.time()
        for ex in self.exchanges:
            r = yield ex.get_symbols()
            for symbol, value in r.iteritems():
                info = yield ex.get_depth(symbol)
                if info:
                    print ex.name, symbol, info
                    self.datacache.setvalue(symbol,ex.name,info)
        print 'done, time cost:',time.time()-begin
        IOLoop.instance().add_timeout(time.time() + 1000, self.process)

    def scanTimeout(self):
        print 'scan timeout start'
        for symbol,v1 in self.datacache.data.iteritems():
            for exchange,v2 in v1.iteritems():
                now = time.time()
                if now - v2['timestamp'] >= self.datacache.clean_timeout:
                    del self.datacache[symbol][exchange]
                    alogger.info('%s,%s,deleted in cache',symbol,exchange)
                else:
                    continue
        print 'scan timeout finished'


    def start(self):
        tornado.ioloop.PeriodicCallback(self.scanTimeout, SCAN_TIMEOUT_INTERVAL).start()
        IOLoop.instance().add_timeout(time.time() + 0.01, self.process)

if __name__ == '__main__':
    Spider.instance().start()
    IOLoop.instance().start() 

