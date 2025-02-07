import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Brush, ResponsiveContainer } from "recharts";
import { Bell, Mail, ChevronDown, Home, LayoutDashboard, Wallet, Newspaper, BarChart2, Users, Settings, Phone } from 'lucide-react';
import './StockDashboard.css';
const date = new Date();
const formattedDate = date.toLocaleDateString('en-CA', { month: '2-digit', day: '2-digit',year: 'numeric' });

const stockData = [
  { month: '15', value: 80 },
  { month: '16', value: 180 },
  { month: '17', value: 90 },
  { month: '18', value: 270 },
  { month: '19', value: 150 },
  { month: '20', value: 260 },
  { month: '21', value: 100 },
  { month: '22', value: 200 },
];

const portfolioStocks = [
  { name: 'Apple', logo: '🍎', value: '$310.40', return: '-1.10%', trend: 'down' },
  { name: 'Meta', logo: 'Ⓜ️', value: '$140.45', return: '-0.10%', trend: 'down' },
  { name: 'Microsoft', logo: '⊞', value: '$240.98', return: '+0.85%', trend: 'up' },
  { name: 'Google', logo: 'G', value: '$99.12', return: '-0.04%', trend: 'down' },
];

const watchlist = [
  { name: 'SPOT', company: 'Spotify', value: '$310.40', change: '-1.10%' },
  { name: 'ABNB', company: 'Airbnb', value: '$132.72', change: '-10.29%' },
  { name: 'SHOP', company: 'Shopify', value: '$28.57', change: '-6.48%' },
  { name: 'SONY', company: 'Playstation', value: '$71.86', change: '+0.98%' },
  { name: 'DBX', company: 'Dropbox Inc', value: '$20.44', change: '-3.08%' },

];

function StockDashboard () {
  const [ticker, setTicker] = useState("");
  const [predictions, setPredictions] = useState<number[]>([]);

  const fetchPredictions = async () => {
    const response = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker, start_date: "2020-01-01", end_date: formattedDate, forecast_out: 7 }),
    });
    const data = await response.json();
    setPredictions(data.predictions);
  };

  // Transform predictions into an array of objects
  const chartData = predictions.map((value, index) => ({
    index: index + 1, // X-axis index
    value: value, // Predicted stock price
  }));

  const handleBlur = () => {
    if (ticker && !ticker.endsWith(".NS")) {
      setTicker(ticker + ".NS"); // Save with ".NS" on blur
    }
  };
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
               <div className="nav-item">
              <Home className="nav-icon" />
              <span>Home</span>
              </div>
             <div className="nav-item">
              <LayoutDashboard className="nav-icon" />
              <span>Dashboard</span>
              </div>
             <div className="nav-item">
              <Wallet className="nav-icon" />
              <span>Wallet</span>
              </div>
             <div className="nav-item">
              <Newspaper className="nav-icon" />
              <span>News</span>
            </div>
            
            <div className="nav-item">
              <BarChart2 className="nav-icon" />
              <span>Stock & fund</span>
              <ChevronDown className="ml-auto" />
            </div>
            <div className="nav-sub-item">Stock</div>
            <div className="nav-sub-item">Cryptocurrency</div>
            <div className="nav-sub-item">Mutual Fund</div>
            <div className="nav-sub-item">Gold</div>
            </div>
            <div className='line'></div>
            <div className='nav-third-container'>
            <div className="nav-item">
              <Users className="nav-icon" />
              <span>Our community</span>
            </div>
            <div className="nav-item">
              <Settings className="nav-icon" />
              <span>Settings</span>
            </div>
            <div className="nav-item">
              <Phone className="nav-icon" />
              <span>Contact us</span>
            </div>
            </div>
          </nav>
          </div>
          
        </div>

        {/* Main Content */}
        <div className="main-content">
          {/* Header */}
          <div className="search-bar">
            <div className='search'>
            <input
              type="text"
              value={ticker.replace(".NS", "")} 
              onChange={(e) => setTicker(e.target.value)}
              onBlur={handleBlur}
              placeholder="Search for various stocks........"
              className="search-input"
            />
            <button onClick={fetchPredictions} className="search-button"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
  <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/>
</svg></button>
            </div>
            <div className="header-actions">
              <Mail />
              <Bell />
              <div className="profile">
                <div className="profile-image"></div>
                <span>Airlangga Mahesa</span>
                <ChevronDown />
              </div>
            </div>
          </div>

          {/* Portfolio Section */}
          <h2 className="section-title">My Portfolio</h2>
          <div className="portfolio-section">
            
            <div className="stock-cards">
              {portfolioStocks.map((stock) => (
                <div key={stock.name} className="stock-card">
                  <div className="stock-info">
                    <span>{stock.logo}</span>
                    <span>{stock.name}</span>
                  </div>
                  <div className="stock-values">
                    <div>Total Shares</div>
                    <div className="stock-amount">{stock.value}</div>
                    <div className={`stock-change ${stock.trend === 'up' ? 'change-positive' : 'change-negative'}`}>
                      {stock.return}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className='chart-watchlist-container'>
              {/* Chart Section */}
          <div className="chart-container">
            <div className="chart-header">
              <div className="chart-header">
                <div className="stock-info">
                  <span>🍎</span>
                  <span className="stock-name">Apple inc</span>
                  <span className="stock-company">AAPL</span>
                </div>
                <div className="stock-amount">$150.70</div>
              </div>
              <div className="time-filters">
                <button className="time-filter">1 Day</button>
                <button className="time-filter active">1 Week</button>
                <button className="time-filter">1 Month</button>
                <button className="time-filter">3 Month</button>
                <button className="time-filter">6 Month</button>
                <button className="time-filter">1 Year</button>
                <button className="time-filter">5 Year</button>
                <button className="time-filter">All</button>
              </div>
            </div>
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


          {/* Watchlist */}
          <div className='watchlist'>
          <div className="watchlist-header">
            <h2 className="section-title">My watchlist</h2>
            <button className="text-2xl font-bold">+</button>
          </div>
          <div className='watchlist-content'>
            {watchlist.map((stock) => (
              <div key={stock.name} className="watchlist-item">
                <div className="watchlist-stock">
                  <div className="stock-icon">{stock.name[0]}</div>
                  <div className="stock-details">
                    <div className="stock-name">{stock.name}</div>
                    <div className="stock-company">{stock.company}</div>
                  </div>
                </div>
                <div className="stock-price">
                  <div className="stock-current">{stock.value}</div>
                  <div className={stock.change.startsWith('+') ? 'change-positive' : 'change-negative'}>
                    {stock.change}
                  </div>
                </div>
              </div>
            ))}
          </div>
          </div>
          
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDashboard;