import { useState } from "react";
import axios from "axios";

export default function StockAnalyzer() {
  const [company, setCompany] = useState("");
  const [ticker, setTicker] = useState("");
  const [ownedStock, setOwnedStock] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:8000/Indicotor", {
        company,
        ticker,
        owned_stock: ownedStock,
      });
      setResult(response.data);
    } catch (error) {
      console.error("Error fetching data", error);
    }
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-lg mx-auto bg-white rounded-xl shadow-md space-y-4">
      <h1 className="text-xl font-bold">Stock Impact Predictor</h1>
      <input
        type="text"
        placeholder="Company Name"
        className="border p-2 w-full"
        value={company}
        onChange={(e) => setCompany(e.target.value)}
      />
      <input
        type="text"
        placeholder="Stock Ticker"
        className="border p-2 w-full"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
      />
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          checked={ownedStock}
          onChange={(e) => setOwnedStock(e.target.checked)}
        />
        <label>Do you own this stock?</label>
      </div>
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? "Analyzing..." : "Predict Impact"}
      </button>
      {result && (
        <div className="mt-4 p-4 border rounded">
          <h2 className="text-lg font-semibold">Results</h2>
          <p><strong>Impact:</strong> {result.impact}%</p>
          <p><strong>Trade Decision:</strong> {result.trade_decision}</p>
          <h3 className="text-md font-semibold mt-2">Technical Indicators</h3>
          <p><strong>RSI:</strong> {result.RSI}</p>
          <p><strong>EMA:</strong> {result.EMA}</p>
          <p><strong>MACD:</strong> {result.MACD}</p>
          <p><strong>Bollinger Bands:</strong> Low: {result.Bollinger_Bands.Low}, Mid: {result.Bollinger_Bands.Mid}, Up: {result.Bollinger_Bands.Up}</p>
          <p><strong>OBV:</strong> {result.OBV}</p>
        </div>
      )}
    </div>
  );
}
