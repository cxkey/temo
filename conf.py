# TODO get self ip 
import socket

HOST = '0.0.0.0'
PORT = 9998

DB_HOST = '10.8.54.165'
DB_PORT = 3306
DB_USER = 'fishing_w'
DB_PWD = 'appL3!@#_w'
DB_NAME = 'fishing'

HTTP_REQUEST_TIMEOUT = 120
HTTP_CONNECT_TIMEOUT = 60

REDIS_HOST = '10.8.54.165'
REDIS_PORT = 6379
REDIS_DB = '1'
REDIS_CACHE_PERIOD = 60 *5

TASK_WAIT_TOO_MUCH_TIME = 90

DEBUG_MODE = True
ENV = 'test'

PROJECT_NAME = 'fishing'
INSTANCE_NAME = 'server'

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3

MEINV_INDEX_DISPLAY_NUM = 36
MEINVPIC_INDEX_DISPLAY_NUM = 5
GAOXIAOVIDEO_INDEX_DISPLAY_NUM = 8

UPLOAD_DIR = '/tmp/'

RISK_RATE = 0.5
PROFIT_RATE = 0.02

INIT_AMOUNT = {
    'iost': {'amount':100,'price':0.001}
}

