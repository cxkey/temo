# -*- coding:utf-8 -*- 
import json
from decimal import Decimal

class Response:
    
    def __init__(self, result=True, message='', info={}):
        self.result = result
        self.message = message
        self.info = info
    
    def dict(self):
        d = {}

        for k in self.__dict__:
            if k.startswith('_'):
                continue
            if isinstance(self.__dict__[k], \
                (bool, int, float, str, list, tuple, set, dict, unicode)):
                d[k] = self.__dict__[k]
            else:
                d[k] = str(self.__dict__[k])

        return d
    
    def json(self):
        return json.dumps(self.dict(), ensure_ascii=False)

if __name__ == '__main__':
    #info = {u'你好': u'邮件11111'}
    info = {
        #u'你好': u'邮件',
        u'你好': '邮件',
        #'你好': ['你坏', '就佛娥姐']
    }
    print json.dumps(info, ensure_ascii=False)
    # print json.dumps(Response(True, '', info).dict())
    #print Response(True, '你好').json()
    print '---------------------------------'
    print Response(True, '', info).json()
        
