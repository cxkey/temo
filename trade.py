from singleton import singleton
from Queue import Queue  
from util import *
from init import *
import conf


class Trade:
    def __init__(self, symbol, buyer, buy_price, buy_amount, seller, sell_price, sell_amount):
        self.symbol = symbol

        self.buyer = buyer #exchange instance
        self.buy_price = Deciaml(buy_price)
        self.buy_amount = Decimal(buy_amount)

        self.seller = seller #exchange instance
        self.sell_price = Decimal(sell_price)
        self.sell_amount = Decimal(sell_amount)

        self.status = 0 # 0:未交易 1:交易succ  -1:fail


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
    
    def produce(self):
        self.put(trade)
        if self._thread == None or self._thread.is_alive() == False:
            self._thread = threading.Thread(target=self._process)
            self._thread.start()

    @coroutine
    def get_trade_amount(self,trade):
        #小币
        asset_1 = trade.symbol.split('_')[0]
        #主币
        balance = trade.symbol.split('_')[1]
        asset_init_amount = init_amount[asset]        
        buyer_now_amount = yield buyer.get_asset_amount(asset)
        buyer_balance = yield buyer.get_assert_amount(balance)
        buy_amount = min(asset_init_amount *(1 + RISK_RATE) - buyer_now_amount, \
                buyer_balance / trade.buy_price, trade.buy_amount)
        seller_now_amount = yield seller.get_asset_amount(asset)
        sell_amount = min(seller_now_amount - asset_init_amount * (1-) RISK_RATE,\
                trade.sell_amount, seller_now_amount)
        trade_amount = min(buy_amount,sell_amount)
        raise gen.Return(trade_amount)


    @coroutine
    def check_trade(self,trade):
        #再检查一遍实时数据，是否能继续交易            
        price1 = yield trade.buyer.get_depth(trade.symbol)                            
        price2 = yield trade.seller.get_depth(trade.symbol) 
        bid1 = price1['bids'][0]
        ask1 = price1['asks'][0]
        bid2 = price2['bids'][0]
        ask2 = price2['asks'][0]
        if (Decimal(ask1) < Decimal(bid2)) and util.profit_rate(ask1,bid2) > conf.PROFIT_RATE:
            trade.buy_price = Decimal(ask1)
            trade.sell_price = Decimal(bid2)
            raise gen.Return(True)
        elif (Decimal(ask2) < Decimal(bid1)) and util.profit_rate(ask2, bid1) > conf.PROFIT_RATE: 
            #情况逆转，交换买卖双方
            tmp = trade.buyer
            trade.buyer = trade.seller
            trade.buy_price = Decimal(ask2)
            trade.seller = tmp
            trade.sell_price = Decimal(bid1)
            raise gen.Return(True)
        raise gen.Return( False)

    @coroutine
    def _process(self):
        while True:
            trade = self.pop()
            if trade == None:
                alogger.info('no trade to do now')
                return
            try:
                if self.check_trade(trade):            
                    amount = yield self.get_trade_amount()
                    yield trade.buyer.create_trade(symbol,amount,buy)
                    yield trade.seller.create_trade(symbol,amount,sell)
            except Exception as e :
                alogger.exception(e)


