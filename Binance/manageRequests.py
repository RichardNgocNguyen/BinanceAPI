from datetime import datetime, timedelta
import requests
import hashlib
import hmac
import time
import json

from Binance import config

class BINANCE_API:
    def __init__(self):
        # Shared Session
        self.session = requests.Session()
        # Access Keys
        self.api_k = config.api_k
        self.api_s = config.api_s
        # Time Endpoints
        self.base = 'https://api.binance.us'
        self.time = '/api/v3/time'
        # Periods
        self.MIN_5 = "5m"
        self.MIN_15 = "15m"
        self.HOUR_1 = "1h"
        self.HOUR_2 = "2h"
        self.HOUR_4 = "4h"
        self.DAY_1 = "1d"
        # DST Range
        self.dst = {}
        # Rate Limits
        self.request_weight = 0
        self.order_weight = 0
        # Storage for Unique Asset Details
        self.information = {}
        with open('Binance\info.txt', 'r') as file:
            for line in file:
                j = json.loads(line)
                pair = j['symbol']
                self.information[pair] = j

    def getTimestamp(self):
        query = self.base + self.time
        current_time = self.session.get(query)
        self.updateWeights(request=current_time)
        return current_time.json()['serverTime']

    def updateWeights(self, request=None, order=None):
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

    def isDST(self, dt: datetime, offset=0):
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
        return self.isDST(dt)
    
