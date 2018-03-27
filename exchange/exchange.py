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
            'bids': [Decimal(5.252e-05), Decimal(580.0)], 
            'asks': [Decimal(5.259e-05), Decimal(200.0)]
        }
        '''
        raise NotImplementedError('function: get_depth() must be defined')
    
    @abstractmethod
    def get_asset_amount(self, asset):
        '''
        Decimal(0.00)
        '''
        raise NotImplementedError('function: get_asset_amount() must be defined')
        

    @abstractmethod
    def get_balance(self):
        '''
        {
            'usdt': {
                'free': Decimal(100.00),
                'lock': Decimal(100.00),
            },
            'iost': {
                'free': Decimal(100.00),
                'lock': Decimal(0.00)
            },
        }
        '''
        raise NotImplementedError('function: get_balance() must be defined')

    @coroutine
    def create_trade(self, symbol, amount, price, side):
        '''
        '''
        raise NotImplementedError('function: get_balance() must be defined')

if __name__ == '__main__':
    pass

