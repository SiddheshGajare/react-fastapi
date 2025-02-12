import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Brush, ResponsiveContainer, Legend } from "recharts";
import { Bell, Mail, ChevronDown, Home, LayoutDashboard, Wallet, Newspaper, BarChart2, Users, Settings, Phone, ChevronUp } from 'lucide-react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import './StockDashboard.css';

// Get today's date in 'YYYY-MM-DD' format
const date = new Date();
const formattedDate = date.toLocaleDateString('en-CA', { month: '2-digit', day: '2-digit', year: 'numeric' });

interface StockDataPoint {
  date: string;
  price: number;
  type: 'historical' | 'prediction';
}

const StockCards = () => {
  const [stocks, setStocks] = useState<{ name: string; price: number | string }[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/stock-prices")
      .then((response) => response.json())
      .then((data) => setStocks(data.stocks))
      .catch((error) => console.error("Error fetching stock prices:", error));
  }, []);

  return (
    <div className="stock-cards">
      {stocks.map((stock) => (
        <div key={stock.name} className="stock-card">
          <div className="stock-info">
            <span>{stock.name}</span>
          </div>
          <div className="stock-values">
            <div>Current Price</div>
            <div className="stock-amount">₹{stock.price}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

function StockDashboard() {
  const [ticker, setTicker] = useState("");
  const [stockData, setStockData] = useState<StockDataPoint[]>([]);
  const navigate = useNavigate();

  const fetchPredictions = async () => {
    const response = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ticker,
        start_date: "2020-01-01",
        end_date: formattedDate,
        forecast_out: 7
      }),
    });
    const data = await response.json();
    setStockData(data.data);
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const historicalValue = payload.find(p => p.dataKey === 'historicalPrice')?.value;
      const predictedValue = payload.find(p => p.dataKey === 'predictedPrice')?.value;
      const value = historicalValue ?? predictedValue;
      const type = historicalValue ? 'Historical' : 'Predicted';

      return (
        <div className="custom-tooltip bg-white p-4 rounded shadow">
          <p className="date">{new Date(label).toLocaleDateString()}</p>
          <p className="price">${value?.toFixed(2)}</p>
          <p className="type">{type}</p>
        </div>
      );
    }
    return null;
  };

  const handleBlur = () => {
    if (ticker && !ticker.endsWith(".NS")) {
      setTicker(ticker + ".NS"); // Ensure NSE format
    }
  };

  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="dashboard-container">
      <div className="dashboard-layout">
        {/* Sidebar */}
        <div className="sidebar">
          <div className='nav-first-container'>
            <div className="logo-container">
              <BarChart2 className="nav-icon" />
              <span className="logo-text">GoStock</span>
            </div>

            <div className="investment-card">
              <div className="investment-label">Total Investment</div>
              <div className="investment-amount">$5380.90</div>
              <div className="investment-percentage">+18.10%</div>
            </div>
          </div>
          <div className='nev-bar'>
            <nav>
              <div className='nev-2ndcontainer'>
                <div className="nav-item" onClick={() => navigate('/suggetion')}>
                  <Home className="nav-icon" />
                  <span>Home</span>
                </div>
                <div className="nav-item" onClick={() => navigate('/dashBoard')}>
                  <LayoutDashboard className="nav-icon" />
                  <span>Dashboard</span>
                </div>
                <div className="nav-item">
                  <Wallet className="nav-icon" />
                  <span>Wallet</span>
                </div>
                <div className="nav-item"  onClick={() => navigate('/news')}>
                  <Newspaper className="nav-icon" />
                  <span>News</span>
                </div>
              </div>
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="main-content">
          {/* Search Bar */}
          <div className="search-bar">
            <div className='search'>
              <input
                type="text"
                value={ticker.replace(".NS", "")}
                onChange={(e) => setTicker(e.target.value)}
                onBlur={handleBlur}
                placeholder="Search for various stocks..."
                className="search-input"
              />
              <button onClick={fetchPredictions} className="search-button">🔍</button>
            </div>
          </div>

          {/* Stock Price Section */}
          <h2 className="section-title">Stock Prices</h2>
          <StockCards />

          {/* Stock Chart */}
          <div className="chart-container">
            <h2 className="section-title">Stock Predictions</h2>
            {stockData.length > 0 && (
              <ResponsiveContainer width="100%" height={400}>
                <LineChart 
                  data={stockData.map(item => ({
                    ...item,
                    historicalPrice: item.type === 'historical' ? item.price : null,
                    predictedPrice: item.type === 'prediction' ? item.price : null,
                    date: item.date
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} angle={-45} textAnchor="end" height={60} />
                  <YAxis domain={['auto', 'auto']} tickFormatter={(value) => `$${value.toFixed(2)}`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Line type="monotone" dataKey="historicalPrice" stroke="#10B981" strokeWidth={2} dot={false} name="Historical Price" connectNulls={true} />
                  <Line type="monotone" dataKey="predictedPrice" stroke="#FF9933" strokeWidth={2} dot={false} name="Predicted Price" connectNulls={true} strokeDasharray="5 5" />
                  <Brush dataKey="date" height={30} stroke="#8884d8" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default StockDashboard;
