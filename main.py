# -*- coding:utf-8 -*-
import os, signal, sys, time, datetime
from tornado import ioloop
import conf
from daemon import Daemon
from conf import PROJECT_NAME, INSTANCE_NAME, MAX_WAIT_SECONDS_BEFORE_SHUTDOWN
from logger import alogger, slogger, elogger, init_logger
import signal
import sys
import os, json
from daemon import Daemon
from tornado.options import define, options
import tornado.httpserver
from spider import Spider
from druid import Druid
from account import Account
from trade import TradeSet
import time
from exchange.binan import BinanceEx
from exchange.huobi import HuobiEx
from exchange.okex import OkexEx

from tornado.options import define, options
import tornado.httpserver
from web import WebEntry
from init import *

EXCHANGES = {
    #'binance': {'instance': BinanceEx.instance(), },
    #'huobi':   {'instance': HuobiEx.instance(),   },
    #'okex':    {'instance': OkexEx.instance(),    },
}

class Application:
    def __init__(self):
        pass
        
    def start(self):
        print 'start init precision'
        init_precision()
        print 'end init precision'

        if len(EXCHANGES.keys()) > 0:
            Spider.instance().start(EXCHANGES)
            Druid.instance().start(EXCHANGES)
            Account.instance().start(EXCHANGES)
            TradeSet.instance().start()

        self.server = tornado.httpserver.HTTPServer(WebEntry())
        self.server.listen(conf.PORT)
        alogger.info('server start listening...')

        ioloop.IOLoop.instance().start()

    def stop(self):
        self.server.stop()

app = Application()

def main():
    try:
        global app
        app.start()
    except Exception as e:
        print e

class DaemonWrapper(Daemon):
    def __init__(self, instance_no):
        self.sigterm = False

        self.prefix = '/tmp/%s/instances/%s_%s' % (PROJECT_NAME, INSTANCE_NAME, instance_no)
        pidfile = self.prefix + os.sep + '%s.pid' % INSTANCE_NAME
        stderr = self.prefix + os.sep + '%s.err' % INSTANCE_NAME
        print self.prefix
        print pidfile
        print stderr

        Daemon.__init__(self, pidfile, stderr=stderr)

    def run(self):
        init_logger(self.prefix)
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        main()

    def shutdown(self, sig, frame):
        alogger.info('stopping http server')
        self.app.stop()
        io_loop = tornado.ioloop.IOLoop.instance()

        deadline = time.time() + 5

        def stop_loop():
            now = time.time()
            if now < deadline and (io_loop._callbacks):
                io_loop.add_timeout(now + 1, stop_loop)
            else:
                io_loop.stop()
                alogger.info('scheduler shutdown')
        stop_loop()

    def do(self, action):
        if action in ('stop', 'restart'):
            self.stop()

        if action in ('start', 'restart'):
            if not os.path.exists(self.prefix):
                os.makedirs(self.prefix)
            self.start()


if __name__ == '__main__':
    '''
        python main.py start 0  
    '''

    if sys.argv[1] == "debug":
        init_logger('.')
        main()
    else:
        print sys.argv
        action = sys.argv[1]
        instance_no = sys.argv[2]
        wrapper = DaemonWrapper(instance_no)
        wrapper.do(action)

