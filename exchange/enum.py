BUY=0
SELL=1
TRADE_INIT = 0
TRADE_PARTIALLY_SUCCESS = 1
TRADE_FILLED_SUCCESS=2
TRADE_FAIL=-1
TRADE_CANCELED=-2
TRADE_STATUS = {
    'binance':{'NEW':TRADE_INIT,
               'PARTIALLY_FILLED':TRADE_PARTIALLY_SUCCESS,
               'FILLED':TRADE_FILLED_SUCCESS,
               'CANCELED':TRADE_CANCELED,
               'PENDING_CANCEL':TRADE_INIT,
               'REJECTED':TRADE_FAIL,
               'EXPIRED':TRADE_FAIL
               },
    'huobi':{'pre-submitted':TRADE_INIT,
             'submitting':TRADE_INIT,
             'submitted':TRADE_INIT,
             'partial-filled':TRADE_PARTIALLY_SUCCESS,
             'partial-canceled':TRADE_PARTIALLY_SUCCESS,
             'filled':TRADE_FILLED_SUCCESS,
             'canceled':TRADE_CANCELED
            },
    'okex':{'-1':TRADE_CANCELED,
            '0':TRADE_FAIL,
            '1':TRADE_PARTIALLY_SUCCESS,
            '2':TRADE_FILLED_SUCCESS,
            '4':TRADE_INIT
    }
}
