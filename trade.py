from singleton import singleton
from Queue import Queue  


class Trade:
    def __init__(self, symbol, buyer, buy_price, buy_amount, seller, sell_price, sell_amount):
        self.symbol = symbol

        self.buyer = buyer #exchange instance
        self.buy_price = buy_price
        self.buy_amount = buy_amount

        self.seller = seller #exchange instance
        self.sell_price = sell_price
        self.sell_amount = sell_amount

        self.status = 0 # 0:未交易 1:交易succ  -1:fail


@singleton
class TradeSet:
    def __init__(self):
        self.queue = Queue()

    def push(self, trade):
        self.queue.put(trade)

    def pop(self):
        trade = None
        try:
            trade = self.queue.get(False)
        except Exception as e:
            alogger.exception(e)
        return trade            
