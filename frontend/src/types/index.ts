// frontend/src/types/index.ts

export interface StockRequest {
    ticker: string;
    start_date: string;
    end_date: string;
    forecast_days: number;
  }
  
  export interface PredictionResponse {
    dates: string[];
    historical_prices: (number | null)[];
    predicted_prices: (number | null)[];
    predicted_directions: (number | null)[];
  }
  
  export interface ChartDataPoint {
    date: string;
    historical: number | null;
    predicted: number | null;
    direction: number | null;
  }
  
  export type ChartData = ChartDataPoint[];