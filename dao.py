# coding: utf-8
from redisclient import Redis
from tornado import gen
from tornado.ioloop import IOLoop
import conf
import pymysql
import time
import datetime
import threading
from singleton import singleton
from logger import alogger, elogger
import tornado

# 从连接池取出的某一个连接，调用close将该连接返回到连接池
class PooledConnection(object):
    def __init__(self, pool, connection):
        self._connection = connection
        self._pool = pool

    def close(self):
        if self._connection is not None:
            self._pool.returnConnection(self._connection)
            self._connection = None

    def __getattr__(self, name):
        # All other members are the same.
        return getattr(self._connection, name)

    def __del__(self):
        self.close()

# 连接池
class ConnectionPool:
    _instance_lock = threading.Lock()

    # 返回单例对象
    @staticmethod
    def instance():
        if not hasattr(ConnectionPool, '_instance'):
            with ConnectionPool._instance_lock:
                if not hasattr(ConnectionPool, '_instance'):
                    ConnectionPool._instance = ConnectionPool()
        return ConnectionPool._instance

    # 生成连接池--获取指定的连接数放入连接池，默认值为5
    def __init__(self, maxconnections = 5):
        from Queue import Queue
        self._queue = Queue(maxconnections) # create the queue

        for i in xrange(maxconnections):
            conn = self.getConn()
            self._queue.put(conn)

    # 生成连接
    def getConn(self):
        conn = None
        while True:
            try:
                conn = pymysql.connect(**conf.DB_CONFIG)
                conn.ping()
                break
            except Exception as e:
                print e
                alogger.exception(e)
                time.sleep(1)
        return conn

    #
    def connection(self):
        conn = self._queue.get()
        try:        
            conn.ping()
        except Exception as e:
            alogger.exception(e)
            conn = self.getConn()
        return PooledConnection(self, conn)

    # 返回连接到连接池
    def returnConnection(self, conn):
        self._queue.put(conn)

# 交易表
@singleton
class DBTrade:
    def __init__(self):
        self.tablename = 'trade'

    def insert(self, params):
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor()
            sql = "insert into %s (tid, ex_tid, quote, base, side, exchange, price, amount, deal_price, deal_amount, status, fee, create_time) values \
                   ('%s', '%s', '%s', '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, '%s')" % \
                   (self.tablename, params['tid'], params['ex_tid'], params['quote'], params['base'], params['side'], params['exchange'], params['price'], \
                    params['amount'], params['deal_price'], params['deal_amount'], params['status'], params['fee'], params['create_time'])
            cur.execute(sql)
            conn.commit()
        except Exception, e:
            alogger.exception(e)
        finally:
            if cur:
                cur.close()


    def update(self,params):
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor()
            sql = "update trade set status=%s where exchange='%s' and ex_tid='%s'" % (params['status'],params['ex'],params['ex_tid'])
            cur.execute(sql)
            conn.commit()
        except Exception, e:
            alogger.exception(e)
        finally:
            if cur:
                cur.close()

# 利润表，目前是空
@singleton
class DBProfit:
    def __init__(self):
        self.tablename = 'profit'

    def insert(self, params):        
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor()
            sql = "insert into %s (tid, quote_before, base_before, value_before, quote_after, base_after, value_after, create_time) values\
                ('%s', %s, %s, %s, %s, %s, %s, '%s')" % (self.tablename, params['tid'], params['quote_before'], params['base_before'], params['value_before'], params['quote_after'], params['base_after'], params['value_after'], params['create_time'])
            cur.execute(sql)
            conn.commit()
        except Exception, e:
            alogger.exception(e)
        finally:
            if cur:
                cur.close()

# 数据统计表
@singleton
class DBStatistics:
    def __init__(self):
        self.tablename = 'statistics'

    
    def select_asset(self):
        ret = []
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor()
            sql = "select distinct asset from %s" % self.tablename
            cur.execute(sql)
            r = cur.fetchall()
            for item in r:
                ret.append(item[0])
        except Exception as e:
            alogger.exception(e)
        finally:
            cur.close()
        return ret                

    def sum_group_by_date_asset(self):
        ret = []
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor()
            now = datetime.datetime.now() - datetime.timedelta(days=3)
            sql = "select date, asset, sum(value) from `statistics` s group by date, asset having date > '%s';" % str(now)
            cur.execute(sql)
            r = cur.fetchall()
            return r
            #for i in r:
            #    ret.append({
            #        'date': i[0],
            #        'asset': i[1],
            #        'sum': i[2],
            #    })
            return ret
        except Exception, e:
            alogger.exception(e)
            return None
        finally:
            if cur:
                cur.close()

    def select_asset_by_date_exchange(self,exchange):
        ret = []
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor() 
            now = datetime.datetime.now() - datetime.timedelta(days=3) 
            sql = "select date, asset, value from `statistics` s where s.exchange='%s' and s.date > '%s';" % (exchange, str(now))
            cur.execute(sql)
            r = cur.fetchall()
            return r
        except Exception as e:
            alogger.exception(e)
            return None
        finally:
            if cur:
                cur.close()

    def select_asset_by_date_asset(self,asset):
        ret = []
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor() 
            now = datetime.datetime.now() - datetime.timedelta(days=3) 
            sql = "select date, exchange, value from `statistics` s where s.asset='%s' and s.date > '%s';" % (asset, str(now))
            cur.execute(sql)
            r = cur.fetchall()
            return r
        except Exception as e:
            alogger.exception(e)
            return None
        finally:
            if cur:
                cur.close()



    def select(self,):        
        ret = []
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor()
            now = datetime.datetime.now() - datetime.timedelta(days=3)
            sql = "select id, date, exchange, asset, base, amount, price, value, create_time from statistics where date > '%s';" % str(now)
            print sql
            cur.execute(sql)
            r = cur.fetchall()
            for i in r:
                ret.append({
                    'id': i[0],
                    'date': i[1],
                    'exchange': i[2],
                    'asset': i[3],
                    'base': i[4],
                    'amount': i[5],
                    'price': i[6],
                    'value': i[7],
                    'create_time': i[8], 
                })
            return ret
        except Exception, e:
            alogger.exception(e)
            return None
        finally:
            if cur:
                cur.close()

    def insert(self, params):        
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor()
            sql = "insert into %s (date, exchange, asset, base, amount, price, value, create_time, update_time) values \
                   ('%s', '%s', '%s', '%s', %s, %s, %s, '%s', '%s')" \
                   % (self.tablename, params['date'], params['exchange'], params['asset'], params['base'], params['amount'], params['price'], params['value'], datetime.datetime.now(), datetime.datetime.now())
            cur.execute(sql)
            conn.commit()
        except Exception, e:
            alogger.exception(e)
        finally:
            if cur:
                cur.close()
   

if __name__ == '__main__':
    conn = ConnectionPool.instance().connection()
    print conn.ping()
    #params = {}
    #params['date'] = '2018.03.25 11:00:00'
    #params['exchange'] = 'huobi'
    #params['asset'] = 'iost'
    #params['base'] = 'btc'
    #params['amount'] = 100
    #params['price'] = 0.2
    #params['value'] = 20 
    #DBStatistics.instance().insert(params)
    print DBStatistics.instance().select()

