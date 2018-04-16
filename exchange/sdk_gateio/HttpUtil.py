#!/usr/bin/python
# -*- coding: utf-8 -*-

#import http.client
import urllib
import json
import hashlib
import hmac
import requests
from tornado.gen import coroutine   
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError

import sys 
sys.path.append('../')  
sys.path.append('../../')  


# timeout in 5 seconds: 
TIMEOUT = 5 

def getSign(params, secretKey):
    #bSecretKey = bytes(secretKey, encoding='utf8')
    bSecretKey = bytes(secretKey)

    sign = ''
    for key in params.keys():
        value = str(params[key])
        sign += key + '=' + value + '&'
    #bSign = bytes(sign[:-1], encoding='utf8')
    bSign = bytes(sign[:-1])

    mySign = hmac.new(bSecretKey, bSign, hashlib.sha512).hexdigest()
    return mySign

def httpGet(url, resource, params=''):
    try:
        response = requests.get('http://' + url + resource + '/' +params, timeout=TIMEOUT)
        if response.status_code == 200: 
            return response.json()
        else:
            return {"status":"fail"}   
    except Exception as e: 
        print("httpGet failed, detail is:%s" %e) 
        return {"status":"fail","msg":e}  

@coroutine  
def asyc_httpGet(url, resource, params=''):
    res = {"status":"fail","msg":''}
    try:
        http_client = AsyncHTTPClient() 
        response = yield http_client.fetch('http://' + url + resource + '/' +params, request_timeout=TIMEOUT)
        res = json.loads(response.body) 
    except Exception as e:
        print e
        raise gen.Return({"status":"fail","msg":e})  
    raise gen.Return(res)         


        

def httpPost(url, resource, params, apiKey, secretKey):
    headers = {
            "Content-type" : "application/x-www-form-urlencoded",
            "KEY":apiKey,
            "SIGN":getSign(params, secretKey)
    }
    tempParams = urllib.urlencode(params) if params else ''

    try:
        response = requests.post('http://' + url + resource, data=tempParams, headers=headers, timeout=TIMEOUT)
        if response.status_code == 200: 
            return response.json()
        else:
            return {"status":"fail"}   
    except Exception as e: 
        print("httpGet failed, detail is:%s" %e) 
        return {"status":"fail","msg":e}  
     


@coroutine  
def asyc_httpPost(url, resource, params, apiKey, secretKey):
    res = {"status":"fail","msg":''}
    try:
        headers = {
                "Content-type" : "application/x-www-form-urlencoded",
                "KEY":apiKey,
                "SIGN":getSign(params, secretKey)
        }
        tempParams = urllib.urlencode(params) if params else ''
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch('http://' + url + resource, body=tempParams, headers=headers, method='POST', request_timeout=TIMEOUT)
        res =  json.loads( response.body)
    except Exception as e: 
        print("httpGet failed, detail is:%s" %e) 
        raise gen.Return( {"status":"fail","msg":e}  )
    raise gen.Return(res)     
