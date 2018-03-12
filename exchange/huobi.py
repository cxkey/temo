# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from exchange import Exchange
from sdk_huobi import HuobiService

class HuobiEx(Exchange):
    
    def get_symbols(self):
        r = HuobiService.get_symbols()
        print r

    def get_depth(self, symbol):
        ret = {
            'bids': [],
            'asks': [],
        }
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
    hbex = HuobiEx('huobi')
    r = hbex.get_depth('iosteth')
    print r
    r = hbex.get_symbols()
    

