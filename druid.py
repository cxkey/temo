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

ex_dict = {
    'binan':BinanceEx.instance(),
    'huobi':HuobiEx.instance(),
    'okex':instance()
}


@singleton
class Druid:
    def __init__(self):
        self.terminate = False
        self.handlers = []
        self.data = None
        self.data_timeout = 60 * 10
        self.trade_rate = 0.1
        self.tset = TradeSet.instance()

    def start(self):
        IOLoop.instance().add_timeout(time.time() + 300, self.scanSymbol)

    def profit_rate(self, price1, price2):
        #TODO calc the cost
        return abs(price1 - price2) / price1 

    def check_trade(self, symbol, ex1, price1, ex2, price2):
        flag = False
        trade = None

        bid1 = price1['bids'][0]
        ask1 = price1['asks'][0]
        bid2 = price2['bids'][0]
        ask2 = price2['asks'][0]

        if ask1 < bid2 and profit_rate(ask1, bid2) > self.trade_rate:
            flag = True
            trade = Trade(symbol, ex_dict[ex1], ask1, price1['asks'][1], ex_dict[ex2], bid2, price2['bids'][1])
            return flag, trade

        if ask2 < bid1 and profit_rate(ask2, bid1) < self.trade_rate:
            flag = True
            trade = Trade(symbol, ex_dict[ex2], ask2, price2['asks'][1], ex_dict[ex1], bid1, price1['bids'][1])
            return flag, trade            


    @coroutine
    def risk(self,trade):
        buyer = trade.buyer
        #TODO get symbol amount
        now_amount = yield buyer.get_amount(trade.symbol)
        if abs(now_amount - init_amount['symbol'])/init_amount > rsik_rate:
            return True
        seller = trader.seller
        now_amount = yield seller.get_amount(trade.symbol)
        if abs(now_amount - init_amount['symbol'])/init_amount > rsik_rate:
            return True        
        return False
        

    def push(self,trade):
        if self.risk(trade):
            pass
        else:
            self.tset.push(trade)


    def scanSymbol(self):
        self.data = Cache.instance()
        # '''
        # self.data = {
        #     'r_usdt':{'okex':{'bids': [0.9724, 265.75107117], 'asks': [1.1, 48.2973]},
        #               'binan':{'bids': [0.9824, 265.75107117], 'asks': [1.3, 48.2973]},
        #               'huobi':{'bids': [0.9624, 265.75107117], 'asks': [1.2, 48.2973]}
        #              }
        # }
        # '''
        alogger.info('scan symbol start')
        for symbol, value in self.data.data.iteritems():
            exs = self.data.data[symbol].keys()
            perm_list = util.permutation(exs)
            for item in perm_list:
                try:
                    ex1 = item[0]
                    ex2 = item[1]
                    price1 = self.data.get(symbol, ex1)
                    price2 = self.data.get(symbol, ex2)
                    flag, trade = self.check_trade(symbol, ex1, price1, ex2, price2)
                    if flag:
                        self.push(trade)
                except Exception as e:
                    alogger.exception(e)
        print 'scan symbol end'
        IOLoop.instance().add_timeout(time.time() + 1, self.scanSymbol)                    

if __name__ == '__main__':
    Druid.instance().start()
    IOLoop.instance().start()

