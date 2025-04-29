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
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import ta  




# API Keys and Configuration for newIo {News sentiment}
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
class StockRequest2(BaseModel):
    company: str
    ticker: str
    owned_stock: bool

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
def analyze_sentiment1(news_list: List[str]) -> float:
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

def fetch_stock_indicators(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="1mo", interval="1d")  # Last 1 month data

    if df.empty:
        return None

    # Calculate Technical Indicators
    df["EMA"] = ta.trend.ema_indicator(df["Close"], window=20)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
    df["MACD"] = ta.trend.macd(df["Close"])
    df["Bollinger_Up"], df["Bollinger_Mid"], df["Bollinger_Low"] = (
        ta.volatility.bollinger_hband(df["Close"]), 
        ta.volatility.bollinger_mavg(df["Close"]), 
        ta.volatility.bollinger_lband(df["Close"])
    )
    df["OBV"] = ta.volume.on_balance_volume(df["Close"], df["Volume"])
    df.fillna(0, inplace=True)  # This will replace all NaN values with 0

    return df.iloc[-1].to_dict() 


def analyze_sentiment(news_list: List[str]) -> float:
    """
    Analyze sentiment of news articles using FinBERT
    """
    if not news_list:
        return 0.0

    try:
        sentiments = []
        print("\n===== News Sentiment Analysis =====\n")

        for news in news_list:
            result = sentiment_pipeline(news)[0]

            # Extract sentiment probabilities (assumed based on FinBERT behavior)
            sentiment = result['label']
            score = result['score']

            if sentiment == "positive":
                sentiment_score = score * 10  # Scale up positive impact
            elif sentiment == "negative":
                sentiment_score = -score * 10  # Scale up negative impact
            else:  # Neutral case
                sentiment_score = 0.0

            # Store sentiment score for averaging
            sentiments.append(sentiment_score)

            # Print detailed probabilities
            print(f"News: {news[:100]}...")
            print(f"Sentiment Probabilities -> Negative: {1-score:.4f}, Neutral: {0.0000:.4f}, Positive: {score:.4f}")
            print(f"Calculated Sentiment Score: {sentiment_score:.4f}\n")

        # Compute average sentiment score
        avg_sentiment = float(np.mean(sentiments)) if sentiments else 0.0
        predicted_impact = round(avg_sentiment * 2, 2)  # Convert score to % impact

        print("===== Final Impact Calculation =====")
        print(f"Average Sentiment Score: {avg_sentiment:.4f}")
        print(f"Predicted Impact: {predicted_impact}%\n")

        return predicted_impact  # Return as a percentage change

    except Exception as e:
        print(f"Error analyzing sentiment: {str(e)}")
        return 0.0

@app.post("/predict")
async def predict_stock(data: StockRequest):
    """
    Predict stock prices using historical data, sentiment analysis, and SVR
    """
    try:
        # Debug: Print the input parameters
        print(f"Input parameters: ticker={data.ticker}, start_date={data.start_date}, end_date={data.end_date}")
        
        # Fetch stock data
        stock_data = yf.download(data.ticker, start=data.start_date, end=data.end_date)
        
        # Debug: Print what we received from Yahoo Finance
        #print(f"Downloaded stock data shape: {stock_data.shape}")
        #print(f"Downloaded stock data columns: {stock_data.columns}")
        #print(f"Downloaded stock data index: {stock_data.index}")
        #print(f"First 5 rows of stock data:")
        #print(stock_data.head())

        if stock_data.empty:
            return {"error": "Stock data not available"}

        # Create a copy of the original data for historical prices
        original_stock_data = stock_data.copy()

        # Fetch and analyze news sentiment
        company_name = data.ticker.split(".")[0]
        sentiment_score = analyze_sentiment1(fetch_news(company_name))

        # Ensure sentiment_score is a float
        try:
            sentiment_score = float(sentiment_score)
        except ValueError:
            sentiment_score = 0.0  # Default to neutral sentiment if conversion fails

        # Build historical_prices from the original data
        historical_prices = []
        
        # Debug: Check if the index and Close column exist
        #print(f"Original stock data index type: {type(original_stock_data.index)}")
        #print(f"Original stock data has Close column: {'Close' in original_stock_data.columns}")
        
        if 'Close' in original_stock_data.columns and len(original_stock_data) > 0:
            # Explicitly iterate over the dataframe rows to ensure we're accessing the data correctly
            for date_idx, row in original_stock_data.iterrows():
                try:
                    price = row['Close']
                    formatted_date = date_idx.strftime("%Y-%m-%d")
                    historical_prices.append({
                        "date": formatted_date,
                        "price": float(price),
                        "type": "historical"
                    })
                    print(f"Added historical price: {formatted_date}, {price}")
                except (ValueError, TypeError, AttributeError) as e:
                    print(f"Error processing row at {date_idx}: {e}")
        else:
            print("Cannot create historical prices: 'Close' column missing or dataframe is empty")

        # Debug: Print the first few historical prices to verify
        print(f"First 5 historical prices: {historical_prices[:5]}")
        print(f"Total historical prices: {len(historical_prices)}")

        # Define features
        features = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Add numeric sentiment column
        stock_data['Sentiment'] = sentiment_score

        # Create target variable
        stock_data['Target'] = stock_data['Close'].shift(-data.forecast_out)
        stock_data.fillna(method="ffill", inplace=True) 
        stock_data.dropna(inplace=True)

        # Ensure no invalid data before training
        if stock_data.isnull().values.any():
            return {"error": "Data contains NaN values after processing"}

        # Prepare training data
        X = stock_data[features + ['Sentiment']].values
        y = stock_data['Target'].values

        if len(X) == 0 or len(y) == 0:
            return {"error": "Not enough data for training"}

        # Split and scale data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test) 
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
        predictions *= sentiment_adjustment

        # Generate prediction dates
        last_date = max(stock_data.index[-1], pd.Timestamp.today().normalize())
        prediction_dates = get_next_business_days(last_date, len(predictions))

        # Prepare prediction response
        prediction_data = [
            {"date": date.strftime("%Y-%m-%d"), "price": float(price), "type": "prediction"}
            for date, price in zip(prediction_dates, predictions)
        ]
        
        # Calculate and print accuracy metrics
        y_pred_test = svr.predict(X_test_scaled)

# Calculate various metrics
        mse = mean_squared_error(y_test, y_pred_test)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred_test)
        r2 = r2_score(y_test, y_pred_test)

# Calculate Mean Absolute Percentage Error (MAPE)
        mape = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100

# Print all metrics to terminal
        print("\n==== MODEL EVALUATION METRICS ====")
        print(f"Mean Squared Error (MSE): {mse:.4f}")
        print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
        print(f"Mean Absolute Error (MAE): {mae:.4f}")
        print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")
        print(f"R-squared (R²): {r2:.4f}")
        print("================================\n")
        stock = yf.Ticker(data.ticker)
        hist = stock.history(period="1d")
        print(float(hist["Close"].iloc[-1]))
        print(data.ticker)
        print(prediction_data)
        # Return the combined data
        return {
            "name": data.ticker,
            "data": historical_prices + prediction_data,
            "Hdata": historical_prices,
            "curprice" :float(hist["Close"].iloc[-1]),
            "sentiment_score": float(sentiment_score),
            "adjustment_factor": float(sentiment_score * 0.1)
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(error_details)  # Logs the full error traceback
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
        news_list = fetch_news(company)
        if not news_list:
            return {"company": company, "impact": 0.0, "reasons": ["No relevant news found."]}

        impact = analyze_sentiment(news_list)

        # Generate detailed reasons
        reasons = []
        for news in news_list:
            result = sentiment_pipeline(news)[0]
            sentiment_label = result['label']
            score = result['score']

            if sentiment_label == "positive":
                sentiment_score = score * 10
                sentiment_text = "[Positive]"
            elif sentiment_label == "negative":
                sentiment_score = -score * 10
                sentiment_text = "[Negative]"
            else:
                sentiment_score = 0.0
                sentiment_text = "[Neutral]"

            # Format reason with sentiment label
            reason_text = f"{sentiment_text} {news[:150]}..."
            reasons.append(reason_text)

        return {"company": company, "impact": float(impact), "reasons": reasons}

    except Exception as e:
        return {"error": f"Failed to analyze news impact: {str(e)}"}


@app.post("/Indicotor")
def predict_stock_impact(stock_request: StockRequest2):
    news_list = fetch_news(stock_request.company)
    sentiment_score = analyze_sentiment1(news_list)

    stock_data = fetch_stock_indicators(stock_request.ticker)
    if stock_data is None:
        return {"error": "Stock data not available"}

    # Convert sentiment score to impact percentage
    impact = sentiment_score * 10  

    # Trading Decision Based on Indicators & Sentiment
    trade_signal = "No Action"
    
    if sentiment_score > 0.05 and stock_data["RSI"] < 70:
        trade_signal = "Buy"
    elif sentiment_score < -0.05 and stock_data["RSI"] > 30:
        trade_signal = "Sell" if stock_request.owned_stock else "Avoid"
    elif stock_request.owned_stock:
        trade_signal = "Hold"

    return {
        "company": stock_request.company,
        "ticker": stock_request.ticker,
        "impact": round(impact, 2),
        "RSI": round(stock_data["RSI"], 2),
        "EMA": round(stock_data["EMA"], 2),
        "MACD": round(stock_data["MACD"], 2),
        "Bollinger_Bands": {
            "Low": round(stock_data["Bollinger_Low"], 2),
            "Mid": round(stock_data["Bollinger_Mid"], 2),
            "Up": round(stock_data["Bollinger_Up"], 2)
        },
        "OBV": round(stock_data["OBV"], 2),
        "trade_decision": trade_signal
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)