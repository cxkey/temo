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


class PooledConnection(object):
    def __init__(self, pool, connection):
        self._connection  = connection
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

class ConnectionPool:
    _instance_lock = threading.Lock()

    @staticmethod
    def instance():
        if not hasattr(ConnectionPool, '_instance'):
            with ConnectionPool._instance_lock:
                if not hasattr(ConnectionPool, '_instance'):
                    ConnectionPool._instance = ConnectionPool()
        return ConnectionPool._instance


    def __init__(self, maxconnections = 5):
        from Queue import Queue
        self._queue = Queue(maxconnections) # create the queue

        for i in xrange(maxconnections):
            conn = self.getConn()
            self._queue.put(conn)
    
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


    def connection(self):
        conn = self._queue.get()
        try:        
            conn.ping()
        except Exception as e:
            alogger.exception(e)
            conn = self.getConn()
        return PooledConnection(self, conn)

    def returnConnection(self, conn):
        self._queue.put(conn)

@singleton  
class DBTrade:
    def __init__(self):
        self.tablename = 'trade'

    def insert(self, params):
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor()
            sql = "insert into %s (tid, quote, base, side, exchange, price, amount, deal_price, deal_amount, status, fee, create_time) values \
                   ('%s', '%s', '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, '%s')" % \
                   (self.tablename, params['tid'], params['quote'], params['base'], params['side'], params['exchange'], params['price'], \
                    params['amount'], params['deal_price'], params['deal_amount'], params['status'], params['fee'], params['create_time'])
            cur.execute(sql)
            conn.commit()
        except Exception, e:
            alogger.exception(e)
        finally:
            if cur:
                cur.close()
        
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
        
@singleton
class DBStatistics:
    def __init__(self):
        self.tablename = 'statistics'

    def sum_group_by_date_asset(self):
        ret = []
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor()
            sql = "select date, asset, sum(value) from `statistics` s group by date, asset "
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

    def select(self,):        
        ret = []
        conn = ConnectionPool.instance().connection()
        try:
            cur = conn.cursor()
            sql = "select id, date, exchange, asset, base, amount, price, value, create_time from statistics;"
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

