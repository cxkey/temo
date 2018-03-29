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
    # 0: 未交易 1: 部分成交  2:完全成交  -1:交易失败 -2:交易取消
    TRADE_INIT, TRADE_PARTIALLY_SUCCESS, TRADE_FILLED_SUCCESS, TRADE_FAIL, TRADE_CANCELED = 0, 1, 2, -1 ,-2

    def __init__(self, symbol, buyer, buy_price, buy_amount, seller, sell_price, sell_amount):
        self.symbol = symbol

        self.tid = util.gen_id()

        self.buyer = buyer # exchange instance
        self.buy_price = buy_price
        self.buy_amount = buy_amount
        self.buyer_asset_amount = None
        self.buyer_order_id = None

        self.seller = seller # exchange instance
        self.sell_price = sell_price
        self.sell_amount = sell_amount
        self.seller_asset_amount = None
        self.seller_order_id = None

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
            params['ex_tid'] = self.buyer_order_id
            params['price'] = self.buy_price
            params['amount'] = self.buy_amount
            params['deal_price'] = self.buy_price
        else:            
            params['exchange'] = self.seller.name
            params['ex_tid'] = self.seller_order_id
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
        sell_success,sell_id = yield self.seller.create_trade(symbol=self.symbol, amount=amount, price=self.sell_price, side=SELL)
        alogger.info('make deal:SELL res:{}, trade:{} amount:{}'.format(str(sell_success), self.__str__(), amount))
        if not sell_success:
            alogger.info('&SELL_FAIL,DEAL_STOP,{}'.format(self.tid))
            return

        buy_success,buy_id = yield self.buyer.create_trade(symbol=self.symbol, amount=amount, price=self.buy_price, side=BUY)
        alogger.info('make deal:BUY res:{}, trade:{} amount:{}'.format(str(buy_success), self.__str__(), amount))
        if buy_success:
            #卖和买都提交成功了
            self.seller_order_id = sell_id
            self.buyer_order_id = buy_id
            self.db_action(Trade.SELL, amount, Decimal(1), Trade.TRADE_INIT)
            self.db_action(Trade.BUY, amount, Decimal(1), Trade.TRADE_INIT)
            sell_item = {'ex':self.seller,'id':self.seller_order_id,'symbol':self.symbol}
            buy_item = {'ex':self.buyer,'id':self.buyer_order_id,'symbol':self.symbol}
            TradeSet.instance().add_check(sell_item)
            TradeSet.instance().add_check(buy_item)
            elogger.info('&DEAL1, {}, amount:{}'.format(self.__str__(), amount))
        else:
            #买失败，尝试回滚卖方交易
            yield self.seller.cancel_trade()
            self.seller_order_id = sell_id
            self.db_action(Trade.SELL, amount, Decimal(1), Trade.TRADE_INIT)
            self.seller_order_id = sell_id
            sell_item = {'ex':self.seller,'id':self.seller_order_id,'symbol':self.symbol}
            TradeSet.instance().add_check(sell_item)
            elogger.info('&BUY_FAIL,TRY_ROLLBACK_SELL,{}'.format(self.tid))


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

        alogger.info('---------------{}------------------'.format(self.tid))
        alogger.info('{}, 买家主币的数量:{}, 买家小币初始量:{}, 卖家小币初始量:{}'.format(self.tid, buyer_base_balance, buyer_init_amount, seller_init_amount))
        alogger.info('{}, 买家小币最大持有量:{}'.format(self.tid, buyer_init_amount * Decimal(1 + conf.RISK_RATE)))
        alogger.info('{}, 买家小币当前已有数量:{}'.format(self.tid, self.buyer_asset_amount))
        alogger.info('{}, 买家小币最大能买量:{}, 买家小币价格{}'.format(self.tid, buyer_base_balance / self.buy_price, self.buy_price))
        alogger.info('{}, 深度小币量:{}'.format(self.tid, self.buy_amount))

        alogger.info('{}, 卖家小币初始量:{}, 卖家小币初始量:{}'.format(self.tid, seller_init_amount, buyer_init_amount))
        alogger.info('{}, 卖家小币最少持有量:{}'.format(self.tid, seller_init_amount * Decimal(1 - conf.RISK_RATE)))
        alogger.info('{}, 卖家小币当前已有数量:{}'.format(self.tid, self.seller_asset_amount))
        alogger.info('{}, 深度小币量:{}'.format(self.tid, self.sell_amount))
        alogger.info('---------------{}------------------'.format(self.tid))

        buy_amount = min(buyer_init_amount * Decimal(1 + conf.RISK_RATE) - self.buyer_asset_amount, \
                         buyer_base_balance / self.buy_price, \
                         self.buy_amount)

        sell_amount = min(self.seller_asset_amount - seller_init_amount * Decimal(1 - conf.RISK_RATE), \
                          self.seller_asset_amount,
                          self.sell_amount)
        alogger.info('[{}] buy:{}, sell:{}'.format(self.tid, buy_amount, sell_amount))
        trade_amount = min(buy_amount, sell_amount)


        binance_strict = {
            'eth': Decimal(0.01),
            'btc': Decimal(0.001),
        }
        asset = self.symbol.split('_')[0]
        base = self.symbol.split('_')[1]
        if self.buyer.name == 'binance' and base in binance_strict.keys():
            if self.buy_price * trade_amount <= binance_strict[base]:
                alogger.info('has_risk strict {}'.format(self.__str__()))
                raise gen.Return(Decimal('0'))
        if self.seller.name == 'binance' and base in binance_strict.keys():
            if self.sell_price * trade_amount <= binance_strict[base]:
                alogger.info('has_risk strict {}'.format(self.__str__()))
                raise gen.Return(Decimal('0'))
        if self.buyer.name == 'okex' and  trade_amount < 10:
            alogger.info('has_risk strict {}'.format(self.__str__()))
            raise gen.Return(Decimal('0'))
        if self.seller.name == 'okex' and trade_amount < 10:
            alogger.info('has_risk strict {}'.format(self.__str__()))
            raise gen.Return(Decimal('0'))

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
        base = self.symbol.split('_')[1]

        if conf.ENV == 'test':
            self.buyer_asset_amount = 800
            self.seller_asset_amount = 600
            raise gen.Return(False)
            return

        self.buyer_asset_amount = yield self.buyer.get_asset_amount(asset)
        self.seller_asset_amount = yield self.seller.get_asset_amount(asset)
        raise gen.Return(False)
        #if abs(Decimal(self.buyer_asset_amount)  + Decimal(self.buyer_amount) / conf.INIT_AMOUNT[asset][self.seller.name]['amount'] > conf.RISK_RATE:
        #    alogger.info('has_risk buy risk {} buyer_asset_amount:{} buyer_init_amount:{}'.format(self.__str__(), self.buyer_asset_amount, conf.INIT_AMOUNT[asset][self.buyer.name]['amount']))
        #    raise gen.Return(True)
        #    return

        #if abs(self.seller_asset_amount - conf.INIT_AMOUNT[asset][self.seller.name]['amount']) / conf.INIT_AMOUNT[asset][self.seller.name]['amount'] > conf.RISK_RATE:
        #    alogger.info('has_risk sell risk {} seller_asset_amount:{} seller_init_amount:{}'.format(self.__str__(), self.seller_asset_amount, conf.INIT_AMOUNT[asset][self.seller.name]['amount']))
        #    raise gen.Return(True)
        #    return


@singleton
class TradeSet:
    def __init__(self):
        self.queue = Queue()
        self.check_status_queue = Queue()
        self._thread = None

    def add_check(self,item):
        self.check_status_queue.put(item)

    def pop_check(self):
        item = None
        try:
            item = self.check_status_queue.get(False)
        except Exception as e:
            pass
        finally:
            return item

    def push(self, trade):
        self.queue.put(trade)

    def pop(self):
        trade = None
        try:
            trade = self.queue.get(False)
        except Exception as e:
            pass
        finally:
            return trade  
    
    def produce(self, trade):
        self.queue.put(trade)
        #if self._thread == None or self._thread.is_alive() == False:
        #    self._thread = threading.Thread(target=self._process)
        #    self._thread.start()

    @gen.coroutine
    def _process(self):
        while True:
            trade = self.pop()
            if trade is None:
                alogger.info('heart: trade_set is empty')
                IOLoop.instance().add_timeout(time.time() + 5, self._process)
                break
            try:
                #real_check_result = yield trade.check()
                real_check_result = True
                if real_check_result:
                    alogger.info('real_check success. tid:{}'.format(str(trade.tid)))
                    amount = yield trade.calc_final_amount()
                    #elogger.info('&REALCHECK, {}, amount:{}'.format(str(trade), amount))
                    if amount > Decimal('0') :
                        alogger.info('calc success. tid:{} amount:{}'.format(str(trade.tid), amount))
                        elogger.info('&CONFIRM, {}, amount:{}'.format(str(trade), amount))
                        yield trade.make_deal(amount)
                    else:
                        alogger.info('calc fail: amount is invalid. tid:{} amount:{}'.format(str(trade.tid), amount))
                else:
                    alogger.info('real_check fail. tid:{}'.format(str(trade.tid)))
            except Exception as e :
                alogger.info('trade process exception. tid:{}'.format(str(trade.tid)))
                alogger.exception(e)
                #IOLoop.instance().add_timeout(time.time() + 5, self._process)
    
    @gen.coroutine
    def check_status():
        while True:
            item = self.pop_check()
            if item is None:
                alogger.info('heart: check_status_queue is empty')
                IOLoop.instance().add_timeout(time.time() + 5, self.check_status)
                break
            try:
                ex = item['ex']
                status = yield ex.trade_info(item['symbol'],item['id'])
                if status == Trade.TRADE_INIT:
                    self.add_check(item)
                else:
                    params = {}
                    params['status'] = status
                    params['ex'] = item['ex'].name
                    params['ex_tid'] = item['id']
                    DBTrade.instance().update(params)
            except Exception as e:
                alogger.info('check status process exception. tid:{}'.format(str(trade.tid)))
                alogger.exception(e)
                            

    def start(self):
        IOLoop.instance().add_timeout(time.time() + 1, self._process)
        IOLoop.instance().add_timeout(time.time() + 10, self.check_status)

def test():
    t = Trade('ost_eth', HuobiEx.instance(), Decimal('0.0003472'), 100, OkexEx.instance(), Decimal('0.0003488'), 100)
    TradeSet.instance().produce(t) 

if __name__ == '__main__':
    init_logger('.')
    test()
    IOLoop.instance().start()

