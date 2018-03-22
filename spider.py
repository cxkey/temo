from singleton import singleton
from logger import alogger, elogger, init_logger
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

SCAN_TIMEOUT_INTERVAL = 3600 * 6 * 1000
SHOW_CACHE_INTERVAL = 10 * 1000
PROCESS_BUSY_INTERVAL = 10
PROCESS_INTERVAL = 2

class Wisp:
    def __init__(self, exchange):
        self.exchange = exchange
        self.running = False
        self.cache = Cache.instance()

    @gen.coroutine
    def dig_symbols(self):
        begin = time.time()
        self.running = True
        try:
            r = yield self.exchange.get_symbols()
            if r:
                for s in r.keys():
                    if s in self.cache.data.keys() and \
                        self.exchange.name in self.cache.data[s].keys():
                        continue

                    self.cache.setkey(s, self.exchange.name)
                alogger.info('wisp symbol [%s] done, time cost:%s' % (self.exchange.name, str(time.time() - begin)))
        except Exception, e:
            alogger.info('wisp symbol [%s] exception' % self.exchange.name)
            alogger.exception(e)
        finally:
            self.running = False

    @gen.coroutine
    def dig_depth(self):
        begin = time.time()
        self.running = True
        try:
            for symbol in self.cache.data.keys():
                if self.exchange.name not in self.cache.data[symbol].keys():
                    continue

                info = yield self.exchange.get_depth(symbol)
                if info:
                    self.cache.setvalue(symbol, self.exchange.name, info)
            alogger.info('wisp depth [%s] done, time cost:%s' % (self.exchange.name, str(time.time() - begin)))
        except Exception, e:
            alogger.info('wisp depth [%s] exception' % self.exchange.name)
            alogger.exception(e)
        finally:
            self.running = False
    
@singleton
class Spider:
    def __init__(self):
        self.terminate = False
        self.busy = False
        self.wisps = [
            Wisp(BinanceEx.instance()),
            Wisp(HuobiEx.instance()),
            Wisp(OkexEx.instance()),
        ]
        self.cache = Cache.instance()

    def runLoop(self):
        if self.terminate:
            alogger.info('spider terminate')
            tornado.ioloop.IOLoop.instance().stop()
            return

        if self.busy:
            IOLoop.instance().add_timeout(time.time() + PROCESS_BUSY_INTERVAL, self.runLoop)
            self.busy = False
            return

        IOLoop.instance().add_timeout(time.time() + PROCESS_INTERVAL, self.runLoop)

        self.process()

    @gen.coroutine
    def process(self):
        begin = time.time()

        bingo = len(self.wisps)
        for wisp in self.wisps:
            if wisp.running:
                bingo -= 1
                continue
            
            alogger.info('wisp depth [%s] start' % wisp.exchange.name)
            wisp.dig_depth()

        if bingo == 0:
            self.busy = True
            alogger.info('wisps are all busy')

    def refresh_symbols(self):
        alogger.info('refresh symbols start')

        for wisp in self.wisps:
            alogger.info('wisp symbol [%s] start' % wisp.exchange.name)
            wisp.dig_symbols()

        #for symbol, v1 in self.cache.data.iteritems():
        #    for exchange,v2 in v1.iteritems():
        #        now = time.time()
        #        if now - v2['timestamp'] >= self.cache.clean_timeout:
        #            del self.cache[symbol][exchange]
        #            alogger.info('%s,%s,deleted in cache',symbol,exchange)
        #        else:
        #            continue

        alogger.info('refresh_symbols finished')

    def show_cache(self):
        alogger.info('--------cache--------')
        alogger.info(str(self.cache))
        alogger.info('--------cache--------')
        alogger.info('--------cache--------')

    def start(self):
        tornado.ioloop.PeriodicCallback(self.refresh_symbols, SCAN_TIMEOUT_INTERVAL).start()
        tornado.ioloop.PeriodicCallback(self.show_cache, SHOW_CACHE_INTERVAL).start()
        IOLoop.instance().add_timeout(time.time() + 0.01, self.refresh_symbols)
        IOLoop.instance().add_timeout(time.time() + 1, self.runLoop)

if __name__ == '__main__':
    init_logger('.')
    Spider.instance().start()
    IOLoop.instance().start() 

