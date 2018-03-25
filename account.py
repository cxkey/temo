#encoding:utf-8
import pymysql
from redisclient import *
import json
from dao import *
from singleton import singleton
from logger import alogger, elogger
from cache import Cache
from copy import deepcopy
from tornado.ioloop import IOLoop
from tornado import gen
import util
from util import permutation
import time
from decimal import Decimal
from exchange.binan import BinanceEx 
from exchange.huobi import HuobiEx  
from exchange.okex import OkexEx 
from Queue import Queue
from trade import *
from init import *
from dao import DBStatistics
import conf
from conf import INIT_AMOUNT

redis = Redis.instance() 

@singleton
class Account:

    def __init__(self):
        self.exchanges = {}
        self.cache = Cache.instance()

    @gen.coroutine
    def statistics(self):
        # 当前平台所持有的币种, 数量, 价格, 换算成ETH, USDT, BTC 为 base 的资产
        # 初始时平台所持有的币种, 数量, 价格, 换算成ETH, USDT, BTC 为 base 的资产
        try:
            '''
            data = {
                'huobi': {
                    'btc': {
                        'iost': [amount, bid1_price],
                        'usdt': [amount, bid1_price],
                    },
                    'eth': {
                        'iost': [amount, bid1_price],
                        'usdt': [amount, bid1_price],
                    },
                    'usdt': {
                        'iost': [amount, bid1_price],
                        'usdt': [amount, bid1_price],
                    },
                },
                'binance': {
                    ...
                },
            }
            data = {
                'huobi': {
                    'iost': {
                        'btc': [amount, bid1_price, amount*bid1_price],
                        'eth': [amount, bid1_price, amount*bid1_price],
                        'usdt': [amount, bid1_price, amount*bid1_price],
                    },
                    'eth': {
                        'btc': [amount, bid1_price, amount*bid1_price],
                        'eth': [amount, bid1_price, amount*bid1_price],
                        'usdt': [amount, bid1_price, amount*bid1_price],
                    },
                    'usdt': {
                        'btc': [amount, bid1_price, amount*bid1_price],
                        'eth': [amount, bid1_price, amount*bid1_price],
                        'usdt': [amount, bid1_price, amount*bid1_price],
                    },
                },
                'binance': {
                    ...
                },
            }
            '''
            data = {}
            bases = ['btc', 'eth', 'usdt']
            for ex_name, v in self.exchanges.items():
                if ex_name not in data:
                    data[ex_name] = {}
                    #for b in bases:
                    #    data[ex_name][b] = {}

                ex_balance = yield v['instance'].get_balance()
                if not ex_balance:
                    continue
                alogger.info('name:{}, value:{}'.format(ex_name, ex_balance))

                for asset, vb in ex_balance.items():
                    if asset not in data[ex_name]:
                        data[ex_name][asset] = {}
                        for b in bases:
                            data[ex_name][asset][b] = []
                            ret_price = self.cache.get('{}_{}'.format(asset, b), ex_name)

                            if not (ret_price and 'bids' in ret_price):
                                #if 'iost' in asset or 'eth' in asset:
                                #    alogger.info('no cache data {}_{} {}'.format(asset, b, ex_name))
                                alogger.info('no cache data {}_{} {}'.format(asset, b, ex_name))
                                if asset == 'usdt':
                                    # TODO calc the usdt price
                                    pass
                                else:
                                    continue

                            alogger.info('cache data {}_{} {}'.format(asset, b, ex_name))
                            data[ex_name][asset][b] = [vb['free'], ret_price['bids'][0], vb['free'] * ret_price['bids'][0]]
            alogger.info('data: {}'.format(data))

            BASE = 'btc'
            for ex, v1 in data.items():
                for asset, v2 in v1.items():
                    p = {
                        'date': util.get_time_hour_align(),
                        'exchange': ex,
                        'asset': asset,
                        'base': BASE,
                        'amount': v2['btc'][0],
                        'price': v2['btc'][1],
                        'value': v2['btc'][2],
                    }
                    DBStatistics.instance().insert(p)
        except Exception, e:
            alogger.exception(e)

    def start(self, exs):
        self.exchanges = exs
        tornado.ioloop.PeriodicCallback(self.statistics, 10 * 1000).start()

# 计算单笔交易的收益
def cal_single_profit(params):
    redis_key = params['quote'] + '_' + params['base'] + '_' + params['exchange']
    value = redis.get(redis_key)
    if value == None:
        # 表示是该 symbol 第一次交易，取初始量
        # 实际上线, 应该是从交易所获取
        value = INIT_AMOUNT[params['quote']]
    else:        
        value = json.loads(value)

    # 单次盈利 = 上一次交易结束后小币总量 * 此次交易与上次交易的价差
    value_profit = value['amount'] * (params['deal_price'] - value['price'])        
    # 单次主币变化 = 交易量 * 此次交易与上次交易的价差
    base_profit = params['amount'] * (params['deal_price'] - value['price'])
    # TODO: 写db
    params = {}
    DBProfit.instance().insert(params)

    value['price'] = str(params['deal_price'])
    if params['side'] == BUY:
        value['amount'] = value['amount'] + params['amount']
    else:
        value['amount'] = value['amount'] - params['amount']
    # 存下当前交易的值，供下一次使用        
    redis.set(redis_key, json.dumps(value))  

def cal_all_profit():
    pass

