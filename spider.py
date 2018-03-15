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

class Wisp:
    def __init__(self, exchange):
        self.exchange = exchange
        self.running = False
        self.cache = Cache.instance()

    @gen.coroutine
    def dig_symbols(self):
        print 210
        begin = time.time()
        self.running = True
        try:
            r = yield self.exchange.get_symbols()
            if r:
                for s in r.keys():
                    if s in self.cache.data.keys() and \
                        self.exchange.name in self.cache.data[s].keys():
                        print 215, s, self.exchange.name
                        continue
                    else:
                        print 214, s, self.exchange.name
                        self.cache.setkey(s, self.exchange.name)
        except Exception, e:
            print str(e)
        finally:
            self.running = False

    @gen.coroutine
    def dig_depth(self):
        print 110
        begin = time.time()
        self.running = True
        try:
            for symbol in self.cache.data.keys():
                info = yield self.exchange.get_depth(symbol)
                if info:
                    #alogger.info('%s, %s, %s' % (self.exchange.name, symbol, str(info)))
                    print '%s, %s, %s' % (self.exchange.name, symbol, str(info))
                    self.cache.setvalue(symbol, self.exchange.name, info)
            print 'dig done, %s, time cost:%s' % (self.exchange.name, str(time.time() - begin))
            #alogger.info('dig done, %s, time cost:%s' % (self.exchange.name, str(time.time() - begin)))
        except Exception, e:
            print str(e)
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
        alogger.info('spider start')
        if self.terminate:
            alogger.info('spider terminate')
            tornado.ioloop.IOLoop.instance().stop()
            return

        if self.busy:
            alogger.info('spider busy')
            IOLoop.instance().add_timeout(time.time() + 1, self.runLoop)
            self.busy = False
            return

        IOLoop.instance().add_timeout(time.time() + 1, self.runLoop)

        self.process()

    @gen.coroutine
    def process(self):
        print 'spider process start'
        begin = time.time()

        bingo = len(self.wisps)
        for wisp in self.wisps:
            if wisp.running:
                bingo -= 1
                continue
            
            wisp.dig()

        if bingo == 0:
            self.busy = True

    def refresh_symbols(self):
        print 'refresh symbols start'

        for wisp in self.wisps:
            print '11111111'
            wisp.dig_symbols()

        #for symbol, v1 in self.cache.data.iteritems():
        #    for exchange,v2 in v1.iteritems():
        #        now = time.time()
        #        if now - v2['timestamp'] >= self.cache.clean_timeout:
        #            del self.cache[symbol][exchange]
        #            alogger.info('%s,%s,deleted in cache',symbol,exchange)
        #        else:
        #            continue

        print 'refresh_symbols finished'

    def start(self):
        tornado.ioloop.PeriodicCallback(self.refresh_symbols, SCAN_TIMEOUT_INTERVAL).start()
        IOLoop.instance().add_timeout(time.time() + 0.01, self.refresh_symbols)
        IOLoop.instance().add_timeout(time.time() + 1, self.runLoop)

if __name__ == '__main__':
    Spider.instance().start()
    IOLoop.instance().start() 

