# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from exchange import Exchange
from sdk_huobi import HuobiService
from tornado import gen
from tornado.gen import coroutine
from tornado.ioloop import IOLoop

import sys
sys.path.append('../')

from singleton import singleton
from logger import alogger, elogger

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

@gen.engine   
def main():
    hbex = HuobiEx.instance()
    r = yield hbex.get_symbols()
    if r:
        for key, value in r.iteritems(): 
            r = yield hbex.get_depth(key)   
            print key,r

if __name__ == '__main__':
    main()
    IOLoop.instance().start()

