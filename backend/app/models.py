# backend/app/models.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StockRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    forecast_days: int = 7

class PredictionData(BaseModel):
    date: str
    price: float
    direction: Optional[int] = None

class PredictionResponse(BaseModel):
    dates: List[str]
    historical_prices: List[Optional[float]]
    predicted_prices: List[Optional[float]]
    predicted_directions: List[Optional[int]]

class ErrorResponse(BaseModel):
    detail: str