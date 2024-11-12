from Binance.Binance_API import BINANCE_API
from Binance.Indicators import INDICATORS
from Binance import config


# SHIBUSDT -> Base: SHIB, Quote: USDT

A = BINANCE_API(secret=config.api_s, public=config.api_k)


A.get_klines(symbol= "SHIBUSDT", interval= A.HOUR_4)
A.get_klines(symbol= "SHIBUSDT", interval= A.MIN_15)

I = INDICATORS(date=A.date[A.HOUR_4], opens= A.open[A.HOUR_4], 
               highs= A.high[A.HOUR_4], lows= A.low[A.HOUR_4], 
               closes= A.close[A.HOUR_4], volume= A.volume[A.HOUR_4])

# Uses base asset (SHIB)
# market_buy = A.send_order(symbol='SHIBUSDT', side=A.buy, option=A.market, quantity=1524390)
# limit_buy = A.send_order(symbol='SHIBUSDT', side=A.buy, option=A.limit, price=0.00001400, quantity=1349046)
# market_sell = A.send_order(symbol='SHIBUSDT', side=A.sell, option=A.market, quantity=1386927)
# limit_sell = A.send_order(symbol='SHIBUSDT', side=A.sell, option=A.limit, price=0.00002000, quantity=1349046)


# Uses quote asset (USDT)
# market_buy = A.send_order(symbol='SHIBUSDT', side=A.buy, option=A.market, quoteQty=25)
# limit_buy = A.send_order(symbol='SHIBUSDT', side=A.buy, option=A.limit, price=0.00001550, quoteQty=22)         
# market_sell = A.send_order(symbol='SHIBUSDT', side=A.sell, option=A.market, quoteQty=23)
# limit_sell = A.send_order(symbol='SHIBUSDT', side=A.sell, option=A.limit, price=0.00001950, quoteQty=22)

