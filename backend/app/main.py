import os
from fastapi import FastAPI
from pydantic import BaseModel
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import requests
from transformers import pipeline
from pandas.tseries.offsets import BDay
from typing import List, Dict, Optional





# API Keys and Configuration
API_KEY = "pub_6830389454d2be3370f4b9fd5786223c9d6ad"

# Initialize FinBERT Sentiment Analysis Pipeline
sentiment_pipeline = pipeline("text-classification", model="ProsusAI/finbert")

# FastAPI App Setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class StockRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    forecast_out: int = 7

class NewsResponse(BaseModel):
    impact: float
    reasons: List[str]

class StockPrice(BaseModel):
    name: str
    price: float

class StockPricesResponse(BaseModel):
    stocks: List[StockPrice]

# Market Calendar
MARKET_HOLIDAYS_2025 = [
    "2025-01-01",  # New Year's Day
    "2025-01-26",  # Republic Day
    "2025-03-17",  # Holi
    "2025-04-14",  # Dr. Ambedkar Jayanti
    "2025-04-18",  # Good Friday
    "2025-05-01",  # Maharashtra Day
    "2025-08-15",  # Independence Day
    "2025-10-02",  # Gandhi Jayanti
    "2025-10-24",  # Dussehra
    "2025-11-12",  # Diwali
    "2025-12-25",  # Christmas
]

def get_next_business_days(start_date: datetime, num_days: int) -> List[datetime]:
    business_days = []
    current_date = pd.Timestamp(start_date)
    
    while len(business_days) < num_days:
        if current_date.strftime('%Y-%m-%d') not in MARKET_HOLIDAYS_2025 and current_date.weekday() < 5:
            business_days.append(current_date)
        current_date = current_date + BDay(1)  # Move to the next business day
    
    return business_days


def fetch_news(company: str) -> List[str]:
    """
    Fetch latest news articles for a company using NewsData.io API
    """
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&q={company}&country=in"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'results' not in data:
            return []
        
        return [
            article['title'] + " " + (article.get('description', '') or '')
            for article in data['results']
        ]
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []

def analyze_sentiment(news_list: List[str]) -> float:
    """
    Analyze sentiment of news articles using FinBERT
    """
    if not news_list:
        return 0.0
        
    try:
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
                sentiments.append(0)
        
        return float(np.mean(sentiments)) if sentiments else 0.0
    except Exception as e:
        print(f"Error analyzing sentiment: {str(e)}")
        return 0.0

@app.post("/predict")
async def predict_stock(data: StockRequest):
    """
    Predict stock prices using historical data, sentiment analysis, and SVR
    """
    try:
        # Fetch stock data
        stock_data = yf.download(data.ticker, start=data.start_date, end=data.end_date)
        
        if stock_data.empty:
            return {"error": "Stock data not available"}
        
        # Fetch and analyze news sentiment
        company_name = data.ticker.split(".")[0]
        sentiment_score = analyze_sentiment(fetch_news(company_name))
        
        # Prepare historical data
        historical_data = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "price": float(price),
                "type": "historical"
            }
            for date, price in zip(stock_data.index, stock_data['Close'])
        ]
        
        # Prepare features for prediction
        features = ['Open', 'High', 'Low', 'Close', 'Volume']
        stock_data['Sentiment'] = sentiment_score
        
        # Create prediction target
        stock_data['Target'] = stock_data['Close'].shift(-data.forecast_out)
        stock_data.dropna(inplace=True)
        
        # Prepare training data
        X = stock_data[features + ['Sentiment']].values
        y = stock_data['Target'].values
        
        # Split and scale data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        # Train SVR model
        svr = SVR(kernel='rbf', C=1e3, gamma=0.1)
        svr.fit(X_train_scaled, y_train)
        
        # Prepare prediction data
        last_data = stock_data[features + ['Sentiment']].tail(data.forecast_out).values
        last_data_scaled = scaler.transform(last_data)
        
        # Make predictions
        predictions = svr.predict(last_data_scaled)
        
        # Adjust predictions based on sentiment
        sentiment_adjustment = 1 + sentiment_score * 0.1
        predictions = predictions * sentiment_adjustment
        
        # Generate prediction dates
        last_date = max(stock_data.index[-1], pd.Timestamp.today().normalize())

        prediction_dates = get_next_business_days(last_date, len(predictions))
        
        # Prepare prediction data for response
        prediction_data = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "price": float(price),
                "type": "prediction"
            }
            for date, price in zip(prediction_dates, predictions)
        ]
        
        return {
            "data": historical_data + prediction_data,
            "sentiment_score": float(sentiment_score),
            "adjustment_factor": float(sentiment_score * 0.1)
        }
        
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

@app.get("/stock-prices")
async def get_stock_prices():
    """
    Get current stock prices for a predefined list of companies
    """
    stock_tickers = {
        "TCS": "TCS.NS",
        "Tata Steel": "TATASTEEL.NS",
        "Reliance": "RELIANCE.NS",
        "ICICI Bank": "ICICIBANK.NS"
    }
    
    try:
        stock_prices = []
        
        for stock_name, ticker in stock_tickers.items():
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            
            if not hist.empty:
                stock_price = float(hist["Close"].iloc[-1])
                stock_prices.append({"name": stock_name, "price": stock_price})
            else:
                stock_prices.append({"name": stock_name, "price": 0.0})
        
        return {"stocks": stock_prices}
        
    except Exception as e:
        return {"error": f"Failed to fetch stock prices: {str(e)}"}

@app.get("/news-impact/{company}")
async def news_impact(company: str):
    """
    Get news sentiment impact for a company based on its name.
    """
    try:
        # Fetch news using the company name
        news_list = fetch_news(company)

        # Analyze sentiment of the fetched news articles
        impact = analyze_sentiment(news_list)

        # Extract key phrases or sentences as reasons
        reasons = [news[:200] + "..." for news in news_list[:3]] if news_list else ["No relevant news found."]

        return {
            "company": company,
            "impact": float(impact),
            "reasons": reasons
        }

    except Exception as e:
        return {"error": f"Failed to analyze news impact: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)