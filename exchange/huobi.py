# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from exchange import Exchange
from sdk_huobi import HuobiService

import sys
sys.path.append('../')

from singleton import singleton
from logger import alogger, elogger

@singleton
class HuobiEx(Exchange):
    
    def __init__(self):
        self.name = 'huobi'

    def get_symbols(self):
        r = HuobiService.get_symbols()
        if 'data' not in r:
            return None

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

        return ret

    def get_depth(self, symbol):
        ret = {
            'bids': [],
            'asks': [],
        }
        if not symbol:
            return None

        symbol = symbol.replace('_', '')

        r = HuobiService.get_depth(symbol, 'step0')
        if r.get('status', None) is not None:
            tick = r.get('tick', None)
            if tick is not None:
                bids = tick.get('bids', [])
                if bids:
                    ret['bids'] = bids[0]
                
                asks = tick.get('asks', [])
                if asks:
                    ret['asks'] = asks[0]

                return ret
            else:
                return None
        
        return None
   
if __name__ == '__main__':
    hbex = HuobiEx.instance()
    #r = hbex.get_depth('iosteth')
    #print r
    r = hbex.get_symbols()
    if r:
        for k in r.keys():
            print k
            price1 = hbex.get_depth(k)
            print price1

