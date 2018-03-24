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
from profit import *

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
        #cal_single_prodit(params)

    def __str__(self):
        return '[%s] buyer:%s,%s,%s,%s, seller:%s,%s,%s,%s' % (self.symbol, self.buyer.name, \
                str(self.buy_price.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_EVEN)), \
                str(self.buy_amount), \
                str(self.buyer_asset_amount), \
                self.seller.name, \
                str(self.sell_price.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_EVEN)), \
                str(self.sell_amount), \
                str(self.seller_asset_amount)) 


    @gen.coroutine
    def make_deal(self, amount):
        # TODO 如果一方失败, 另一方要尝试回滚 
        
        # 先卖, 后买
        #yield self.seller.create_trade(symbol=self.symbol, amount=amount, side=SELL)
        #yield self.buyer.create_trade(symbol=self.symbol, amount=amount, side=BUY)

        alogger.info('make_deal1')
        self.db_action(Trade.SELL, amount, Decimal(1), Trade.TRADE_SUCCESS)
        alogger.info('make_deal2')
        self.db_action(Trade.BUY, amount, Decimal(1), Trade.TRADE_SUCCESS)
        alogger.info('make_deal3')

    @gen.coroutine
    def calc_final_amount(self):
        # 小币, 主币
        asset, base = self.symbol.split('_')[0], self.symbol.split('_')[1]

        if conf.ENV == 'test':
            buyer_base_balance = 500
            init_amount = 1000
        else:
            buyer_base_balance = yield self.buyer.get_asset_amount(base)
            init_amount = conf.INIT_AMOUNT[asset]['amount']

        buy_amount = min(init_amount * (1 + conf.RISK_RATE) - self.buyer_asset_amount, \
                         buyer_base_balance / self.buy_price, \
                         self.buy_amount)

        sell_amount = min(self.seller_asset_amount - init_amount * (1 - conf.RISK_RATE), \
                          self.seller_asset_amount,
                          self.sell_amount)
        alogger.info('buy:{}, sell:{}'.format(buy_amount, sell_amount))
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
        if abs(self.buyer_asset_amount - conf.INIT_AMOUNT[asset]['amount']) / conf.INIT_AMOUNT[asset]['amount'] > conf.RISK_RATE:
            raise gen.Return(True)
            return

        trade.seller_asset_amount = yield trade.seller.get_asset_amount(asset)
        if abs(trade.seller_asset_amount - conf.INIT_AMOUNT[asset]['amount']) / conf.INIT_AMOUNT[asset]['amount'] > conf.RISK_RATE:
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
                # liubida real_check_result = yield trade.check()
                real_check_result = True
                if real_check_result:
                    # liubida amount = yield trade.calc_final_amount()
                    amount = 100
                    if amount > 0 :
                        # TODO 这里还要考虑下
                        alogger.info('!deal! {}'.format(str(trade)))
                        trade.make_deal(amount)
                    else:
                        alogger.info('amount is invalid. {}. {}'.format(amount, str(trade)))
                else:
                    alogger.info('trade real_check fail: %s' % str(trade))
            except Exception as e :
                alogger.exception(e)

def test():
    t = Trade('ost_eth', HuobiEx.instance(), Decimal('0.99'), 100, OkexEx.instance(), Decimal('1.20'), 100)
    TradeSet.instance().produce(t) 

    #t = Trade('ost_eth', OkexEx.instance(), Decimal('1.10'), 100, HuobiEx.instance(), Decimal('1.30'), 100)
    #TradeSet.instance().produce(t) 

if __name__ == '__main__':
    init_logger('.')
    test()
    IOLoop.instance().start()

