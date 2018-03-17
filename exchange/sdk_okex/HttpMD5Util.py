#!/usr/bin/python
# -*- coding: utf-8 -*-
#用于进行http请求，以及MD5加密，生成签名的工具类

import json
import hashlib
import time
import urllib
import requests
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.gen import coroutine
from tornado import gen

def buildMySign(params,secretKey):
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) +'&'
    data = sign+'secret_key='+secretKey
    return  hashlib.md5(data.encode("utf8")).hexdigest().upper()

@coroutine        
def AsychttpGet(url,resource,params=''):
    headers = {
        "Content-type" : "application/x-www-form-urlencoded",
    }
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url + resource + '?' + params,headers=headers)
    data = response.body
    raise gen.Return( json.loads(data))


@coroutine
def AsychttpPost(url,resource,params):
     headers = {
            "Content-type" : "application/x-www-form-urlencoded",
     }
     http_client = AsyncHTTPClient()
     response = yield http_client.fetch(url + resource + '?' + params, method='POST', headers=headers)
     data = response.body
     raise gen.Return( data)


             
def httpGet(url,resource,params=''):
    headers = {
        "Content-type" : "application/x-www-form-urlencoded",
    }
    response = requests.get(url + resource + '?' + params,headers=headers)
    data = response.text
    return json.loads(data)

def httpPost(url,resource,params):
    headers = {
            "Content-type" : "application/x-www-form-urlencoded",
    }
    print url
    print resource
    print params
    temp_params = urllib.urlencode(params)
    response = requests.post(url + resource, data= temp_params, headers=headers)
    data = response.text
    return json.loads(data)

