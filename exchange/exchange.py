# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class Exchange:
    def __init__(self,ex_name):
        self.name = ex_name

    @abstractmethod
    def get_symbols(self):
        '''
        { 
            'eth_btc': {
                'base': 'eth',
                'quote': 'btc',
                'base_precision': 8,
                'quote_precision': 8,
            },
        }
        '''
        raise NotImplementedError('function: get_depth() must be defined')

    @abstractmethod
    def get_depth(self, symbol):
        '''
        {
            'bids': [5.252e-05, 580.0], 
            'asks': [5.259e-05, 200.0]
        }
        '''
        raise NotImplementedError('function: get_depth() must be defined')
  


if __name__ == '__main__':
    pass

