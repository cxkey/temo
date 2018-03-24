# -*- coding: utf-8 -*-

from exchange import Exchange
from binance.client import Client
from binance.enums import *
from tornado import gen
from tornado.ioloop import IOLoop
import time
import threading

import sys
sys.path.append('../')
sys.path.append('../../')

import S

from singleton import singleton
from logger import alogger, elogger
from decimal import Decimal
from enum import *

api_key = S.KEYS['binance']['access_key']
api_secret = S.KEYS['binance']['secret_key']

@singleton
class BinanceEx(Exchange):
    
    def __init__(self):
        Exchange.__init__(self, 'binance')
        self.client = Client(api_key, api_secret)

    def _do_get_symbols(self, callback):
        r = self.client.get_exchange_info()
        IOLoop.instance().add_callback(callback, r)

    def _get_symbols(self, callback):
        threading.Thread(target=self._do_get_symbols, args=(callback,)).start()

    @gen.coroutine
    def get_symbols(self):
        r = yield gen.Task(self._get_symbols)
        if 'symbols' not in r:
            raise gen.Return(None)

        ret = {}
        for s in r['symbols']:
            try:
                if str(s['baseAsset'].lower()) == 'bnb' or \
                   str(s['quoteAsset'].lower()) == 'bnb':
                   continue
                item = {
                    'base': str(s['baseAsset'].lower()),
                    'quote': str(s['quoteAsset'].lower()),
                    'base_precision': s['baseAssetPrecision'],
                    'quote_precision': s['quotePrecision'],
                }
                ret['%s_%s' % (item['base'], item['quote'])] = item
            except Exception, e:
                alogger.exception(e)
                raise gen.Return(None)

        raise gen.Return(ret)

    def _do_get_depth(self, symbol, callback):
        r = self.client.get_order_book(symbol=symbol, limit=10)
        IOLoop.instance().add_callback(callback, r)

    def _get_depth(self, symbol, callback):
        threading.Thread(target=self._do_get_depth, args=(symbol, callback)).start()

    @gen.coroutine
    def get_depth(self, symbol):
        ret = {
            'bids': [],
            'asks': [],
        }
        if not symbol:
            raise gen.Return(None)

        symbol = symbol.replace('_', '').upper()
        #r = self.client.get_order_book(symbol=symbol, limit=10)
        r = yield gen.Task(self._get_depth, symbol)

        bids = r.get('bids', [])
        if bids:
            ret['bids'] = [Decimal(i) for i in bids[0][0:-1]]
        
        asks = r.get('asks', [])
        if asks:
            ret['asks'] = [Decimal(i) for i in asks[0][0:-1]]

        raise gen.Return(ret)

    def get_all_tickers(self):
        r = self.client.get_all_tickers()
        print r

    @gen.coroutine
    def get_history(self, symbol):
        ret = {}
        if not symbol:
            return None
        symbol = symbol.replace('_', '').upper()            
        r = self.client.get_historical_trades(symbol=symbol)
        for item in r:
            t1 = time.strftime("%Y%m%d%H%M", time.localtime(item['time']/1000))
            price = item['price']
            ret[t1] = price
            print t1,price
        return ret

    @gen.coroutine
    def get_asset_amount(self, asset):
        ret = {}
        if not asset:
            raise gen.Return(Decimal(0.00))
            return

        asset = asset.replace('_', '').upper()            
        r = self.client.get_asset_balance(asset=asset)
        if r and 'free' in r:
            raise gen.Return(Decimal(r['free']))
        else:
            raise gen.Return(Decimal(0.00))

    @gen.coroutine
    def create_trade(self, symbol,amount,price,side):
        if side == BUY:
            side = SIDE_BUY
        else:
            side = SIDE_SELL

        order = self.client.create_order(
            symbol = symbol,
            side = side,
            type = ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=amount,
            price=price)
        return order

    @gen.coroutine
    def create_test_trade(self):
        order = self.client.create_test_order(
            symbol='BNBBTC',
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=100,
            price='0.00001')
        return order

@gen.engine
def main():
    baex = BinanceEx.instance()
    r = yield baex.get_symbols()
    if r:
        for k in r.keys():
            price1 = yield baex.get_depth(k)
            print k, price1
    #baex.get_all_tickers()
    #r = yield baex.get_asset_amount('IOST')
    #print r
    #r = yield baex.create_test_trade()
    #print r
    IOLoop.instance().stop() 
   
if __name__ == '__main__':
    main()
    IOLoop.instance().start() 

