# TODO get self ip 
import socket
import os

HOST = '0.0.0.0'
PORT = 9998

DB_CONFIG = {
    'host': '10.8.54.165',
#    'host': '128.1.131.178',
    'port': 3306,
    'user': 'fishing_w',
    'passwd': 'appL3!@#_w',
    'db': 'fishing',
    'charset': 'utf8',
    'autocommit': True
}

HTTP_REQUEST_TIMEOUT = 120
HTTP_CONNECT_TIMEOUT = 60

REDIS_HOST = '10.8.54.165'
REDIS_PORT = 6379
REDIS_DB = '1'
REDIS_CACHE_PERIOD = 60 * 5

TASK_WAIT_TOO_MUCH_TIME = 90

DEBUG_MODE = False
if os.getcwd() == '/opt/production/fishing':
    ENV = 'pro'
else:
    ENV = 'test'

PROJECT_NAME = 'fishing'
INSTANCE_NAME = 'server'

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3

MEINV_INDEX_DISPLAY_NUM = 36
MEINVPIC_INDEX_DISPLAY_NUM = 5
GAOXIAOVIDEO_INDEX_DISPLAY_NUM = 8

UPLOAD_DIR = '/tmp/'

RISK_RATE = 10
PROFIT_RATE = 0.0003

#from exchange.binan import BinanceEx
#from exchange.huobi import HuobiEx
#from exchange.okex import OkexEx
#EXCHANGES = {
#    'binance': {'instance': BinanceEx.instance(), 'enabled': True},
#    'huobi': {'instance': HuobiEx.instance(), 'enabled': True},
#}

INIT_AMOUNT = {
    'usdt' : { 'binance':{'amount': 0},          'huobi':{'amount': 155.52099500}, 'okex':{'amount': 0} },
    'btc'  : { 'binance':{'amount': 0.02167182}, 'huobi':{'amount': 0.02843271},   'okex':{'amount': 0.02420212} },
    'eth'  : { 'binance':{'amount': 0.02497500}, 'huobi':{'amount': 0.45345454},   'okex':{'amount': 0.02688146} },
    'chat' : { 'binance':{'amount': 198},        'huobi':{'amount': 198},          'okex':{'amount': 198} },
    'ost'  : { 'binance':{'amount': 100},        'huobi':{'amount': 100},          'okex':{'amount': 100} },
    'iost' : { 'binance':{'amount': 399.6},      'huobi':{'amount': 487},          'okex':{'amount': 0} },
}

# base is USDT
INIT_COST = {
    'btc' : { 'amount': 100, 'price': 8870.82 },
    'eth' : { 'amount': 100, 'price': 538.92  },
    'omg' : { 'amount': 100, 'price': 11.47 },
}

