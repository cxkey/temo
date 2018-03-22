from singleton import singleton
from logger import alogger, elogger
from cache import Cache
from copy import deepcopy
from tornado.ioloop import IOLoop
from util import permutation
import time
from decimal import Decimal
from exchange.binan import BinanceEx 
from exchange.huobi import HuobiEx  
from exchange.okex import OkexEx 
from Queue import Queue
from trade import *
from init import *
import conf
import util

ex_dict = {
    'binance':BinanceEx.instance(),
    'huobi':HuobiEx.instance(),
    'okex':OkexEx.instance()
}

@singleton
class Druid:
    def __init__(self):
        self.terminate = False
        self.handlers = []
        self.cache = None
        self.data_timeout = 60 * 10
        self.tset = TradeSet.instance()

    def start(self):
        IOLoop.instance().add_timeout(time.time() + 20, self.scanSymbol)

    def check_trade(self, symbol, ex1, price1, ex2, price2):
        trade = None

        bid1, bid1_amount = price1['bids'][0], price1['bids'][1] 
        ask1, ask1_amount = price1['asks'][0], price1['asks'][1]
        bid2, bid2_amount = price2['bids'][0], price2['bids'][1]
        ask2, ask2_amount = price2['asks'][0], price2['asks'][1]

        if ask1 < bid2 and util.profit_rate(ask1, bid2) > conf.PROFIT_RATE:
            trade = Trade(symbol, ex1, ask1, ask1_amount, ex2, bid2, bid2_amount)
        elif ask2 < bid1 and util.profit_rate(ask2, bid1) > conf.PROFIT_RATE:
            trade = Trade(symbol, ex2, ask2, ask2_amount, ex1, bid1, bid1_amount)
        else:
            return False, None

        ret_risk = yield trade.has_risk()
        if not ret_risk:
            return True, trade

        return False, None

    def scanSymbol(self):
        self.cache = Cache.instance()
        # '''
        # self.cache = {
        #     'r_usdt':{'okex':{'bids': [0.9724, 265.75107117], 'asks': [1.1, 48.2973]},
        #               'binan':{'bids': [0.9824, 265.75107117], 'asks': [1.3, 48.2973]},
        #               'huobi':{'bids': [0.9624, 265.75107117], 'asks': [1.2, 48.2973]}
        #              }
        # }
        # '''
        alogger.info('scan symbol start')
        for symbol, value in self.cache.data.iteritems():
            exs = self.cache.data[symbol].keys()
            perm_list = util.permutation(exs)
            for item in perm_list:
                try:
                    # ex1, ex2 is exchange instance 
                    ex1, ex2 = ex_dict[item[0]], ex_dict[item[1]]
                    price1 = self.cache.get(symbol, ex1.name)
                    if price1 is None:
                        continue
                    price2 = self.cache.get(symbol, ex2.name)
                    if price2 is None:
                        continue
                    flag, trade = self.check_trade(symbol, ex1, price1, ex2, price2)
                    if flag and trade is not None:
                        self.tset.produce(trade)
                except Exception as e:
                    alogger.exception(e)
        print 'scan symbol end'
        IOLoop.instance().add_timeout(time.time() + 1, self.scanSymbol)                    

if __name__ == '__main__':
    Druid.instance().start()
    IOLoop.instance().start()

