# -*- coding: utf-8 -*-

from exchange import Exchange
from binance.client import Client

api_key = 'kUImpef08tTdWHqBUjgRzcl3DGkVAMfTCEGKFzev2qSVGx7AaJg2oXWO9WytkzMQ'
api_secret = 'N1eKTmppDwVXHvRS5jbKcvkYMZDN9xCfYxFRm2vOc1VflPmL3O3xGrSDuIa3K6Mw'

class BinanceEx(Exchange):
    
    def __init__(self, name):
        Exchange.__init__(self, name)
        self.client = Client(api_key, api_secret)

    def get_symbols(self):
        r = self.client.get_exchange_info()
        if 'symbols' not in r:
            return None

        ret = {}
        for s in r['symbols']:
            try:
                item = {
                    'base': str(s['baseAsset'].lower()),
                    'quote': str(s['quoteAsset'].lower()),
                    'base_precision': s['baseAssetPrecision'],
                    'quote_precision': s['quotePrecision'],
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
        print symbol
        r = self.client.get_order_book(symbol=symbol.upper(), limit=3)
        if r.get('bids', None) is not None:
            bids = r.get('bids', [])
            if bids:
                ret['bids'] = [ float(i) for i in bids[0][0:-1]]
            
            asks = r.get('asks', [])
            if asks:
                ret['asks'] = [ float(i) for i in asks[0][0:-1]]

            return ret
        
        return None
   
if __name__ == '__main__':
    baex = BinanceEx('binance')
    r = baex.get_symbols()
    if r:
        for k in r.keys():
            print k
            price1 = baex.get_depth(k)
            print price1

