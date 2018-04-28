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
import decimal
from decimal import Decimal, ROUND_DOWN
from enum import *
from redisclient import redis
import json

api_key = S.KEYS['binance']['access_key']
api_secret = S.KEYS['binance']['secret_key']

@singleton
class BinanceEx(Exchange):
    
    def __init__(self):
        Exchange.__init__(self, 'binance')
        self.client = Client(api_key, api_secret)
    
    def a(self):
        amount = Decimal(98.3432434324324432432)
        print amount
        amount = Decimal(amount).quantize(Decimal('0.00000100'))
        print amount
        amount = Decimal(amount).quantize(Decimal('1.00000000'), rounding=ROUND_DOWN)
        print amount
        amount = (Decimal(amount) / Decimal('1.00000000')).quantize(Decimal('1'), rounding=ROUND_DOWN)
        print amount
        return self.client.get_symbol_info('CHATETH')

    def ping(self):
        return self.client.ping()
        
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
        try:
            r = self.client.get_order_book(symbol=symbol, limit=10)
            IOLoop.instance().add_callback(callback, r)
        except Exception, e:
            if 'Invalid symbol' in str(e):
                pass
            else:
                alogger.exception(e)
            IOLoop.instance().add_callback(callback, None)

    def _get_depth(self, symbol, callback):
        threading.Thread(target=self._do_get_depth, args=(symbol, callback)).start()

    @gen.coroutine
    def get_depth(self, symbol):
        ret = {
            'bids': [],
            'asks': [],
        }

        try:
            symbol = symbol.replace('_', '').upper()
            r = yield gen.Task(self._get_depth, symbol)
            if r is None:
                ret = None
            else:
                bids = r.get('bids', [])
                if bids:
                    ret['bids'] = [Decimal(i) for i in bids[0][0:-1]]
                
                asks = r.get('asks', [])
                if asks:
                    ret['asks'] = [Decimal(i) for i in asks[0][0:-1]]

                if (not ret['asks']) and (not ret['bids']):
                    ret = None
        except Exception,e:
            alogger.exception(e)
        finally:
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
    def get_assets_amount(self, asset_list):
        ret = {}
        try:
            for asset in asset_list:
                binan_asset = asset.replace('_', '').upper()            
                r = self.client.get_asset_balance(asset=binan_asset)
                if r and 'free' in r:
                    ret[asset] = Decimal(r['free'])
                else:
                    ret[asset] = Decimal(0.00)
        except Exception,e:
            alogger.exception(e) 
        finally:
            raise gen.Return(ret)

    @gen.coroutine
    def get_balance(self,):
        r = self.client.get_account()
        if not (r and 'balances' in r ):
            raise gen.Return(None)

        ret = {}
        '''
        {
            'usdt': {
                'free': Decimal(100.00),
                'lock': Decimal(100.00),
            },
            'iost': {
                'free': Decimal(100.00),
                'lock': Decimal(0.00)
            },
        }
        '''
        ZERO = Decimal(0.00)
        for b in r['balances']:
            if Decimal(b['free']) == ZERO and Decimal(b['locked']) == ZERO:
                continue
            else:
                asset = str(b['asset'].lower())
                if asset not in ret:
                    ret[asset] = {'free': Decimal(b['free']), 'lock': Decimal(b['locked'])}

        raise gen.Return(ret)

    @gen.coroutine
    def create_trade(self, symbol,amount,price,side):
        success = False
        t_id = None
        try:
            if side == BUY:
                side = SIDE_BUY
            else:
                side = SIDE_SELL

            key = 'precision' + ':' + symbol + ':' + self.name
            info = redis.get(key)
            if info:
                info = json.loads(info)
                price = Decimal(price).quantize(Decimal('{0:g}'.format(float(info['price-precision']))))
                amount = Decimal(amount).quantize(Decimal('{0:g}'.format(float(info['amount-precision']))), decimal.ROUND_DOWN)
           
            symbol = symbol.replace('_','').upper()
            order = self.client.create_order(
                symbol = symbol,
                side = str(side),
                type = str(ORDER_TYPE_LIMIT),
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=amount,
                price=str(price)
                )
            # {u'orderId': 6916333, u'clientOrderId': u'XOmgWMHBImw1aKfCvUeKGd', u'origQty': u'400.00000000', u'symbol': u'IOSTBTC', u'side': u'BUY', u'timeInForce': u'GTC', u'status': u'NEW', u'transactTime': 1522120616990, u'type': u'LIMIT', u'price': u'0.00000298', u'executedQty': u'0.00000000'}
            if 'status' in order and 'orderId' in order:
                success = True
                t_id = order['orderId']
        except Exception as e:       
            alogger.exception(e)
        raise gen.Return((success,t_id))

    @gen.coroutine
    def cancel_trade(self, symbol, trade_id):
        success = False
        try:
            symbol = symbol.replace('_','').upper()
            result = self.client.cancel_order(symbol=symbol, orderId=trade_id)
            success = True
        except Exception as e:
            alogger.exception(e)
        raise gen.Return( success)

    @gen.coroutine
    def trade_info(self, symbol, trade_id):
        status = TRADE_INIT
        try:
            symbol = symbol.replace('_','').upper()
            result = self.client.get_order(symbol=symbol, orderId=trade_id)
            print result
            if 'status' in result and result['status']:
                status = TRADE_STATUS[self.name][result['status']]
        except Exception as e:
            alogger.exception(e)
        raise gen.Return(status)            

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
    t1 = time.time()
    baex.ping()
    # baex = BinanceEx.instance()
    s = yield baex.get_symbols()
    symbol = s.keys()[0]
    asset='BTC'
    # print s
    # r = yield baex.get_depth(s.keys()[0])
    # r =  baex.get_all_tickers()
    r = yield baex.get_history(symbol)
    print 'get_history',r

    r = yield baex.get_asset_amount(asset)
    print 'get_asset_amount',r
    r = yield baex.get_assets_amount( ['BTC','ETH'])
    print 'get_assets_amount',r
    r = yield baex.get_balance( )
    print 'get_balance',r
    # print time.time() - t1
    #r = yield baex.trade_info('CHATBTC','2726795')
    #print r
    #r = baex.a()
    #print r
    #r = yield baex.get_symbols()
    #if r:
    #    for k in r.keys():
    #        price1 = yield baex.get_depth(k)
    #        if 'iost' in k:
    #            print k, price1
    #        break
    #price1 = yield baex.get_depth('iost_btc')
    #print price1
    
    #baex.get_all_tickers()
    #r = yield baex.get_asset_amount('IOST')
    #print r

    #r = yield baex.create_test_trade()
    #print r

    #r = yield baex.create_trade('iost_btc',400,Decimal('0.001'),BUY)
    #print r
    #r = yield baex.get_balance()
    #print r
    #IOLoop.instance().stop() 
    print 'end'
   
if __name__ == '__main__':
    main()
    IOLoop.instance().start()


