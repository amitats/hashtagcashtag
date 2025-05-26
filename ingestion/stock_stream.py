import yfinance as yf
import time

def stream_stock_data(symbols):
    while True:
        for symbol in symbols:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d", interval="1m").tail(1)
            price = data['Close'].values[0]
            print(symbol, price)
            # Send to Kafka
            producer.send('stock_topic', {'symbol': symbol, 'price': price})
        time.sleep(60)

stream_stock_data(['AAPL', 'TSLA', 'AMZN'])
