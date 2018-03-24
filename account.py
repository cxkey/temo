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
import conf
from conf import INIT_AMOUNT
from spider import Spider
from main import EXCHANGES

redis = Redis.instance() 

@singleton
class Account:

    def __init__():
        self.exchanges = {}

    def statistics(self):
        # 当前平台所持有的币种, 数量, 价格, 换算成ETH, USDT, BTC 为 base 的资产
        # 初始时平台所持有的币种, 数量, 价格, 换算成ETH, USDT, BTC 为 base 的资产
        for k, v in self.exchanges.items():
            ex = v['instance']
            ex_balance = v['instance'].get_balance()
            alogger.info('name:{}, value:{}'.format(k, ex_balance))

    def start(self, exs):
        self.exchanges = exs
        tornado.ioloop.PeriodicCallback(self.statistics, 30 * 1000).start()


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

