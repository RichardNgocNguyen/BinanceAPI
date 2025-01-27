from Binance.manageReq import BINANCE_API


# Parent: BiNANCE_API
# Child: POST
class POST(BINANCE_API):
    def __init__(self):
        # Parent Inherited Variables
        super().__init__()
        # POST Endpoints
        self.order = '/api/v3/order'
        # Sides
        self.buy = 'BUY'
        self.sell = 'SELL'
        # Options
        self.market = 'MARKET'
        self.limit = 'LIMIT'

    def sendOrder(self, symbol, side, option, price=None, quantity=None, quoteQty=None):
        url = self.base + self.order

        step = self.getExchangeInfo(symbol)['filters'][2]['stepSize'].rstrip('0')
        precision = len(step.split('.')[1])

        if quantity is not None and quoteQty is not None or \
            quantity is None and quoteQty is None or \
            option == self.limit and price is None or \
            option == self.market and price is not None:
            return 'Invalid'
        
        if quantity is not None:
            quantity = round(quantity, precision)

        elif quoteQty is not None:
            quantity = round(quoteQty / float(self.getSymbolTick(symbol)['price']), precision)

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
        ms_time = self.getTimestamp()
        query += f"recvWindow=7500&timestamp={ms_time}"
        signature = self.hashing(query)
        header = {'X-MBX-APIKEY': self.api_k}
        url = url + '?' + query + f'&signature={signature}'
        post = self.session.post(url, headers=header, timeout=30, verify=True)
        self.updateWeights(order=post)
        return post.json()

    def cancelOrder(self, symbol, order_id=None):
        if order_id is None:
            url = self.base + self.active
        else:
            url = self.base + self.order

        parameters = {'symbol': symbol, 'orderId': order_id}
        query = ""
        for item in parameters:
            if parameters[item] is not None:
                query += f'{item}={parameters[item]}&'

        ms_time = self.getTimestamp()
        query += f"timestamp={ms_time}"
        signature = self.hashing(query)
        header = {'X-MBX-APIKEY': self.api_k}
        url = url + '?' + query + f'&signature={signature}'
        delete = self.session.delete(url, headers=header, timeout=30, verify=True)
        self.updateWeights(request=delete)
        return delete.json()
    