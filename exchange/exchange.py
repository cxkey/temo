# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class Exchange:

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def get_symbols(self):
        raise NotImplementedError('function: get_depth() must be defined')

    @abstractmethod
    def get_depth(self, symbol):
        raise NotImplementedError('function: get_depth() must be defined')
   
if __name__ == '__main__':
    pass

