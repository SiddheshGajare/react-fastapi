import requests
import yfinance as yf
import pandas as pd
import numpy as np
import ta  # For technical indicators
from transformers import pipeline

# ✅ NewsData.io API Key
API_KEY = "pub_6830389454d2be3370f4b9fd5786223c9d6ad"

# ✅ FinBERT Sentiment Analysis Pipeline
sentiment_pipeline = pipeline("text-classification", model="ProsusAI/finbert")

# ✅ Function to Fetch Latest News
def fetch_news(company):
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&q={company}&country=in"
    response = requests.get(url)
    data = response.json()
    
    if 'results' not in data:
        return []
    
    return [article['title'] + " " + (article.get('description', '') or '') for article in data['results']]

# ✅ Function to Analyze News Sentiment
def analyze_sentiment(news_list):
    sentiments = []
    for news in news_list:
        result = sentiment_pipeline(news)[0]
        sentiment = result['label']
        score = result['score']
        
        if sentiment == "positive":
            sentiments.append(score)
        elif sentiment == "negative":
            sentiments.append(-score)
        else:
            sentiments.append(0)  # Neutral has no effect
    
    return np.mean(sentiments) if sentiments else 0  # Return average sentiment score

# ✅ Function to Fetch Live Stock Price & Calculate Indicators
def fetch_stock_indicators(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="1mo", interval="1d")  # Last 1 month data

    if df.empty:
        return None

    # Calculate Technical Indicators
    df["EMA"] = ta.trend.ema_indicator(df["Close"], window=20)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
    df["MACD"] = ta.trend.macd(df["Close"])
    df["Bollinger_Up"], df["Bollinger_Mid"], df["Bollinger_Low"] = ta.volatility.bollinger_hband(df["Close"]), ta.volatility.bollinger_mavg(df["Close"]), ta.volatility.bollinger_lband(df["Close"])
    df["OBV"] = ta.volume.on_balance_volume(df["Close"], df["Volume"])

    return df.iloc[-1]  # Return the latest stock indicators

# ✅ Function to Predict Stock Impact
def predict_stock_impact(company, ticker):
    news_list = fetch_news(company)
    sentiment_score = analyze_sentiment(news_list)
    
    stock_data = fetch_stock_indicators(ticker)
    if stock_data is None:
        return "Stock data not available"

    # Convert sentiment score to impact percentage
    impact = sentiment_score * 10  

    # Trading Decision Based on Indicators & Sentiment
    trade_signal = "Hold"
    if sentiment_score > 0.05 and stock_data["RSI"] < 70:
        trade_signal = "Buy"
    elif sentiment_score < -0.05 and stock_data["RSI"] > 30:
        trade_signal = "Sell"

    # Display Results
    print(f"\n📊 Predicted News Impact on {company}: {impact:.2f}%")
    print(f"📈 Technical Indicators:")
    print(f"   - RSI: {stock_data['RSI']:.2f}")
    print(f"   - EMA: {stock_data['EMA']:.2f}")
    print(f"   - MACD: {stock_data['MACD']:.2f}")
    print(f"   - Bollinger Bands: ({stock_data['Bollinger_Low']:.2f}, {stock_data['Bollinger_Mid']:.2f}, {stock_data['Bollinger_Up']:.2f})")
    print(f"   - OBV: {stock_data['OBV']:.2f}")
    print(f"\n💡 Suggested Trade Decision: {trade_signal}")

    return impact

# ✅ Run Model for TCS (Example)
if __name__ == "__main__":

    company_name = input("Enter company name: ")
    stock_ticker = company_name+".NS"  # Use ".NS" for Indian NSE stocks on Yahoo Finance
    predict_stock_impact(company_name, stock_ticker)
