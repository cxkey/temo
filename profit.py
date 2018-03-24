#encoding:utf-8
import pymysql
from redisclient import *
from conf import INIT_AMOUNT
import json
from dao import *


redis = Redis.instance() 

#计算单笔交易的收益
def cal_single_profit(params):
    redis_key = params['quote'] + '_' + params['base'] + '_' + params['exchange']
    value = redis.get(redis_key)
    if value == None:
        #表示是该symbol第一次交易，取初始量和初始价格
        value = INIT_AMOUNT[params['quote']]
    else:        
        value = json.loads(value)

    #单次盈利 = 上一次交易结束后小币总量 * 此次交易与上次交易的价差
    value_profit = value['amount'] * (params['deal_price'] - value['price'])        
    #单次主币变化 = 交易量 * 此次交易与上次交易的价差
    base_profit = params['amount'] * (params['deal_price'] - value['price'])
    #TODO: 写db
    params = {}
    DBProfit.instance().insert(params)

    value['price'] = str(params['deal_price'])
    if params['side'] == BUY:
        value['amount'] = value['amount'] + params['amount']
    else:
        value['amount'] = value['amount'] - params['amount']
    #存下当前交易的值，供下一次使用        
    redis.set(redis_key, json.dumps(value))  

def cal_all_profit():
    pass

