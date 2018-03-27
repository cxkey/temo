# encoding: utf-8
from singleton import singleton
from Queue import Queue  
from util import *
from init import *
import conf
from logger import init_logger, alogger, elogger
from exchange.enum import *
from tornado import gen
import threading
import util
from decimal import *
from dao import DBTrade, DBProfit
from exchange.binan import BinanceEx 
from exchange.huobi import HuobiEx  
from exchange.okex import OkexEx  
import datetime
from redisclient import *
from tornado.ioloop import IOLoop

class Trade:

    BUY, SELL = 0, 1
    # 0: 未交易 1: 交易成功  -1:交易失败
    TRADE_INIT, TRADE_SUCCESS, TRADE_FAIL = 0, 1, -1 

    def __init__(self, symbol, buyer, buy_price, buy_amount, seller, sell_price, sell_amount):
        self.symbol = symbol

        self.tid = util.gen_id()

        self.buyer = buyer # exchange instance
        self.buy_price = buy_price
        self.buy_amount = buy_amount
        self.buyer_asset_amount = None

        self.seller = seller # exchange instance
        self.sell_price = sell_price
        self.sell_amount = sell_amount
        self.seller_asset_amount = None

        self.status = Trade.TRADE_INIT

    def db_action(self, side, amount, fee, status):
        params = {}
        params['tid'] = self.tid
        params['quote'] = self.symbol.split('_')[0]
        params['base'] = self.symbol.split('_')[1]
        params['side'] = side
        params['status'] = status
        params['fee'] = fee
        params['deal_amount'] = amount
        params['create_time'] = datetime.datetime.now()

        if side == Trade.BUY:
            params['exchange'] = self.buyer.name
            params['price'] = self.buy_price
            params['amount'] = self.buy_amount
            params['deal_price'] = self.buy_price
        else:            
            params['exchange'] = self.seller.name
            params['price'] = self.sell_price
            params['amount'] = self.sell_amount
            params['deal_price'] = self.sell_price

        DBTrade.instance().insert(params)

    def __str__(self):
        return '[%s|%s] [buyer:%s|%s|%s|%s] [seller:%s|%s|%s|%s]' % (self.tid, self.symbol, self.buyer.name, \
                str(self.buy_price.quantize(Decimal('0.0000000001'), rounding=ROUND_HALF_EVEN)), \
                str(self.buy_amount), \
                str(self.buyer_asset_amount), \
                self.seller.name, \
                str(self.sell_price.quantize(Decimal('0.0000000001'), rounding=ROUND_HALF_EVEN)), \
                str(self.sell_amount), \
                str(self.seller_asset_amount)) 

    @gen.coroutine
    def make_deal(self, amount):
        # TODO 如果一方失败, 另一方要尝试回滚 
        
        # 先卖, 后买
        r_sell = yield self.seller.create_trade(symbol=self.symbol, amount=amount, price=self.sell_price, side=SELL)
        alogger.info('make deal:SELL res:{}, trade:{} amount:{}'.format(str(r_sell), self.__str__(), amount))
        # TODO 1. Decimal(1); 2. Trade.TRADE_SUCCESS 
        self.db_action(Trade.SELL, amount, Decimal(1), Trade.TRADE_SUCCESS)

        r_buy = yield self.buyer.create_trade(symbol=self.symbol, amount=amount, price=self.buy_price, side=BUY)
        alogger.info('make deal:BUY res:{}, trade:{} amount:{}'.format(str(r_buy), self.__str__(), amount))
        self.db_action(Trade.BUY, amount, Decimal(1), Trade.TRADE_SUCCESS)

        # TODO the exchange.create_trade should return the same format. it is defined in the class Exchange 
        if True or (r_sell.status and r_buy.status):
            elogger.info('&DEAL1, {}, amount:{}'.format(str(trade), amount))

    @gen.coroutine
    def calc_final_amount(self):
        # 小币, 主币
        asset, base = self.symbol.split('_')[0], self.symbol.split('_')[1]

        if conf.ENV == 'test':
            buyer_base_balance = 500
            init_amount = 1000
        else:
            buyer_base_balance = yield self.buyer.get_asset_amount(base)
            buyer_init_amount = Decimal(conf.INIT_AMOUNT[asset][self.buyer.name]['amount'])
            seller_init_amount = Decimal(conf.INIT_AMOUNT[asset][self.seller.name]['amount'])

        #print 'debug 1', buyer_base_balance,buyer_init_amount,seller_init_amount
        #print 'debug 2', buyer_init_amount * Decimal(1 + conf.RISK_RATE)
        #print 'debug 3', self.buyer_asset_amount
        #print 'debug 4', buyer_base_balance / self.buy_price, self.buy_price
        #print 'debug 5', self.buy_amount
        buy_amount = min(buyer_init_amount * Decimal(1 + conf.RISK_RATE) - self.buyer_asset_amount, \
                         buyer_base_balance / self.buy_price, \
                         self.buy_amount)

        sell_amount = min(self.seller_asset_amount - seller_init_amount * Decimal(1 - conf.RISK_RATE), \
                          self.seller_asset_amount,
                          self.sell_amount)
        alogger.info('[{}] buy:{}, sell:{}'.format(self.tid, buy_amount, sell_amount))
        trade_amount = min(buy_amount, sell_amount)
        raise gen.Return(trade_amount)

    @gen.coroutine
    def check(self):
        # 再检查一遍实时数据，是否能继续交易
        price1 = yield self.buyer.get_depth(self.symbol)
        price2 = yield self.seller.get_depth(self.symbol) 

        if len(price1['bids']) > 0 and len(price1['asks']) > 0 and \
            len(price2['bids']) > 0 and len(price2['asks']) > 0:
            bid1, bid1_amount = price1['bids'][0], price1['bids'][1] 
            ask1, ask1_amount = price1['asks'][0], price1['asks'][1]
            bid2, bid2_amount = price2['bids'][0], price2['bids'][1]
            ask2, ask2_amount = price2['asks'][0], price2['asks'][1]
        else:
            raise gen.Return(False)
            return

        if ask1 < bid2 and util.profit_rate(ask1, bid2) > conf.PROFIT_RATE:
            self.buy_price = ask1
            self.buy_amount = ask1_amount
            self.sell_price = bid2
            self.sell_amount = bid2_amount 
        elif ask2 < bid1 and util.profit_rate(ask2, bid1) > conf.PROFIT_RATE: 
            # 情况逆转，交换买卖双方
            tmp = self.buyer
            self.buyer = self.seller
            self.buy_price = ask2
            self.buy_amount = ask2_amount
            self.seller = tmp
            self.sell_price = bid1
            self.sell_amount = bid1_amount
        else:
            raise gen.Return(False)

        ret_risk = yield self.has_risk()
        if not ret_risk:
            raise gen.Return(True)
        else:
            raise gen.Return(False)

    @gen.coroutine
    def has_risk(self):
        asset = self.symbol.split('_')[0]

        if conf.ENV == 'test':
            self.buyer_asset_amount = 800
            self.seller_asset_amount = 600
            raise gen.Return(False)
            return

        self.buyer_asset_amount = yield self.buyer.get_asset_amount(asset)
        if abs(self.buyer_asset_amount - conf.INIT_AMOUNT[asset][self.buyer.name]['amount']) / conf.INIT_AMOUNT[asset][self.seller.name]['amount'] > conf.RISK_RATE:
            raise gen.Return(True)
            return

        self.seller_asset_amount = yield self.seller.get_asset_amount(asset)
        if abs(self.seller_asset_amount - conf.INIT_AMOUNT[asset][self.seller.name]['amount']) / conf.INIT_AMOUNT[asset][self.seller.name]['amount'] > conf.RISK_RATE:
            raise gen.Return(True)
            return

        raise gen.Return(False)

@singleton
class TradeSet:
    def __init__(self):
        self.queue = Queue()
        self._thread = None

    def push(self, trade):
        self.queue.put(trade)

    def pop(self):
        trade = None
        try:
            trade = self.queue.get(True, 5)
        except Exception as e:
            pass
        finally:
            return trade  
    
    def produce(self, trade):
        self.queue.put(trade)
        if self._thread == None or self._thread.is_alive() == False:
            self._thread = threading.Thread(target=self._process)
            self._thread.start()

    @gen.coroutine
    def _process(self):
        while True:
            trade = self.pop()
            if trade is None:
                alogger.info('trade_set is empty')
                continue
            try:
                ret_risk = yield trade.has_risk()
                real_check_result = yield trade.check()
                if real_check_result:
                    alogger.info('real_check success. tid:{}'.format(str(trade.tid)))
                    amount = yield trade.calc_final_amount()
                    if amount > 0 :
                        # TODO 这里还要考虑下
                        alogger.info('calc success. tid:{} amount:{}'.format(str(trade.tid), amount))
                        elogger.info('&CONFIRM, {}, amount:{}'.format(str(trade), amount))
                        trade.make_deal(amount)
                    else:
                        alogger.info('calc fail: amount is invalid. tid:{} amount:{}'.format(str(trade.tid), amount))
                else:
                    alogger.info('real_check fail. tid:{}'.format(str(trade.tid)))
            except Exception as e :
                alogger.info('trade process exception. tid:{}'.format(str(trade.tid)))
                alogger.exception(e)

def test():
    t = Trade('ost_eth', HuobiEx.instance(), Decimal('0.0003472'), 100, OkexEx.instance(), Decimal('0.0003488'), 100)
    TradeSet.instance().produce(t) 

if __name__ == '__main__':
    init_logger('.')
    test()
    IOLoop.instance().start()

