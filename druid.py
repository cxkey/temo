
from house.huobi import HuobiService as huobi
from house.binance import demo as binance
from singleton import singleton
from logger import alogger, elogger

@singleton
class Druid:
    def __init__(self):
        self.terminate = False
        self.handlers = []

    def start(self):
        tornado.ioloop.PeriodicCallback(self.aaa, 3600000).start()
        IOLoop.instance().add_timeout(time.time() + 0.01, self.runLoop)
        IOLoop.instance().start() 

    def aaa(self):
        alogger.loginfo('1')

if __name__ == '__main__':
    pass

