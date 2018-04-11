#encoding: utf-8
from tornado.ioloop import IOLoop   
from tornado import gen  
from decimal import Decimal  
from exchange.binan import BinanceEx
from exchange.huobi import HuobiEx
from exchange.sdk_huobi import HuobiService 
from exchange.okex import OkexEx  
import conf
from dao import *
from redisclient import *
import json

binan = BinanceEx.instance()
huobi = HuobiEx.instance()   
okex = OkexEx.instance()  

redis = Redis.instance() 

okex_precision = json.loads(open('exchange/okex_precision.py','r').read())

def dig_symbols():
    symbols = []
    bases = ['btc', 'eth', 'usdt'] 
    assets = DBStatistics.instance().select_asset()
    for asset in assets:
        if asset in bases:
            continue
        for base in bases:
            s = asset + '_' + base
            symbols.append(s)
    return symbols        

def init_precision():
    symbols = dig_symbols()
    #get binance precision
    for s in symbols:
        s_b = s.replace('_','').upper()
        res = binan.client.get_symbol_info(s_b) 
        if res and 'filters' in res:
            info = {}
            info['price-precision'] = str(res['filters'][0]['tickSize'])
            info['price-min'] = str(res['filters'][0]['minPrice'])
            info['price-max'] = str(res['filters'][0]['maxPrice'])
            info['amount-precision'] = str(res['filters'][1]['stepSize'])
            info['amount-min'] = str(res['filters'][1]['minQty'])
            info['amount-max'] = str(res['filters'][1]['maxQty'])
            info['value-min'] = str(res['filters'][2]['minNotional'])
            key = 'precision:' + s +':' +'binance'
            redis.set_no_expire(key,json.dumps(info))

    #get huobi precisoon
    r = HuobiService.get_symbols_sync()
    for item in r['data']:
        s_h = item['base-currency'] + '_' + item['quote-currency']
        if s_h not in symbols:
            continue
        info = {}
        info['price-precision'] = str( '%.10f' % Decimal(pow(0.1 , int(item['price-precision']))))
        info['price-min'] = ''
        info['price-max'] = ''
        info['amount-precision'] = str( '%.10f' % Decimal(pow(0.1 , int(item['amount-precision']))))
        info['amount-min'] = ''
        info['amount-max'] = ''
        info['value-min'] = ''
        key = 'precision:' +s_h + ':' + 'huobi'
        redis.set_no_expire(key,json.dumps(info)) 

    #get okex precision
    for s in symbols:
        if s not in okex_precision:
            continue
        r = okex_precision[s]
        info = {}
        info['price-precision'] = str(r['precision'])
        info['price-min'] = ''
        info['price-max'] = ''
        info['amount-precision'] = str(r['min_trade_size'])
        info['amount-min'] = str(r['min_trade_size'])
        info['amount-max'] = ''
        info['value-min'] = ''
        key = 'precision:' + s + ':' + 'okex'
        redis.set_no_expire(key,json.dumps(info)) 

if __name__ == '__main__':
    init_precision()

