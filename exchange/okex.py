# -*- coding: utf-8 -*- 
import sys
sys.path.append('../')
from singleton import singleton
from exchange import Exchange
from sdk_okex.Client import *
from logger import alogger, elogger
from tornado.gen import coroutine
from tornado.ioloop import IOLoop 
from tornado import gen
from decimal import Decimal
import time
from enum import *
from redisclient import redis
import json

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
            ret['bids'] = [Decimal(i) for i in bids[0]]
            asks = r.get('asks',[])
            if asks:
                ret['asks'] = [Decimal(i) for i in asks[-1]]
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
        ret = Decimal(0.00)
        try:
            r = okcoinSpot.userinfo()
            if asset in r['info']['funds']['free'].keys():
                ret = Decimal(r['info']['funds']['free'][asset])
        except Exception,e:
            alogger.exception(e) 
        finally:
            raise gen.Return(ret)

    @coroutine
    def get_balance(self,):
        ret = {}
        ZERO = Decimal(0.00)
        try:
            r = okcoinSpot.userinfo()
            for item in r['info']['funds']['free'].keys():
                amount = Decimal(r['info']['funds']['free'][item])
                if amount > ZERO:
                    if item not in ret:
                        ret[item] = { 'free': ZERO, 'lock': ZERO, }
                    ret[item]['free'] = amount
            for item in r['info']['funds']['freezed'].keys():
                amount = Decimal(r['info']['funds']['freezed'][item])
                if amount > ZERO:
                    if item not in ret:
                        ret[item] = { 'free': ZERO, 'lock': ZERO, }
                    ret[item]['lock'] = amount
        except Exception as e:
            alogger.exception(e) 
        finally:
            raise gen.Return(ret)
    
    @coroutine        
    def create_trade(self,symbol,amount,price,side):
        success = False
        t_id = None
        try:
            if side == BUY:
                side = 'buy'
            else:
                side = 'sell'
            
            key = 'precision' + ':' + symbol + ':' + self.name
            info = redis.get(key)
            if info:
                info = json.loads(info)
                #price = Decimal(price).quantize(Decimal('{0:g}'.format(float(info['price-precision']))))
                price = Decimal(price).quantize(Decimal('{0:g}'.format(float('0.00000001'))))
                amount = Decimal(amount).quantize(Decimal('{0:g}'.format(float(info['amount-precision']))))
           
            r = okcoinSpot.trade(symbol=symbol,tradeType=side,price=float(price),amount=float(amount))
            alogger.info('debug okex trade price:{} amount:{} result:{}'.format(str(price), str(amount), str(r)))
            if 'result' in r and str(r['result']) in  ('True','true'):
                success = True
                t_id = r['order_id']
        except Exception as e:
            alogger.exception(e) 
        raise gen.Return((success,t_id))
    
    @coroutine  
    def trade_info(self, symbol, trade_id):
        status = TRADE_INIT 
        try: 
            r = okcoinSpot.orderinfo(symbol,trade_id)
            if 'result' in r and str(r['result']) in ('true','True'):
                res = r['orders'][0]
                if 'status' in res and res['status']:
                    status = TRADE_STATUS[self.name][str(res['status'])]
        except Exception as e: 
            alogger.exception(e)  
        raise gen.Return(status)            

    @coroutine 
    def cancel_trade(self,symbol,trade_id):
        success = False
        try:            
            r = okcoinSpot.cancelOrder(symbol,trade_id)
            if 'result' in r and str(r['result']) in  ('True','true'):
                success = True
        except Exception as e:
            alogger.exception(e)
        raise gen.Return(success)

@gen.engine 
def main():
    okex = OkexEx.instance()
    r = yield okex.get_balance()
    print r
    #r = yield okex.get_symbols()
    #r = yield okex.trade_info('ost_btc','5234048')
    #print r
    #for key,value in r.iteritems():
    #    r = yield okex.get_depth(key)
        #print key
        #r = yield okex.get_history(key)
        #print r
        #break
    #r = yield okex.get_asset_amount('chat')
    #print r
    #r = yield okex.create_trade('chat_btc',Decimal(1),Decimal('0.00001100'),BUY)
    #print r

if __name__ == '__main__':
    main()
    IOLoop.instance().start() 

