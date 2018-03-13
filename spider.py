
from house.huobi import HuobiService as huobi
from house.binance import demo as binance
from singleton import singleton
from logger import alogger, elogger
from exchange.binan import BinanceEx
from exchange.huobi import HuobiEx

@singleton
class Spider:
    def __init__(self):
        self.terminate = False
        self.exchanges = [
            BinanceEx.instance(),
            HuobiEx.instance(),
        ]

    def a(self):
        for exchange in self.exchanges:
            nihao

    def runLoop(self):
        if self.terminate:
            logger.info('spider is terminated')
            tornado.ioloop.IOLoop.instance().stop()
            #if len(self.concurrentJobs) == 0:
            #    logger.info('stop spider')
            #    tornado.ioloop.IOLoop.instance().stop()
            #else:
            #    IOLoop.instance().add_timeout(time.time() + 1, self.runLoop)
            return

            logger.info("idle")
            IOLoop.instance().add_timeout(time.time() + 1, self.runLoop)
            self.idle = False
            return

            IOLoop.instance().add_timeout(time.time() + 0.01, self.runLoop)

    def start(self):
        #tornado.ioloop.PeriodicCallback(self.aaa, 3600000).start()
        IOLoop.instance().add_timeout(time.time() + 0.01, self.runLoop)
        IOLoop.instance().start() 

if __name__ == '__main__':
    pass

