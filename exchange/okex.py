# -*- coding: utf-8 -*- 
import sys
sys.path.append('../')
from singleton import singleton
from exchange import Exchange
from sdk_okex.Client import *
from tornado.gen import coroutine
from tornado.ioloop import IOLoop 
from tornado import gen

@singleton
class OkexEx(Exchange):
    def __init__(self):
        Exchange.__init__(self,'okex')

    @coroutine
    def get_symbols(self):        
        r = yield okcoinSpot.tickers()
        if 'data' not in r:
            raise gen.Return( None)

        ret = {}            
        for s in r['data']:
            try:
                item = {
                    'base': str(s['symbol']).split('_')[0],
                    'quote': str(s['symbol']).split('_')[1],
                    'base_precision': '5',
                    'quote_precision': '5'
                }
                ret['%s_%s' % (item['base'], item['quote'])] = item 
            except Exception, e:
                alogger.exception(e)
        raise gen.Return(ret)                

    @coroutine
    def get_depth(self, symbol):
        ret = {
            'bids':[],
            'asks':[],
        }
        if not symbol:
            raise gen.Return(None)

        r = yield okcoinSpot.depth(symbol)
        bids = r.get('bids',[])
        if bids:
            ret['bids'] = bids[0]
            asks = r.get('asks',[])
            if asks:
                ret['asks'] = asks[-1]
            raise gen.Return(ret)
        raise gen.Return(None)

@gen.engine 
def main():
    okex = OkexEx.instance()
    r = yield okex.get_symbols()
    for key,value in r.iteritems():
        r = yield okex.get_depth(key)
        print key,r


if __name__ == '__main__':
    main()
    IOLoop.instance().start() 

        

