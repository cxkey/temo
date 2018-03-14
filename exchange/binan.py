# -*- coding: utf-8 -*-

from exchange import Exchange
from binance.client import Client
from tornado import gen
from tornado.ioloop import IOLoop
import time
import threading

import sys
sys.path.append('../')

from singleton import singleton
from logger import alogger, elogger

api_key = 'kUImpef08tTdWHqBUjgRzcl3DGkVAMfTCEGKFzev2qSVGx7AaJg2oXWO9WytkzMQ'
api_secret = 'N1eKTmppDwVXHvRS5jbKcvkYMZDN9xCfYxFRm2vOc1VflPmL3O3xGrSDuIa3K6Mw'

@singleton
class BinanceEx(Exchange):
    
    def __init__(self):
        Exchange.__init__(self,'binance')
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

    @gen.coroutine
    def get_depth(self, symbol):
        ret = {
            'bids': [],
            'asks': [],
        }
        if not symbol:
            return None

        symbol = symbol.replace('_', '').upper()
        r = self.client.get_order_book(symbol=symbol.upper(), limit=10)
        if r.get('bids', None) is not None:
            bids = r.get('bids', [])
            if bids:
                ret['bids'] = [ float(i) for i in bids[0][0:-1]]
            
            asks = r.get('asks', [])
            if asks:
                ret['asks'] = [ float(i) for i in asks[0][0:-1]]

            return ret
        
        return None

@gen.engine
def main():
    baex = BinanceEx.instance()
    r = yield baex.get_symbols()
    if r:
        for k in r.keys():
            print k
            price1 = baex.get_depth(k)
            print price1
    IOLoop.instance().stop() 
   
if __name__ == '__main__':
    main()
    IOLoop.instance().start() 

