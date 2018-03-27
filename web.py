# -*- coding: utf-8 -*-

import os, time, json, datetime, uuid, time, re
import conf
from dao import DBStatistics
from logger import alogger, elogger
from response import Response
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado import template, gen
from tornado.gen import coroutine
import util
import hashlib
import bcrypt
import concurrent.futures

class WebEntry(tornado.web.Application):
    def __init__(self):
        self.route = [
            (r"/", IndexHandler),
            (r"/api/v1/statistics", StatHandler),
        ]

        settings = dict (
                template_path = os.path.join(os.path.dirname(__file__), "templates"),
                static_path = os.path.join(os.path.dirname(__file__), "static"),
                #xsrf_cookies = True,
                cookie_secret = "123456",
                login_url = "/login",
                debug = True)

        tornado.web.Application.__init__(self, self.route, **settings)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            info = {}
            self.render('index.html', res=Response(True, '', info))
        except Exception as e:
            alogger.exception(e)
            self.write(Response(False, 'exception: %s' % str(e)).json())

class StatHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            ret = DBStatistics.instance().sum_group_by_date_asset()
            #dataset: {
            #        // 这里指定了维度名的顺序，从而可以利用默认的维度到坐标轴的映射。
            #        // 如果不指定 dimensions，也可以通过指定 series.encode 完成映射，参见后文。
            #        dimensions: ['date', 'iost', 'eth', 'usdt'],
            #        source: [
            #            {date: '20180325', 'iost': 43.3, },
            #            {date: '20180326', 'iost': 43.3, 'eth': 85.8, 'iost': 93.7},
            #            {date: '20180327', 'iost': 43.3, 'eth': 85.8, 'iost': 93.7},
            #        ]
            #    },

            #2018-03-25 12:00:00    eth    0.0009004194
            #2018-03-25 12:00:00    iost    0.0027212886
            #2018-03-25 12:00:00    usdt    0.0000000000
            #2018-03-25 14:00:00    eth    0.0009004194
            #2018-03-25 14:00:00    iost    0.0027212886
            #2018-03-25 14:00:00    usdt    0.0000000000

            dataset = {}
            dataset['dimensions'] = ['date']

            tmp = []
            for r in ret:
                d = r[0].strftime('%Y.%m.%d %H:%M:%S')
                asset, value = str(r[1]), str(r[2])
                flag = False
                for t in tmp:
                    if t['date'] == d:
                        t[asset] = value
                        flag = True
                        break
                if not flag:
                    tmp.append({'date':d, asset:value})
                if asset not in dataset['dimensions']:
                    dataset['dimensions'].append(asset)
            dataset['source'] = tmp
            
            info = { 
                'dataset': dataset
            }
            self.write(Response(True, '', info).json())
        except Exception as e:
            alogger.exception(e)
            self.write(Response(False, 'exception: %s' % str(e)).json())

