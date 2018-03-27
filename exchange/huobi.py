# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from exchange import Exchange
from sdk_huobi import HuobiService
from tornado import gen
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
import time

import sys
sys.path.append('../')

from singleton import singleton
from logger import alogger, elogger
from decimal import Decimal
from enum import *

@singleton
class HuobiEx(Exchange):
    def __init__(self):
        Exchange.__init__(self, 'huobi')

    @coroutine
    def get_symbols(self):
        r = yield HuobiService.get_symbols()
        if 'data' not in r:
            raise gen.Return( None)

        ret = {}
        for s in r['data']:
            try:
                if str(s['quote-currency'].lower()) == 'ht' or \
                   str(s['base-currency'].lower()) == 'ht':
                   continue

                item = {
                    'base': str(s['base-currency'].lower()),
                    'quote': str(s['quote-currency'].lower()),
                    'base_precision': s['price-precision'],
                    'quote_precision': s['price-precision'],
                }
                ret['%s_%s' % (item['base'], item['quote'])] = item
            except Exception, e:
                alogger.exception(e)

        raise gen.Return( ret)

    @coroutine
    def get_depth(self, symbol):
        ret = {
            'bids': [],
            'asks': [],
        }
        if not symbol:
            raise gen.Return( None)

        symbol = symbol.replace('_', '')

        print '6666',symbol
        r = yield HuobiService.get_depth(symbol, 'step0')
        if r.get('status', None) is not None:
            tick = r.get('tick', None)
            if tick is not None:
                bids = tick.get('bids', [])
                if bids:
                    ret['bids'] = [Decimal(i) for i in bids[0]]
                
                asks = tick.get('asks', [])
                if asks:
                    ret['asks'] = [Decimal(i) for i in asks[0]]
                raise gen.Return(ret)
            else:
                raise gen.Return(None)
        
        raise gen.Return(None)

    @coroutine
    def get_asset_amount(self,asset):        
        ret = {}
        if not asset: 
            raise gen.Return(Decimal(0.00)) 
            return

        r = yield HuobiService.get_balance() 
        if r['status'] != 'ok':
            raise gen.Return(Decimal(0.00)) 
            return

        for item in r['data']['list']:
            if item['currency'] == asset:
                raise gen.Return(Decimal(item['balance']))
                return

        raise gen.Return(Decimal(0.00)) 

    @coroutine
    def get_balance(self,):
        r = yield HuobiService.get_balance()
        if not (r and 'status' in r and r['status'] == 'ok'):
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
        for b in r['data']['list']:
            asset = str(b['currency'])
            if asset not in ret:
                ret[asset] = { 'free': ZERO, 'lock': ZERO, }

            if b['type'] == 'trade' and Decimal(b['balance']) != ZERO:
                ret[asset]['free'] = Decimal(b['balance'])

            if b['type'] == 'frozen' and Decimal(b['balance']) != ZERO:
                ret[asset]['lock'] = Decimal(b['balance'])

            if ret[asset]['free'] == ZERO and ret[asset]['lock'] == ZERO:
                del ret[asset]

        raise gen.Return(ret)

    @coroutine
    def create_trade(self,symbol,amount,price,side):
        if side == BUY:
            side = 'buy-limit'
        else:
            side = 'sell-limit'
        symbol = symbol.replace('_', '')            
        price = str(Decimal(price))
        r = HuobiService.send_order(amount=amount, source=None, symbol=symbol, _type=side, price=price)
        raise gen.Return(r)


    @coroutine
    def get_history(self,symbol):
        ret = {}
        symbol = symbol.replace('_', '')
        r = yield HuobiService.get_history_trade(symbol,2000)
        if r['status'] != 'ok':
            raise gen.Return(None)

        for item in r['data']:
            t1 = time.strftime("%Y%m%d%H%M", time.localtime(item['data'][0]['ts']/1000))
            price = item['data'][0]['price']
            ret[t1] = price
        raise gen.Return(ret)


@gen.engine   
def main():
    hbex = HuobiEx.instance()
    #r = yield hbex.create_trade('iost_btc',390,Decimal('0.00000299'),BUY)
    #print r
    # test symbols
    #r = yield hbex.get_symbols()
    #for symbol in r.keys():
    #    if 'iost' in symbol:
    #        print symbol
    #        rr = yield hbex.get_depth(symbol)   
    #        print symbol, rr
    #    if 'eth_' in symbol:
    #        print symbol
    #        rr = yield hbex.get_depth(symbol)   
    #        print symbol, rr
    #for key,value in r.iteritems(): 
    #    r = yield hbex.get_depth(key)   
    #    if 'iost' in r:
    #        print key, r

    #r = yield hbex.get_asset_amount('iost')
    #print r 

    r = yield hbex.get_depth('osteth')   
    print r
    #r = yield hbex.get_balance()
    #print r

if __name__ == '__main__':
    main()
    IOLoop.instance().start()

