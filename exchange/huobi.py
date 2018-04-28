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
import decimal
from decimal import Decimal
from enum import *
from redisclient import redis
import json

@singleton
class HuobiEx(Exchange):
    def __init__(self):
        Exchange.__init__(self, 'huobi')

    @coroutine
    def get_symbols(self):
        r = yield HuobiService.get_symbols()

        if 'data' not in r:
            raise gen.Return(None)

        ret = {}
        for s in r['data']:
            try:
                if str(s['quote-currency'].lower()) == 'ht' or \
                   str(s['base-currency'].lower()) == 'ht':
                   continue

                #{'price-precision': 4, 'base-currency': 'elf', 'symbol-partition': 'innovation', 'quote-currency': 'usdt', 'amount-precision': 4}
                item = {
                    'base': str(s['base-currency'].lower()),
                    'quote': str(s['quote-currency'].lower()),
                     #TODO
                    'price_precision': s['price-precision'],
                    'amount_precision': s['amount-precision'],
                }
                ret['%s_%s' % (item['base'], item['quote'])] = item
            except Exception, e:
                alogger.exception(e)

        raise gen.Return(ret)

    @coroutine
    def get_depth(self, symbol):
        ret = {
            'bids': [],
            'asks': [],
        }

        try:
            symbol = symbol.replace('_', '')
            r = yield HuobiService.get_depth(symbol, 'step0')
            if r.get('status', None) is None:
                ret = None
            else:
                tick = r.get('tick', None)
                if tick is None:
                    ret = None
                else:
                    bids = tick.get('bids', [])
                    if bids:
                        ret['bids'] = [Decimal(i) for i in bids[0]]
                    
                    asks = tick.get('asks', [])
                    if asks:
                        ret['asks'] = [Decimal(i) for i in asks[0]]

                    if (not ret['asks']) and (not ret['bids']):
                        ret = None
        except Exception,e:
            alogger.exception(e)
        finally:
            raise gen.Return(ret)

    @coroutine
    def get_asset_amount(self,asset):        
        if not asset: 
            raise gen.Return(Decimal(0.00)) 
            return

        ret = Decimal(0.00)
        try:
            r = yield HuobiService.get_balance() 
            if r['status'] == 'ok':
                for item in r['data']['list']:
                    if item['currency'] == asset:
                        ret = Decimal(item['balance'])
                        break
        except Exception,e:
            alogger.exception(e) 
        finally:
            raise gen.Return(ret)

    @coroutine
    def get_assets_amount(self,asset_list):        
        ret = {}
        for asset in asset_list:
            ret[asset] = Decimal(0.00)

        try:
            r = yield HuobiService.get_balance() 
            if r['status'] == 'ok':
                for asset in asset_list:
                    for item in r['data']['list']:
                        if item['currency'] == asset:
                            ret[asset] = Decimal(item['balance'])
                            break
        except Exception,e:
            alogger.exception(e) 
        finally:
            raise gen.Return(ret)

    @coroutine
    def get_balance(self,):
        r = yield HuobiService.get_balance()
        if not (r and 'status' in r and r['status'] == 'ok'):
            raise gen.Return(None)

        ret = {}
        '''
        {
            'usdt': {
                'free': Decimal(100.00),
                'lock': Decimal(100.00),
            },
            'iost': {
                'free': Decimal(100.00),
                'lock': Decimal(0.00)
            },
        }
        '''
        ZERO = Decimal(0.00)
        for b in r['data']['list']:
            asset = str(b['currency'])
            if asset not in ret:
                ret[asset] = { 'free': ZERO, 'lock': ZERO, }

            if b['type'] == 'trade' and Decimal(b['balance']) != ZERO:
                ret[asset]['free'] = Decimal(b['balance'])

            if b['type'] == 'frozen' and Decimal(b['balance']) != ZERO:
                ret[asset]['lock'] = Decimal(b['balance'])

            if ret[asset]['free'] == ZERO and ret[asset]['lock'] == ZERO:
                del ret[asset]

        raise gen.Return(ret)

    @coroutine
    def create_trade(self,symbol,amount,price,side):
        success = False
        t_id = None
        try:
            if side == BUY:
                side = 'buy-limit'
            else:
                side = 'sell-limit'


            key = 'precision' + ':' + symbol + ':' + self.name
            info = redis.get(key)
            alogger.info('debug huobi redis get info')
            if info:
                info = json.loads(info)
                price = Decimal(price).quantize(Decimal('{0:g}'.format(float(info['price-precision']))))
                amount = Decimal(amount).quantize(Decimal('{0:g}'.format(float(info['amount-precision']))), decimal.ROUND_DOWN)
            
            symbol = symbol.replace('_', '')            
            r = HuobiService.send_order(amount=str(amount), source=None, symbol=symbol, _type=side, price=str(price))
            alogger.info('debug huobi trade result:{}'.format(str(r)))
            if 'status' in r and r['status'] == 'ok':
                success = True
                t_id = r['data']
        except Exception as e:
            alogger.exception(e)
            print str(e)
        raise gen.Return((success, t_id))

    @coroutine  
    def trade_info(self, symbol, trade_id):
        status = TRADE_INIT 
        try: 
            symbol = symbol.replace('_', '')  
            r = HuobiService.order_info(trade_id)
            if 'state' in r and r['state']:
                status = TRADE_STATUS[self.name][r['state']]
        except Exception as e: 
            alogger.exception(e)  
        raise gen.Return(status)            

    @coroutine
    def cancel_trade(self,symbol,order_id):
        success = False
        try:
            r = HuobiService.cancel_order(order_id)
            if 'status' in r and r['status'] == 'ok':
                success = True
        except Exception as e:
            alogger.exception(e)
        raise gen.Return(success)


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


@gen.engine   
def main():
    hbex = HuobiEx.instance()
    #r = yield hbex.create_trade('iost_btc',390,Decimal('0.00000299'),BUY)
    #print r
    # test symbols
    #r = yield hbex.get_symbols()
    #        rr = yield hbex.get_depth(symbol)   
    #        print symbol, rr
    #    if 'eth_' in symbol:
    #        print symbol
    #        rr = yield hbex.get_depth(symbol)   
    #        print symbol, rr
    #for key,value in r.iteritems(): 
    #    r = yield hbex.get_depth(key)   
    #    if 'iost' in r:
    #        print key, r

    t = time.time()
    r= yield hbex.get_symbols()
    # r = yield hbex.get_asset_amount('iost')
    print r
    print time.time() - t

    #r = yield hbex.get_depth('ethusdt')   
    #print r
    #r = yield hbex.get_balance()
    #print r

if __name__ == '__main__':
    main()
    IOLoop.instance().start()

