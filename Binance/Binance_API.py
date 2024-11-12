from datetime import datetime, timedelta
import requests
import hashlib
import hmac
import time
import json

class BINANCE_API:
    def __init__(self, secret, public):
        self.session = requests.Session()
        # Endpoints
        self.base = 'https://api.binance.us'
        self.exchange = '/api/v3/exchangeInfo'
        self.time = '/api/v3/time'
        self.klines = '/api/v3/klines'
        self.ticker = '/api/v3/ticker/price'
        self.order = '/api/v3/order'
        self.active = '/api/v3/openOrders'
        self.oco_order = '/api/v3/order/oco'
        self.account = '/api/v3/account'
        # Sides
        self.buy = 'BUY'
        self.sell = 'SELL'
        # Options
        self.market = 'MARKET'
        self.limit = 'LIMIT'
        # Periods
        self.MIN_5 = "5m"
        self.MIN_15 = "15m"
        self.HOUR_1 = "1h"
        self.HOUR_2 = "2h"
        self.HOUR_4 = "4h"
        self.DAY_1 = "1d"

        self.api_s = secret
        self.api_k = public
        
        self.timestamp = {}
        self.date = {}
        self.dst = {}

        self.open = {}
        self.high = {}
        self.low = {}
        self.close = {}
        self.volume = {}

        self.request_weight = 0
        self.order_weight = 0

        self.information = {}
        with open('Binance\info.txt', 'r') as file:
            for line in file:
                j = json.loads(line)
                pair = j['symbol']
                self.information[pair] = j

    def update_weights(self, request=None, order=None):
        if request is not None:
            self.request_weight = request.headers['x-mbx-used-weight-1m']
        if order is not None:
            self.order_weight = order.headers['x-mbx-order-count-10s']

    def delay(self, threshold=0.7):
        if self.request_weight > 1200 * threshold:
            time.sleep(60)
        elif self.order_weight > 10 * threshold:
            time.sleep(10)

    def hashing(self, query_string: str):
        return hmac.new(self.api_s.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

    def get_timestamp(self):
        query = self.base + self.time
        current_time = self.session.get(query)
        self.update_weights(request=current_time)
        return current_time.json()['serverTime']

    def get_open_orders(self, window=10000):
        query = self.base + self.active
        ms_time = self.get_timestamp()
        parameters = f'recvWindow={window}&timestamp={ms_time}'
        signature = self.hashing(parameters)
        url = query + '?' + parameters + f'&signature={signature}'
        header = {'X-MBX-APIKEY': self.api_k}
        info = self.session.get(url, headers=header, timeout=30, verify=True)
        self.update_weights(request=info)
        return info.json()
    
    def symbol_tick(self, symbol):
        query = self.base + self.ticker
        url = query + '?' + f"symbol={symbol}"
        info = self.session.get(url)
        self.update_weights(request=info)
        return info.json()

    def exchange_info(self, symbol):
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

            self.update_weights(request=info)
            return info.json()["symbols"][0]

    def get_account(self, window=10000):
        query = self.base + self.account
        ms_time = self.get_timestamp()
        parameters = f'recvWindow={window}&timestamp={ms_time}'
        signature = self.hashing(parameters)
        url = query + '?' + parameters + f'&signature={signature}'
        header = {'X-MBX-APIKEY': self.api_k}
        post = self.session.get(url, headers=header, timeout=30, verify=True)
        self.update_weights(request=post)
        return post.json()
    
    def find_balance(self, currency):
        wallet = self.get_account()['balances']
        for i in range(len(wallet)):
            if wallet[i]['asset'] == currency:
                balance = float(wallet[i]['free'])
                return balance
            
    def get_base_asset(self, symbol):
        base_asset = self.exchange_info(symbol)['baseAsset']
        value = self.find_balance(base_asset)
        return [base_asset, value]
    
    def get_quote_asset(self, symbol):
        quote_asset = self.exchange_info(symbol)['quoteAsset']
        value = self.find_balance(quote_asset)
        return [quote_asset, value]

    def send_order(self, symbol, side, option, price=None, quantity=None, quoteQty=None):
        url = self.base + self.order

        step = self.exchange_info(symbol)['filters'][2]['stepSize'].rstrip('0')
        precision = len(step.split('.')[1])

        if quantity is not None and quoteQty is not None or \
            quantity is None and quoteQty is None or \
            option == self.limit and price is None or \
            option == self.market and price is not None:
            return 'Invalid'
        
        if quantity is not None:
            quantity = round(quantity, precision)

        elif quoteQty is not None:
            quantity = round(quoteQty / float(self.symbol_tick(symbol)['price']), precision)

        if price is not None:
            price = '{0:.10f}'.format(price).rstrip('0')

        time_in_force = None
        if option == self.limit:
            time_in_force = "GTC"

        parameters = {'symbol': symbol, 'side': side, 'type': option, 'timeInForce': time_in_force,
                      'quantity': quantity, 'price': price}

        query = ""
        for item in parameters:
            if parameters[item] is not None:
                query += f"{item}={parameters[item]}&"
        ms_time = self.get_timestamp()
        query += f"recvWindow=7500&timestamp={ms_time}"
        signature = self.hashing(query)
        header = {'X-MBX-APIKEY': self.api_k}
        url = url + '?' + query + f'&signature={signature}'
        post = self.session.post(url, headers=header, timeout=30, verify=True)
        self.update_weights(order=post)
        return post.json()

    def cancel_order(self, symbol, order_id=None):
        if order_id is None:
            url = self.base + self.active
        else:
            url = self.base + self.order

        parameters = {'symbol': symbol, 'orderId': order_id}
        query = ""
        for item in parameters:
            if parameters[item] is not None:
                query += f'{item}={parameters[item]}&'

        ms_time = self.get_timestamp()
        query += f"timestamp={ms_time}"
        signature = self.hashing(query)
        header = {'X-MBX-APIKEY': self.api_k}
        url = url + '?' + query + f'&signature={signature}'
        delete = self.session.delete(url, headers=header, timeout=30, verify=True)
        self.update_weights(request=delete)
        return delete.json()
    
    def is_dst(self, dt: datetime, offset=0):
        dt += timedelta(hours=offset)
        if dt.year in self.dst:
            if self.dst[dt.year][0] <= dt <= self.dst[dt.year][1]:
                return True
            else:
                return False
        # DST: Starts 2nd Sunday on March, Ends 1st Sunday on November
        begin_dst = datetime(dt.year, 3, 1)
        sunday = 0
        while True:
            if begin_dst.weekday() == 6:
                sunday += 1
                if sunday == 2:
                    break
            begin_dst += timedelta(days=1)

        end_dst = datetime(dt.year, 11, 1)
        sunday = 0
        while True:
            if end_dst.weekday() == 6:
                sunday += 1
                if sunday == 1:
                    break
            end_dst += timedelta(days=1)

        self.dst[dt.year] = [begin_dst, end_dst]
        return self.is_dst(dt)

    def get_klines(self, symbol, interval, start_time=None):
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
            currently_dst = self.is_dst(t_, utc_offset)
            if currently_dst is True and start_time is None:
                t_ += timedelta(hours=utc_offset + 1)
            else:
                t_ += timedelta(hours=utc_offset)

            self.timestamp[interval].append(int(t_.timestamp()))
            self.date[interval].append(t_)
