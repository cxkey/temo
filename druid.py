from singleton import singleton
from logger import alogger, elogger
from cache import Cache
from copy import deepcopy
from tornado.ioloop import IOLoop
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
        for symbol, value in self.data.data.iteritems():
            exs = self.data.data[symbol].keys()
            perm_list = self.permutation(exs)
            for item in perm_list:
                try:
                    ex1 = item[0]
                    ex2 = item[1]
                    price1 = self.data.get(symbol,ex1)
                    price2 = self.data.get(symbol,ex2)
                    flag,trade =  self.check_trade(symbol,ex1,price1,ex2,price2)
                    if flag:
                        self.tset.push(trade)
                        #redis.set(trade)
                except Exception as e:
                    continue
        print 'scan symbol end'
        IOLoop.instance().add_timeout(time.time() + 1, self.scanSymbol)                    

   
        

if __name__ == '__main__':
    Druid.instance().start()
    IOLoop.instance().start()

