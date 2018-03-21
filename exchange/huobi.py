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

        r = yield HuobiService.get_depth(symbol, 'step0')
        if r.get('status', None) is not None:
            tick = r.get('tick', None)
            if tick is not None:
                bids = tick.get('bids', [])
                if bids:
                    ret['bids'] = bids[0]
                
                asks = tick.get('asks', [])
                if asks:
                    ret['asks'] = asks[0]

                raise gen.Return(ret)
            else:
                raise gen.Return(None)
        
        raise gen.Return(None)

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

    @coroutine
    def get_asset_amount(self,asset):        
        ret = {}
        if not asset: 
            raise gen.Return( None) 
        r = yield HuobiService.get_balance() 
        if r['status'] != 'ok':
            raise gen.Return( None)
        for item in r['data']['list']:
            if Decimal(item['balance']) > 0:
                ret[item['currency']] = item['balance']
        print ret                
        if asset in ret.keys():
            raise gen.Return( ret[asset])
        raise gen.Return( 0)

    @coroutine
    def create_trade(self,symbol,amount,price,side):
        if side == BUY:
            side = 'buy-limit'
        else:
            side = 'sell-limit'
        r = HuobiService.send_order(amount=amount, symbol=symbol, _type=side, price=price)
        return r


@gen.engine   
def main():
    hbex = HuobiEx.instance()
    #r = yield hbex.get_symbols()
    #for key,value in r.iteritems(): 
    #    #r = yield hbex.get_depth(key)   
    #    r = yield hbex.get_history(key)
    #    break
    r = yield hbex.get_asset_amount('iost')
    print r 

if __name__ == '__main__':
    main()
    IOLoop.instance().start()

