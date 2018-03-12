# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class Exchange:

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
        raise NotImplementedError('function: get_depth() must be defined')
   
if __name__ == '__main__':
    pass

