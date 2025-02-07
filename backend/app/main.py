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

@app.post("/predict")
def predict_stock(data: StockRequest):
    # Download stock data
    stock_data = yf.download(data.ticker, start=data.start_date, end=data.end_date)
    
    # Prepare historical data for response
    historical_data = [
        {
            "date": date.strftime("%Y-%m-%d"),
            "price": price,
            "type": "historical"
        }
        for date, price in zip(stock_data.index, stock_data['Close'])
    ]
    
    # Prepare data for prediction
    stock_data['Prediction'] = stock_data['Close'].shift(-data.forecast_out)
    stock_data.dropna(inplace=True)
    
    X = np.array(stock_data.drop(['Prediction'], axis=1))
    y = np.array(stock_data['Prediction'])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    
    svr = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr.fit(X_train, y_train)
    
    last_data = scaler.transform(X[-data.forecast_out:])
    predictions = svr.predict(last_data)
    
    # Generate dates for predictions
    last_date = stock_data.index[-1]
    prediction_dates = [
        (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d")
        for i in range(len(predictions))
    ]
    
    # Prepare prediction data for response
    prediction_data = [
        {
            "date": date,
            "price": price,
            "type": "prediction"
        }
        for date, price in zip(prediction_dates, predictions)
    ]
    
    return {
        "data": historical_data + prediction_data
    }