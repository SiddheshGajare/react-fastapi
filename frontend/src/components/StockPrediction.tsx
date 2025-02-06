import { useState } from "react";

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
          {predictions.map((p, index) => <li key={index}>{p.toFixed(2)}</li>)}
        </ul>
      </div>
    </div>
  );
}

export default StockPrediction;
