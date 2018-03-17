# -*- coding: utf-8 -*- 
import sys
sys.path.append('../')
from singleton import singleton
from exchange import Exchange
from sdk_okex.Client import *
from tornado.gen import coroutine
from tornado.ioloop import IOLoop 
from tornado import gen
import time

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

    @coroutine
    def get_history(self,symbol):        
        ret = {}
        r = yield okcoinSpot.trades(symbol)
        for item in r:
            t1 = time.strftime("%Y%m%d%H%M", time.localtime(item['date'])) 
            price = item['price']
            ret[t1] = price
        raise gen.Return(ret)

    @coroutine
    def get_asset_amount(self,asset):
        ret = {}
        r = okcoinSpot.userinfo()
        ret  =  r['info']['funds']['free']
        if asset in ret.keys():
            return ret[asset]
        else:
            return 0
           

@gen.engine 
def main():
    okex = OkexEx.instance()
    #r = yield okex.get_symbols()
    #for key,value in r.iteritems():
    #    #r = yield okex.get_depth(key)
    #    print key
    #    r = yield okex.get_history(key)
    #    print r
    #    break
    r = yield okex.get_asset_amount('iost')
    print r
    



if __name__ == '__main__':
    main()
    IOLoop.instance().start() 

        

