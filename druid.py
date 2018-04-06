from singleton import singleton
from logger import alogger, elogger
from cache import Cache
from copy import deepcopy
from tornado.ioloop import IOLoop
from tornado import gen
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

@singleton
class Druid:
    def __init__(self):
        self.terminate = False
        self.handlers = []
        self.cache = None
        self.data_timeout = 60 * 10
        self.tset = TradeSet.instance()

    def start(self, exs):
        self.exchanges = exs
        IOLoop.instance().add_timeout(time.time() + 20, self.scanSymbol)

    @gen.coroutine
    def check_trade(self, symbol, ex1, item1, ex2, item2):
        trade = None

        price1, price2 = item1['price'], item2['price']
        bid1, bid1_amount = price1['bids'][0], price1['bids'][1] 
        ask1, ask1_amount = price1['asks'][0], price1['asks'][1]
        bid2, bid2_amount = price2['bids'][0], price2['bids'][1]
        ask2, ask2_amount = price2['asks'][0], price2['asks'][1]

        if ask1 < bid2 and util.profit_rate(ask1, bid2) > conf.PROFIT_RATE:
            trade = Trade(symbol, ex1, ask1, ask1_amount, ex2, bid2, bid2_amount)
            # TODO put it in __init__
            trade.buyer_asset_amount = item1['amount']['quote']
            trade.buyer_base_amount = item1['amount']['base']
            trade.seller_asset_amount = item2['amount']['quote']
        elif ask2 < bid1 and util.profit_rate(ask2, bid1) > conf.PROFIT_RATE:
            trade = Trade(symbol, ex2, ask2, ask2_amount, ex1, bid1, bid1_amount)
            trade.buyer_asset_amount = item2['amount']['quote']
            trade.buyer_base_amount = item2['amount']['base']
            trade.seller_asset_amount = item1['amount']['quote']
        else:
            raise gen.Return((False, None))
            return

        raise gen.Return((True, trade))
        return

    @gen.coroutine
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
        if int(time.time()) % 30 == 0:
            alogger.info('heart: scan symbol')
        for symbol, value in self.cache.data.iteritems():
            exs = self.cache.data[symbol].keys()
            perm_list = util.permutation(exs)
            for item in perm_list:
                try:
                    # ex1, ex2 is exchange instance 
                    ex1, ex2 = self.exchanges[item[0]]['instance'], self.exchanges[item[1]]['instance']
                    item1 = self.cache.get(symbol, ex1.name)
                    if item1 is None:
                        continue
                    item2 = self.cache.get(symbol, ex2.name)
                    if item2 is None:
                        continue
                    flag, trade = yield self.check_trade(symbol, ex1, item1, ex2, item2)
                    if flag and trade is not None:
                        alogger.info('check_trade bingo. {}'.format(str(trade)))
                        elogger.info('&CHECK, {}'.format(str(trade)))
                        self.tset.produce(trade)
                except Exception as e:
                    alogger.exception(e)
        IOLoop.instance().add_timeout(time.time() + 1, self.scanSymbol)

if __name__ == '__main__':
    Druid.instance().start()
    IOLoop.instance().start()

