# -*- coding:utf-8 -*-
import os, signal, sys, time, datetime
from tornado import ioloop
import conf
from daemon import Daemon
from conf import PROJECT_NAME, INSTANCE_NAME, MAX_WAIT_SECONDS_BEFORE_SHUTDOWN
from logger import alogger, elogger, init_logger
import signal
import sys
import os, json
from daemon import Daemon
from tornado.options import define, options
import tornado.httpserver
from spider import Spider
from druid import Druid
import time

class Application:
    def __init__(self):
        pass
        
    def start(self):
        Spider.instance().start()
        #Druid.instance().start()
        ioloop.IOLoop.instance().start()

    def stop(self):
        pass


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
        print 1
        init_logger('.')
        print 2
        main()
        print 3
    else:
        print sys.argv
        action = sys.argv[1]
        instance_no = sys.argv[2]
        wrapper = DaemonWrapper(instance_no)
        wrapper.do(action)

