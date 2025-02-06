import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Brush, ResponsiveContainer } from "recharts";
import "./StockPrediction.css";

function StockPrediction() {
  const [ticker, setTicker] = useState("");
  const [predictions, setPredictions] = useState<number[]>([]);

  const fetchPredictions = async () => {
    const response = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker, start_date: "2020-01-01", end_date: "2025-01-30", forecast_out: 7 }),
    });
    const data = await response.json();
    setPredictions(data.predictions);
  };

  // Transform predictions into an array of objects
  const chartData = predictions.map((value, index) => ({
    index: index + 1, // X-axis index
    value: value, // Predicted stock price
  }));

  return (
    <div className="p-4 border rounded">
      <input
        type="text"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
        placeholder="Enter Stock Ticker"
        className="border p-2 mr-2"
      />
      <button onClick={fetchPredictions} className="bg-blue-500 text-white p-2 rounded">Predict</button>

      <div className="mt-4">
        {predictions.length > 0 && <h2 className="text-lg font-bold">Predictions:</h2>}
        <ul>
          {predictions.map((p, index) => (
            <li key={index}>{p.toFixed(2)}</li>
          ))}
        </ul>

        {predictions.length > 0 && (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="index" 
                domain={["auto", "auto"]} 
                allowDataOverflow 
                tickCount={7} 
              />
              <YAxis 
                dataKey="value" 
                domain={["auto", "auto"]} 
                allowDataOverflow 
              />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#10B981" strokeWidth={2} dot={false} />
              <Brush dataKey="index" height={30} stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

export default StockPrediction;
