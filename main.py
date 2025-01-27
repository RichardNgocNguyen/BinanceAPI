from Binance.getReq import GET
from Binance.postReq import POST
from Binance.Indicators import INDICATOR


'''
SHIBUSDT -> Base: SHIB
            Quote: USDT
'''

get = GET()

# print(get.getSymbolTick('SHIBUSDT'))

# print(get.getAccount())

# print(get.getBalance('SHIB'))

# print(get.getExchangeInfo('SHIBUSDT'))
# print(get.information)

# print(get.getBaseAsset('SHIBUSDT'))
# print(get.getQuoteAsset('SHIBUSDT'))

# print(get.getOpenOrders())



# Requires a GET request for Kline Data
get.getKlines(symbol='SHIBUSDT', interval=get.HOUR_4)
analysis = INDICATOR(date=get.date[get.HOUR_4], opens= get.open[get.HOUR_4], 
                     highs= get.high[get.HOUR_4], lows= get.low[get.HOUR_4], 
                     closes= get.close[get.HOUR_4], volume= get.volume[get.HOUR_4])
                
# print('Upper Band', analysis.BOLL()['upper band'][-4:], '\n')
# print('Middle Band', analysis.BOLL()['middle band'][-4:], '\n')
# print('Lower Band', analysis.BOLL()['lower band'][-4:], '\n')



post = POST()

                                        # Uses base asset (SHIB)
# market_buy = post.sendOrder(symbol='SHIBUSDT', side=post.buy, option=post.market, quantity=558295)
# limit_buy = post.sendOrder(symbol='SHIBUSDT', side=post.buy, option=post.limit, price=0.00001600, quantity=761305)
# market_sell = post.sendOrder(symbol='SHIBUSDT', side=post.sell, option=post.market, quantity=558290)
# limit_sell = post.sendOrder(symbol='SHIBUSDT', side=post.sell, option=post.limit, price=0.00002500, quantity=558290)


                                        # Uses quote asset (USDT)
# market_buy = post.sendOrder(symbol='SHIBUSDT', side=post.buy, option=post.market, quoteQty=11)
# limit_buy = post.sendOrder(symbol='SHIBUSDT', side=post.buy, option=post.limit, price=0.00001500, quoteQty=15)         
# market_sell = post.sendOrder(symbol='SHIBUSDT', side=post.sell, option=post.market, quoteQty=11)
# limit_sell = post.sendOrder(symbol='SHIBUSDT', side=post.sell, option=post.limit, price=0.000024, quoteQty=11)

# cancel_order = post.cancelOrder('SHIBUSDT')
