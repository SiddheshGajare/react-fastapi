// frontend/src/services/api.ts
import { StockRequest, PredictionResponse } from '../types';
const currentDate = new Date();
const formattedDate = currentDate.toISOString().split('T')[0];
const API_BASE_URL = 'http://localhost:8000/api';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export const fetchPredictions = async (ticker: string): Promise<PredictionResponse> => {
  try {
    const request: StockRequest = {
      ticker,
      start_date: '2020-01-01',
      end_date: formattedDate,
      forecast_days: 7
    };

    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new ApiError(response.status, errorData.detail || 'Failed to fetch predictions');
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error(error instanceof Error ? error.message : 'An unknown error occurred');
  }
};