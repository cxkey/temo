from singleton import singleton
from logger import alogger, elogger
from cache import Cache
from copy import deepcopy
from tornado.ioloop import IOLoop
from util import permutation
import time

class Trade:
    def __init__(self,symbol):
        self.symbol = symbol
        self.buyer = None
        self.seller = None
        self.amount = 0
        self.buy_price = 0.00
        self.sell_price = 0.00
        self.status = 0 #0:未交易 1:已交易

    def set_amount(self,amount):
        self.amount = amount

    def set_buyer(self,buyer):
        self.buyer = buyer

    def set_seller(self,seller):
        self.seller = seller


@singleton
class TradeSet:
    def __init__(self):
        self.max_trade_num = 10 #同时最多有10笔交易
        self.trades = {}

    def push(self,trade):
        if len(self.trades) > self.max_trade_num:
            return
        key = trade.symbol+'_' + trade.buyer + '_' + trade.seller
        if key in self.trades.keys():
            return
        self.trades[key] = trade

    def del(self,trade):
        key = trade.symbol+'_' + trade.buyer + '_' + trade.seller
        if key in self.trades.keys():
            del self.trades[key]
   


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
        return abs(price1-price2)/price1 

<<<<<<< HEAD

    def check_trade(self, symbol, ex1,price1,ex2,price2):
        flag = False
        trade = None
        bid1 = price1['bids'][0]
        ask1 = price1['ask'][0]
        bid2 = price2['bids'][0]
        ask2 = price2['ask'][0]
        if (ask1 < bid2) and profit_rate(ask1,bid2) > self.trade_rate:
            flag = True
            trade = Trade()
            trade.set_buyer(ex1)
            trade.set_seller(ex2)
        if (ask2 < bid1) and profit_rate(ask2,bid1) < self.trade_rate:
            flag = True
            trade = Trade()
            trade.set_buyer(ex2)
            trade.set_seller(ex1)
        return flag,trade            


    def permutation(self, array):
        perm_list = []
        for i in range(0, len(array)):
            for j in range(i+1, len(array)):
                perm_list.append([array[i],array[j]])
        return perm_list         

    def pushtrade(self):
        

    def scanSymbol(self):
        self.data = Cache.instance()
        print 'scan symbol start'
=======
    def diff(self, price1,price2):
        bid = price1['bids'][0]
        ask = price2['asks'][0]
        print bid, ask, self.profit(bid,ask)
        if self.profit(bid,ask) >= 0.1:
            return True
        else:
            return False

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
>>>>>>> 90f365773e5e7ca3f7e096ad49943d7ba10f9b80
        for symbol, value in self.data.data.iteritems():
            exs = self.data.data[symbol].keys()
            perm_list = util.permutation(exs)
            for item in perm_list:
                try:
<<<<<<< HEAD
                    ex1 = item[0]
                    ex2 = item[1]
                    price1 = self.data.get(symbol,ex1)
                    price2 = self.data.get(symbol,ex2)
                    flag,trade =  self.check_trade(symbol,ex1,price1,ex2,price2)
                    if flag:
                        self.tset.push(trade)
                        #redis.set(trade)
=======
                    price1 = self.data.get(symbol, item[0])
                    price2 = self.data.get(symbol, item[1])
                    
                    if self.diff(price1,price2):
                        print symbol, item, 'can trade'
                    else:
                        print symbol, item, 'can not trade'
>>>>>>> 90f365773e5e7ca3f7e096ad49943d7ba10f9b80
                except Exception as e:
                    alogger.exception(e)
        print 'scan symbol end'
        IOLoop.instance().add_timeout(time.time() + 1, self.scanSymbol)                    
<<<<<<< HEAD

   
        
=======
>>>>>>> 90f365773e5e7ca3f7e096ad49943d7ba10f9b80

if __name__ == '__main__':
    Druid.instance().start()
    IOLoop.instance().start()

