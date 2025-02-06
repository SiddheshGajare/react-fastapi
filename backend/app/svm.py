import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.svm import SVR, SVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, accuracy_score, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict, Any
import logging
from datetime import datetime, timedelta
#RELIANCE.NS
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockPredictor:
    def __init__(self, ticker: str, start_date: str, end_date: str, forecast_days: int = 7):
        """
        Initialize the StockPredictor class.
        
        Args:
            ticker (str): Stock ticker symbol
            start_date (str): Start date for historical data (YYYY-MM-DD)
            end_date (str): End date for historical data (YYYY-MM-DD)
            forecast_days (int): Number of days to forecast
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.forecast_days = forecast_days
        self.stock_data = None
        self.scaler = StandardScaler()
        self.svr_model = None
        self.svc_model = None

    def fetch_stock_data(self) -> pd.DataFrame:
        """
        Fetch historical stock data from Yahoo Finance.
        
        Returns:
            pd.DataFrame: Historical stock data
        """
        try:
            logger.info(f"Fetching data for {self.ticker}")
            stock_data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
            
            if stock_data.empty:
                raise ValueError(f"No data found for ticker {self.ticker}")
            
            # Calculate technical indicators
            stock_data = self._add_technical_indicators(stock_data)
            self.stock_data = stock_data
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching stock data: {str(e)}")
            raise

    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to the dataset.
        
        Args:
            df (pd.DataFrame): Stock data DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with added technical indicators
        """
        # Moving averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        
        # Relative Strength Index (RSI)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['BB_middle'] = df['Close'].rolling(window=20).mean()
        df['BB_upper'] = df['BB_middle'] + 2 * df['Close'].rolling(window=20).std()
        df['BB_lower'] = df['BB_middle'] - 2 * df['Close'].rolling(window=20).std()
        
        # Volume indicators
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        # Drop NaN values
        return df.dropna()

    def prepare_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
        """
        Prepare data for SVM models.
        
        Returns:
            Tuple containing:
            - X (np.ndarray): Feature matrix
            - y_regression (np.ndarray): Target values for regression
            - y_classification (np.ndarray): Target values for classification
            - last_data (pd.DataFrame): Last n rows for prediction
        """
        if self.stock_data is None:
            self.fetch_stock_data()
            
        # Create features for prediction
        feature_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 
                         'SMA_5', 'SMA_20', 'RSI', 'MACD', 'Signal_Line',
                         'BB_middle', 'BB_upper', 'BB_lower', 'Volume_MA']
        
        # For Regression: Predict the future closing price
        self.stock_data['Target_Price'] = self.stock_data['Close'].shift(-self.forecast_days)
        
        # For Classification: Predict whether the price will go up (1) or down (0)
        self.stock_data['Target_Direction'] = np.where(
            self.stock_data['Close'].shift(-self.forecast_days) > self.stock_data['Close'], 1, 0
        )
        
        # Prepare features and targets
        X = self.stock_data[feature_columns].values[:-self.forecast_days]
        y_regression = self.stock_data['Target_Price'].values[:-self.forecast_days]
        y_classification = self.stock_data['Target_Direction'].values[:-self.forecast_days]
        
        # Get last data points for prediction
        last_data = self.stock_data[feature_columns].tail(self.forecast_days)
        
        return X, y_regression, y_classification, last_data

    def train_models(self, perform_gridsearch: bool = False) -> Dict[str, float]:
        """
        Train SVR and SVC models.
        
        Args:
            perform_gridsearch (bool): Whether to perform GridSearchCV
            
        Returns:
            Dict[str, float]: Dictionary containing model performance metrics
        """
        # Prepare data
        X, y_regression, y_classification, _ = self.prepare_data()
        
        # Split data
        X_train, X_test, y_reg_train, y_reg_test, y_cls_train, y_cls_test = train_test_split(
            X, y_regression, y_classification, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train SVR
        if perform_gridsearch:
            svr_params = {
                'C': [0.1, 1, 10, 100],
                'gamma': ['scale', 'auto', 0.1, 0.01],
                'kernel': ['rbf', 'linear']
            }
            self.svr_model = GridSearchCV(SVR(), svr_params, cv=5, n_jobs=-1)
        else:
            self.svr_model = SVR(kernel='rbf', C=100, gamma='auto')
            
        self.svr_model.fit(X_train_scaled, y_reg_train)
        
        # Train SVC
        if perform_gridsearch:
            svc_params = {
                'C': [0.1, 1, 10, 100],
                'gamma': ['scale', 'auto', 0.1, 0.01],
                'kernel': ['rbf', 'linear']
            }
            self.svc_model = GridSearchCV(SVC(), svc_params, cv=5, n_jobs=-1)
        else:
            self.svc_model = SVC(kernel='rbf', C=100, gamma='auto')
            
        self.svc_model.fit(X_train_scaled, y_cls_train)
        
        # Calculate metrics
        svr_predictions = self.svr_model.predict(X_test_scaled)
        svc_predictions = self.svc_model.predict(X_test_scaled)
        
        metrics = {
            'svr_mae': mean_absolute_error(y_reg_test, svr_predictions),
            'svr_mse': mean_squared_error(y_reg_test, svr_predictions),
            'svr_r2': r2_score(y_reg_test, svr_predictions),
            'svc_accuracy': accuracy_score(y_cls_test, svc_predictions)
        }
        
        logger.info(f"Model performance metrics: {metrics}")
        return metrics

    def predict(self) -> Dict[str, Any]:
        """
        Make predictions using trained models.
        
        Returns:
            Dict[str, Any]: Dictionary containing predictions and their dates
        """
        if self.svr_model is None or self.svc_model is None:
            self.train_models()
            
        _, _, _, last_data = self.prepare_data()
        last_data_scaled = self.scaler.transform(last_data)
        
        # Make predictions
        price_predictions = self.svr_model.predict(last_data_scaled)
        direction_predictions = self.svc_model.predict(last_data_scaled)
        
        # Generate future dates
        last_date = self.stock_data.index[-1]
        prediction_dates = [
            (last_date + timedelta(days=i+1)).strftime('%Y-%m-%d')
            for i in range(self.forecast_days)
        ]
        
        return {
            'dates': prediction_dates,
            'price_predictions': price_predictions.tolist(),
            'direction_predictions': direction_predictions.tolist()
        }

    def plot_predictions(self, predictions: Dict[str, Any]) -> None:
        """
        Plot the predictions.
        
        Args:
            predictions (Dict[str, Any]): Dictionary containing predictions
        """
        plt.figure(figsize=(15, 10))
        
        # Plot historical prices
        plt.subplot(2, 1, 1)
        plt.plot(self.stock_data.index, self.stock_data['Close'], label='Historical Close Price')
        
        # Plot predictions
        prediction_dates = [datetime.strptime(date, '%Y-%m-%d') for date in predictions['dates']]
        plt.plot(prediction_dates, predictions['price_predictions'], 
                'r--', label='Predicted Price')
        
        plt.title(f'{self.ticker} Stock Price Prediction')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        
        # Plot direction predictions
        plt.subplot(2, 1, 2)
        direction_colors = ['g' if d == 1 else 'r' for d in predictions['direction_predictions']]
        plt.bar(prediction_dates, predictions['direction_predictions'], 
               color=direction_colors, alpha=0.5)
        plt.title('Price Direction Prediction (Green=Up, Red=Down)')
        plt.xlabel('Date')
        plt.ylabel('Direction')
        
        plt.tight_layout()
        plt.show()

def main():
    """
    Main function to demonstrate the usage of StockPredictor class.
    """
    # Example usage
    predictor = StockPredictor(
        ticker='AAPL',
        start_date='2020-01-01',
        end_date='2024-01-30',
        forecast_days=7
    )
    
    try:
        # Train models
        metrics = predictor.train_models(perform_gridsearch=True)
        logger.info(f"Training metrics: {metrics}")
        
        # Make predictions
        predictions = predictor.predict()
        logger.info(f"Predictions: {predictions}")
        
        # Plot results
        predictor.plot_predictions(predictions)
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()