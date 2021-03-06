# coding: utf-8
from singleton import singleton
from logger import alogger, slogger, elogger, init_logger
# from exchange.binan import BinanceEx
# from exchange.huobi import HuobiEx
# from exchange.okex import OkexEx
# from exchange.gateio import GateioEx
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.ioloop import IOLoop
import time
import threading
from datetime import datetime
from cache import Cache
import tornado
from druid import *
from dao import *
SCAN_TIMEOUT_INTERVAL = 1800 * 1000
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
        bases = ['btc', 'eth', 'usdt']
        try:
            assets = DBStatistics.instance().select_asset()  
            for asset in assets:
                if asset in bases:
                    continue
                for base in bases:
                    s = asset + '_' + base
                    if s in self.cache.data.keys() and \
                        self.exchange.name in self.cache.data[s].keys():
                        continue
                    self.cache.setkey(s, self.exchange.name)
            self.cache.setkey('eth_btc', self.exchange.name)
            print 'liubida1', self.cache
            slogger.info('wisp symbol [%s] done, time cost:%s' % (self.exchange.name, str(time.time() - begin)))
        except Exception, e:
            slogger.info('wisp symbol [%s] exception' % self.exchange.name)
            slogger.exception(e)
        finally:
            self.running = False

    @gen.coroutine
    def dig_depth(self):
        begin = time.time()
        self.running = True
        try:
            for symbol in self.cache.data.keys():
                try:
                    if self.exchange.name not in self.cache.data[symbol].keys():
                        continue

                    info = yield self.exchange.get_depth(symbol)
                    if info:
                        quote, base = symbol.split('_')[0], symbol.split('_')[1]
                        ret_amount = yield self.exchange.get_assets_amount([quote, base])
                        quote_amount, base_amount = ret_amount[quote], ret_amount[base]
                        amount_info = {'quote':quote_amount, 'base':base_amount}
                        #print 'yyyyy',symbol,info, amount_info
                        #slogger.info('spider value {}, {}, {}'.format(symbol, info, amount_info))
                        self.cache.setvalue(symbol, self.exchange.name, info, amount_info)
                except Exception, e:
                    slogger.info('wisp [%s] depth [%s] exception' % (self.exchange.name,symbol))
                    slogger.exception(e)
            slogger.info('wisp depth [%s] done, time cost:%s' % (self.exchange.name, str(time.time() - begin)))
        except Exception, e:
            slogger.info('wisp depth [%s] exception' % self.exchange.name)
            slogger.exception(e)
        finally:
            self.running = False
    
@singleton
class Spider:
    def __init__(self):
        self.terminate = False
        self.busy = False
        self.wisps = []
        self.cache = Cache.instance()

    def runLoop(self):
        if self.terminate:
            slogger.info('spider terminate')
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
            
            slogger.info('wisp depth [%s] start' % wisp.exchange.name)
            wisp.dig_depth()

        if bingo == 0:
            self.busy = True
            slogger.info('wisps are all busy')

    def refresh_symbols(self):
        slogger.info('refresh symbols start')

        for wisp in self.wisps:
            slogger.info('wisp symbol [%s] start' % wisp.exchange.name)
            wisp.dig_symbols()

        for symbol, v1 in self.cache.data.iteritems():
            for exchange, v2 in v1.iteritems():
                now = time.time()
                if 'timestamp' in v2 and now - v2['timestamp'] >= self.cache.clean_timeout:
                    del self.cache[symbol][exchange]
                    slogger.info('%s, %s, deleted in cache', symbol, exchange)
                else:
                    continue

        slogger.info('refresh_symbols finished')

    def show_cache(self):
        slogger.info('--------cache--------')
        slogger.info(str(self.cache))
        slogger.info('--------cache--------')
        slogger.info('--------cache--------{}'.format(self.cache.stat()))

    def start(self, exs):
        self.wisps = [Wisp(v['instance']) for k, v in exs.items()]

        # 定时执行callback，时间单位为毫秒
        tornado.ioloop.PeriodicCallback(self.refresh_symbols, SCAN_TIMEOUT_INTERVAL).start()
        tornado.ioloop.PeriodicCallback(self.show_cache, SHOW_CACHE_INTERVAL).start()
        # 若干单位时间后执行callback,添加到主线程的实例上
        IOLoop.instance().add_timeout(time.time() + 10, self.refresh_symbols)
        IOLoop.instance().add_timeout(time.time() + 3, self.runLoop)

if __name__ == '__main__':
    init_logger('.')

    EXCHANGES = {
        'binance': {'instance': BinanceEx.instance(), 'enabled': True},
        'huobi':   {'instance': HuobiEx.instance(),   'enabled': True},
        'okex':    {'instance': OkexEx.instance(),    'enabled': True},
        'gateio':    {'instance': GateioEx.instance(),    'enabled': True},
    }
    print 'success'
    Spider.instance().start(EXCHANGES)
    IOLoop.instance().start() 

