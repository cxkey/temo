# -*- coding: utf-8 -*- 
from singleton import singleton
from exchange import Exchange
from sdk_okex.Client import *

@singleton
class OkexEx(Exchange):
    def __init__(self):
        Exchange.__init__(self,'okex')

    def get_symbols(self):        
        r = okcoinSpot.tickers()
        if 'data' not in r:
            return None

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
        return ret                

    def get_depth(self, symbol):
        ret = {
            'bids':[],
            'asks':[],
        }
        if not symbol:
            return None

        r = okcoinSpot.depth(symbol)
        bids = r.get('bids',[])
        if bids:
            ret['bids'] = bids[0][0]
            asks = r.get('asks',[])
            if asks:
                ret['asks'] = asks[-1][0]
            return ret
        return None                



if __name__ == '__main__':
    okex = OkexEx.instance()
    r = okex.get_symbols()
    for key,value in r.iteritems():
        r = okex.get_depth(key)
        print key,r
       

        

