from singleton import singleton
from logger import alogger, elogger
from cache import Cache
from copy import deepcopy
from tornado.ioloop import IOLoop
from util import permutation
import time
from decimal import Decimal

class Trade:
    def __init__(self, symbol, buyer, buy_price, buy_amount, seller, sell_price, sell_amount):
        self.symbol = symbol

        self.buyer = buyer
        self.buy_price = buy_price
        self.buy_amount = buy_amount

        self.seller = seller
        self.sell_price = sell_price
        self.sell_amount = sell_amount

        #self.key = self.symbol + '_' + self.buyer + '_' + self.seller
        self.key = self.symbol + '_' + '_'.join(sorted[self.buyer, self.seller])

        self.status = 0 # 0:未交易 1:交易succ  -1:fail
    
    def flag(self):
        a = sorted[self.buyer, self.seller]
        if a[0] == self.buyer:
            return True
        else:
            return False
        
    def profit11(self):
        #return self.sell_price * self.sell_amount - self.buy_price * self.buy_amount
        return self.buy_price * self.buy_amount

    def oppsite(self, o):
        if o is None
            return False

        if self.symbol == o.symbol and \
            self.buyer == o.seller and \
            self.seller == o.buyer:
            return True

        return False

@singleton
class TradeSet:
    def __init__(self):
        self.max_trade_num = 10 # 同时最多有10个交易对
        '''
        {
            'iost_eth_ex1_ex2': {
                'ex1': [t1, t2],  //此时 t1, t2 的 buyer 都为 ex1
                'ex2': [t3, t4],  //此时 t3, t4 的 buyer 都为 ex2
            },
            'iost_eth_ex1_ex2': [t1, t2],
            'iost_eth_ex1_ex3': {
                'ex1': [t1, t2],
                'ex3': [t3, t4],
            }
        }
        '''
        self.queue = {}

    def risk_value(self, key):
        if key not in self.queue.keys():
            return 0

        trade_sequence = self.queue[key]

        s = Decimal(0.0)
        for ts in trade_sequence:
            if ts.flag():
                s += Decimal(ts.profit11())
            else:
                s -= Decimal(ts.profit11())

        return s

    def push(self, trade):
        if trade.key not in self.queue.keys():
            if len(self.queue.keys()) >= self.max_trade_num:
                print 'bbb'
                return
            else:
                self.queue[trade.key] = [trade]
        else:
            # 正交易的风险值

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
            trade = Trade(symbol, ex1, ask1, price1['asks'][1], ex2, bid2, price2['bids'][1])
            return flag, trade

        if ask2 < bid1 and profit_rate(ask2, bid1) < self.trade_rate:
            flag = True
            trade = Trade(symbol, ex2, ask2, price2['asks'][1], ex1, bid1, price1['bids'][1])
            return flag, trade            

    def permutation(self, array):
        perm_list = []
        for i in range(0, len(array)):
            for j in range(i+1, len(array)):
                perm_list.append([array[i],array[j]])
        return perm_list         

    def pushtrade(self):
        pass

    def scanSymbol(self):
        self.data = Cache.instance()
        print 'scan symbol start'

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
                        self.tset.push(trade)
                        #redis.set(trade)
                except Exception as e:
                    alogger.exception(e)
        print 'scan symbol end'
        IOLoop.instance().add_timeout(time.time() + 1, self.scanSymbol)                    

if __name__ == '__main__':
    Druid.instance().start()
    IOLoop.instance().start()

