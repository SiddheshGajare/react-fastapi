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

# ✅ NewsData.io API Key
API_KEY = "pub_6830389454d2be3370f4b9fd5786223c9d6ad"

# ✅ FinBERT Sentiment Analysis Pipeline
sentiment_pipeline = pipeline("text-classification", model="ProsusAI/finbert")

# ✅ FastAPI App Setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StockRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    forecast_out: int = 7

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
            sentiments.append(0)
    
    return np.mean(sentiments) if sentiments else 0

@app.post("/predict")
def predict_stock(data: StockRequest):
    # ✅ Fetch stock data
    stock_data = yf.download(data.ticker, start=data.start_date, end=data.end_date)
    
    if stock_data.empty:
        return {"error": "Stock data not available"}
    
    # ✅ Fetch and analyze news sentiment
    company_name = data.ticker.split(".")[0]
    sentiment_score = analyze_sentiment(fetch_news(company_name))
    
    # ✅ Prepare historical data for response
    historical_data = [
        {"date": date.strftime("%Y-%m-%d"), "price": price, "type": "historical"}
        for date, price in zip(stock_data.index, stock_data['Close'])
    ]
    
    # ✅ Prepare data for SVM model
    stock_data['Sentiment'] = sentiment_score
    stock_data['Prediction'] = stock_data['Close'].shift(-data.forecast_out)
    stock_data.dropna(inplace=True)
    
    X = np.array(stock_data.drop(['Prediction'], axis=1))
    y = np.array(stock_data['Prediction'])
    
    # ✅ Train SVR Model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    
    svr = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr.fit(X_train, y_train)
    
    # ✅ Predict Future Prices with Sentiment Impact
    last_data = scaler.transform(X[-data.forecast_out:])
    predictions = svr.predict(last_data) * (1 + sentiment_score * 0.1)  # Adjust based on sentiment
    
    # ✅ Generate prediction dates
    last_date = stock_data.index[-1]
    prediction_dates = [
        (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d")
        for i in range(len(predictions))
    ]
    
    # ✅ Prepare prediction data for response
    prediction_data = [
        {"date": date, "price": price, "type": "prediction"}
        for date, price in zip(prediction_dates, predictions)
    ]
    
    return {
        "data": historical_data + prediction_data,
        "sentiment_score": sentiment_score,
        "adjustment_factor": sentiment_score * 0.1
    }
