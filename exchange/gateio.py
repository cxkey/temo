# -*- coding: utf-8 -*- 
import sys 
sys.path.append('../') 
from singleton import singleton      
from exchange import Exchange  
from sdk_gateio.Client import *
from logger import alogger, elogger 
from tornado.gen import coroutine  
from tornado.ioloop import IOLoop  
from tornado import gen 
import decimal  
from decimal import Decimal  
import time   
from enum import *  
from redisclient import redis    
import json  
    
@singleton    
class GateioEx(Exchange):
    def __init__(self):
        Exchange.__init__(self,'gateio')


    @coroutine
    def get_symbols(self):
        r = yield gate_query.asyc_pairs()
        print r
        ret = {}
        for s in r:
            try:
                item = {
                    'base': str(s).split('_')[0],
                    'quote': str(s).split('_')[1],
                    'base_precision': '8',
                    'quote_precision': '8'
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
        try:
            r = yield gate_query.asyc_orderBook(symbol)
            bids = r.get('bids',[])
            if bids:
                ret['bids'] = [Decimal(i) for i in bids[0]] 
                asks = r.get('asks',[]) 
                if asks:
                    ret['asks'] = [Decimal(i) for i in asks[-1]] 
        except Exception,e:     
            alogger.exception(e) 
        finally:   
            raise gen.Return(ret)   

    @coroutine 
    def get_asset_amount(self,asset): 
        ret = Decimal(0.00)
        try:
            r = yield gate_trade.asyc_balances()
            asset = asset.upper()
            if asset in r['available'].keys():
                ret = Decimal(r['available'][asset])
        except Exception as e:
            alogger.exception(e)
        finally:
            raise gen.Return(ret)

    @coroutine 
    def get_assets_amount(self,asset_list): 
        ret = {}
        try:
            r = yield gate_trade.asyc_balances()
            for asset in asset_list:
                new_asset = asset.upper()
                if new_asset in r['available'].keys():
                    ret[asset] = Decimal(r['available'][new_asset])
                else:
                    ret[asset] = Decimal(0.00)  
        except Exception as e:
            alogger.exception(e)
        finally:
            raise gen.Return(ret)     

    @coroutine 
    def get_balance(self):
        ret = {}
        ZERO = Decimal(0.00)
        try:
            r = yield gate_trade.asyc_balances()
            for asset in r['available'].keys():
                amount = Decimal(r['available'][asset])
                if amount > ZERO:
                    if asset not in ret:
                        ret[asset.lower()] = { 'free': ZERO, 'lock': ZERO, } 
                    ret[asset.lower()]['free'] = amount
            for asset in r['locked'].keys():
                amount = Decimal(r['locked'][asset])
                if amount > ZERO:
                    if asset not in ret:
                        ret[asset.lower()] = { 'free': ZERO, 'lock': ZERO, } 
                    ret[asset.lower()]['locked'] = amount
        except Exception as e:    
            alogger.exception(e)  
        finally:
            raise gen.Return(ret)

    @coroutine
    def create_trade(self, symbol, amount, price, side):
        success = False
        t_id = None
        try:
            key = 'precision' + ':' + symbol + ':' + self.name
            info = redis.get(key)
            if info:
                info = json.loads(info)
                price = Decimal(price).quantize(Decimal('{0:g}'.format(float(info['price-precision']))))
                amount = Decimal(amount).quantize(Decimal('{0:g}'.format(float(info['amount-precision']))), decimal.ROUND_DOWN)

            if side == BUY:
                r = yield gate_trade.asyc_buy(symbol, price, amount)
            else:
                r = yield gate_trade.asyc_sell(symbol, price, amount)
    
            print r
            if 'result' in r and str(r['result']) in ['true','True'] :
                success = True
                t_id = r['orderNumber']
        except Exception as e:
            alogger.exception(e)
        raise gen.Return((success,t_id))            


    @coroutine
    def trade_info(self, symbol, trade_id):
        status = TRADE_INIT
        try:
            r = yield gate_trade.asyc_getOrder(trade_id, symbol)
            if 'result' in r and str(r['result']) in ['true','True']:
                res = r['order']
                if 'status' in res and res['status']:
                    status = TRADE_STATUS[self.name][str(res['status'])] 
        except Exception as e: 
            alogger.exception(e)
        raise gen.Return(status) 

    @coroutine 
    def cancel_trade(self,symbol,trade_id):  
        success = False 
        try:
            r = yield gate_trade.asyc_cancelOrder(trade_id, symbol)
            print r 
            if 'result' in r and str(r['result']) in ['true','True']:  
                success = True
        except Exception as e:    
            alogger.exception(e)  
        raise gen.Return(success)            



@gen.engine
def main():
    gateio = GateioEx.instance()
    #r = yield gateio.get_symbols()
    #r = yield gateio.get_depth('ont_eth')
    #r = yield gateio.get_asset_amount('ost')
    #r = yield gateio.create_trade('ost_usdt','0.2000', '98', SELL)
    r = yield gateio.cancel_trade('ost_usdt','523366237')
    #r = yield gateio.get_assets_amount(['ost'])
    print r

if __name__ == '__main__':
    main()
    IOLoop.instance().start() 
