import  util 
from tornado.ioloop import IOLoop  
from tornado import gen
from tornado.gen import coroutine
import time
from decimal import Decimal
from exchange.binan import BinanceEx  
from exchange.huobi import HuobiEx  
from exchange.okex import OkexEx    
import conf

binan = BinanceEx.instance()
huobi = HuobiEx.instance()
okex = OkexEx.instance()

@coroutine
def get_symbols():
    s1 = yield binan.get_symbols()
    s2 = yield huobi.get_symbols()
    s3 = yield okex.get_symbols()
    s11 = set(s1.keys())
    s12 = set(s2.keys())
    s13 = set(s3.keys())
    r = s11 & s12 & s13
    raise gen.Return(r)

@coroutine
def get_depth(symbols):
    cache = {}
    for symbol in symbols:
        try:
            d1 = yield binan.get_depth(symbol)
            d2 = yield huobi.get_depth(symbol)
            d3 = yield okex.get_depth(symbol)
            item = {}
            item['binan'] = d1
            item['huobi'] = d2
            item['okex'] = d3
            if symbol in cache.keys():
                cache[symbol] = item
            else:
                cache[symbol] = {}
                cache[symbol] = item
        except Exception as e:
            print e 
    raise gen.Return(cache)
    

def scan(cache):
    try:
        print 'scan start'
        fd = open('diff.txt','a+')
        for symbol, value in cache.iteritems():
            exs = cache[symbol].keys()
            perm_list = util.permutation(exs)
            for item in perm_list:
                try:
                    ex1 = item[0]
                    ex2 = item[1]
                    price1 = cache[symbol][ex1]
                    price2 = cache[symbol][ex2] 
                    bid1, bid1_amount = Decimal(price1['bids'][0]), Decimal(price1['bids'][1])
                    ask1, ask1_amount = Decimal(price1['asks'][0]), Decimal(price1['asks'][1]) 
                    bid2, bid2_amount = Decimal(price2['bids'][0]), Decimal(price2['bids'][1])
                    ask2, ask2_amount = Decimal(price2['asks'][0]), Decimal(price2['asks'][1])
                
                    
                    key = symbol + '_' + ex1 + '_' + ex2
                    time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) 
                    profit1 = float(util.profit_rate(ask1, bid2))
                    profit2 = float(util.profit_rate(ask2, bid1))
                    fd.write(key)
                    fd.write('\t')
                    fd.write(time_str)
                    fd.write('\t')
                    fd.write(str(profit1))
                    fd.write('\t')
                    fd.write(str(profit2))
                    print key,time_str,price1,price2,profit1,profit2

                    if ask1 < bid2 and profit1 > conf.PROFIT_RATE:  
                        fd.write('\t')
                        fd.write('positive_ok')
                    elif ask2 < bid1 and profit2 > conf.PROFIT_RATE:
                        fd.write('\t')
                        fd.write('negtive_ok')
                    fd.write('\n')
                except Exception as e:
                    print e                        
        fd.close()                    
    except Exception as e:
        print e


@coroutine
def main():
    while True:
        try:
            symbols = yield get_symbols()
            print symbols
            #cache = yield get_depth(symbols)
            #scan(cache)
        except Exception as e:
            print e
        time.sleep(10)            
    IOLoop.instance().stop()

if __name__ == '__main__':
    main()
    IOLoop.instance().start()
    
