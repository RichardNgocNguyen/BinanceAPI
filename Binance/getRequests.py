from datetime import datetime, timedelta
import json
from Binance.manageRequests import BINANCE_API

class GET(BINANCE_API):
    def __init__(self):
        # Parent Inherited Variables
        super().__init__()
        # GET Endpoints
        self.base = 'https://api.binance.us'
        self.exchange = '/api/v3/exchangeInfo'
        self.klines = '/api/v3/klines'
        self.ticker = '/api/v3/ticker/price'
        self.active = '/api/v3/openOrders'
        self.account = '/api/v3/account'
        # Time Data
        self.timestamp = {}
        self.date = {}
        # Series Data
        self.open = {}
        self.high = {}
        self.low = {}
        self.close = {}
        self.volume = {}
    
    def getSymbolTick(self, symbol):
        query = self.base + self.ticker
        url = query + '?' + f"symbol={symbol}"
        info = self.session.get(url)
        self.updateWeights(request=info)
        return info.json()

    def getAccount(self, window=10000):
        query = self.base + self.account
        ms_time = self.getTimestamp()
        parameters = f'recvWindow={window}&timestamp={ms_time}'
        signature = self.hashing(parameters)
        url = query + '?' + parameters + f'&signature={signature}'
        header = {'X-MBX-APIKEY': self.api_k}
        post = self.session.get(url, headers=header, timeout=30, verify=True)
        self.updateWeights(request=post)
        return post.json()
    
    def getBalance(self, currency):
        wallet = self.getAccount()['balances']
        for i in range(len(wallet)):
            if wallet[i]['asset'] == currency:
                balance = float(wallet[i]['free'])
                return balance
            
    def getExchangeInfo(self, symbol):
        if symbol in self.information:
            return self.information[symbol]
        else:
            query = self.base + self.exchange
            url = query + "?" + f"symbol={symbol}"
            info = self.session.get(url)
            
            self.information[symbol] = info.json()["symbols"][0]

            with open('Binance\info.txt', 'a') as file:
                json.dump(info.json()["symbols"][0], file)
                file.write('\n')

            self.updateWeights(request=info)
            return info.json()["symbols"][0]
            
    def getBaseAsset(self, symbol):
        base_asset = self.getExchangeInfo(symbol)['baseAsset']
        value = self.getBalance(base_asset)
        return {'Asset': base_asset, 'Balance': value}
    
    def getQuoteAsset(self, symbol):
        quote_asset = self.getExchangeInfo(symbol)['quoteAsset']
        value = self.getBalance(quote_asset)
        return {'Asset': quote_asset, 'Balance': value}
    
    def getOpenOrders(self, window=10000):
        query = self.base + self.active
        ms_time = self.getTimestamp()
        parameters = f'recvWindow={window}&timestamp={ms_time}'
        signature = self.hashing(parameters)
        url = query + '?' + parameters + f'&signature={signature}'
        header = {'X-MBX-APIKEY': self.api_k}
        info = self.session.get(url, headers=header, timeout=30, verify=True)
        self.updateWeights(request=info)
        return info.json()
    
    def getKlines(self, symbol, interval, start_time=None):
        kline = self.base + self.klines
        if start_time is None:
            parameters = f'?symbol={symbol}&interval={interval}&limit=1000'
        else:
            parameters = f'?symbol={symbol}&interval={interval}&startTime={start_time}&limit=1000'
        url = kline + parameters
        req = self.session.get(url)
        j_stream = req.json()

        self.open[interval] = []
        self.high[interval] = []
        self.low[interval] = []
        self.close[interval] = []
        self.volume[interval] = []
        self.timestamp[interval] = []
        self.date[interval] = []

        for i in range(len(j_stream)):
            self.open[interval].append(float(j_stream[i][1]))
            self.high[interval].append(float(j_stream[i][2]))
            self.low[interval].append(float(j_stream[i][3]))
            self.close[interval].append(float(j_stream[i][4]))
            self.volume[interval].append(float(j_stream[i][5]))

            utc_offset = -8
            t_ = datetime(1970, 1, 1) + timedelta(milliseconds=j_stream[i][0])
            currently_dst = self.isDST(t_, utc_offset)
            if currently_dst is True and start_time is None:
                t_ += timedelta(hours=utc_offset + 1)
            else:
                t_ += timedelta(hours=utc_offset)

            self.timestamp[interval].append(int(t_.timestamp()))
            self.date[interval].append(t_)
            