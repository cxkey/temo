# encoding: utf-8
from singleton import singleton
from Queue import Queue  
from util import *
from init import *
import conf
from exchange.enum import *
from tornado.gen import coroutine

class Trade:
    def __init__(self, symbol, buyer, buy_price, buy_amount, seller, sell_price, sell_amount):
        self.symbol = symbol

        self.buyer = buyer # exchange instance
        self.buy_price = buy_price
        self.buy_amount = buy_amount
        self.buyer_asset_amount = None

        self.seller = seller # exchange instance
        self.sell_price = sell_price
        self.sell_amount = sell_amount
        self.seller_asset_amount = None

        self.status = 0 # 0: 未交易 1: 交易成功  -1: 交易失败

    def __str__(self):
        return '[%s] buyer:%s,%s,%s,%s, seller:%s,%s,%s,%s' % (self.symbol, self.buyer.name, str(self.buy_price), \
                str(self.buy_amount), str(self.buyer_asset_amount), self.seller.name, str(self.sell_price), \
                str(self.sell_amount), str(self.seller_asset_amount)) 

    @coroutine
    def make_deal(self, amount):
        # TODO 如果一方失败, 另一方要尝试回滚 
        
        # 先卖, 后买
        yield trade.seller.create_trade(symbol=self.symbol, amount=amount, side=SELL)

        yield trade.buyer.create_trade(symbol=self.symbol, amount=amount, side=BUY)

    @coroutine
    def calc_final_amount(self):
        # 小币, 主币
        asset, base = self.symbol.split('_')[0], self.symbol.split('_')[1]

        buyer_base_balance = yield buyer.get_assert_amount(base)
        buy_amount = min(conf.INIT_AMOUNT[asset] * (1 + conf.RISK_RATE) - self.buyer_asset_amount, \
                         buyer_base_balance / self.buy_price, \
                         self.buy_amount)

        sell_amount = min(seller_now_amount - conf.INIT_AMOUNT[asset] * (1 - conf.RISK_RATE), \
                          self.seller_asset_amount,
                          self.sell_amount)
        trade_amount = min(buy_amount, sell_amount)
        raise gen.Return(trade_amount)

    @coroutine
    def check(self):
        # 再检查一遍实时数据，是否能继续交易

        price1 = yield self.buyer.get_depth(self.symbol)
        price2 = yield self.seller.get_depth(self.symbol) 

        bid1, bid1_amount = price1['bids'][0], price1['bids'][1] 
        ask1, ask1_amount = price1['asks'][0], price1['asks'][1]
        bid2, bid2_amount = price2['bids'][0], price2['bids'][1]
        ask2, ask2_amount = price2['asks'][0], price2['asks'][1]

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

    @coroutine
    def has_risk(self):
        asset = self.symbol.split('_')[0]
        raise gen.Return(False)
        return

        self.buyer_asset_amount = yield self.buyer.get_asset_amount(asset)
        if abs(self.buyer_asset_amount - conf.INIT_AMOUNT[asset]) / conf.INIT_AMOUNT[asset] > conf.RISK_RATE:
            raise gen.Return(True)
            return

        trade.seller_asset_amount = yield trade.seller.get_asset_amount(asset)
        if abs(trade.seller_asset_amount - conf.INIT_AMOUNT[asset]) / conf.INIT_AMOUNT[asset] > conf.RISK_RATE:
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
            trade = self.queue.get(False)
        except Exception as e:
            alogger.exception(e)
        return trade  
    
    def produce(self, trade):
        self.queue.put(trade)
        if self._thread == None or self._thread.is_alive() == False:
            self._thread = threading.Thread(target=self._process)
            self._thread.start()

    @coroutine
    def _process(self):
        while True:
            trade = self.pop()
            if trade == None:
                alogger.info('no trade to do now')
                return
            try:
                real_check_result = yield trade.check()
                if real_check_result:
                    amount = yield trade.calc_final_amount()
                    if amount > 0 :
                        # TODO 这里还要考虑下
                        trade.make_deal(amount)
                else:
                    alogger.info('trade real_check fail: %s' % str(trade))
            except Exception as e :
                alogger.exception(e)

