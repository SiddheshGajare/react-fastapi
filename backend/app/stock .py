import yfinance as yf

# List of stock tickers for NSE
stock_tickers = {
    "TCS": "TCS.NS",
    "Tata Steel": "TATASTEEL.NS",
    "Reliance": "RELIANCE.NS",
    "ICICI Bank": "ICICIBANK.NS"
}

def get_stock_prices():
    print("Fetching stock prices...\n")
    
    for stock_name, ticker in stock_tickers.items():
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")  # Fetch latest day's data
        
        if not hist.empty:
            stock_price = hist["Close"].iloc[-1]  # Get latest closing price
            print(f"{stock_name}: ₹{stock_price:.2f}")
        else:
            print(f"{stock_name}: Data not available")

if __name__ == "__main__":
    get_stock_prices()
