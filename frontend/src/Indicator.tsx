import { useState } from "react";
import axios from "axios";
import { Bell, Mail, ChevronDown, Home, LayoutDashboard, Wallet, Newspaper, BarChart2, Users, Settings, Phone, ChevronUp } from 'lucide-react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import './Indicator.css';

function StockAnalyzer() {
  const [company, setCompany] = useState("");
  const [ticker, setTicker] = useState("");
  const [ownedStock, setOwnedStock] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

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
                <div className="nav-item" onClick={() => navigate('/StockAnalyzer')} >
                  <Wallet className="nav-icon" />
                  <span>Wallet</span>
                </div>
                <div className="nav-item"  onClick={() => navigate('/news')}>
                  <Newspaper className="nav-icon" />
                  <span>News</span>
                </div>

                <div>
                      <div 
                        className="nav-item"
                        onClick={() => setIsOpen(!isOpen)}
                      >
                        <BarChart2 className="nav-icon" />
                        <span>Stock & fund</span>
                        {(!isOpen) ?
                        <ChevronDown className={`ml-auto transition-transform duration-200 ${isOpen ? 'rotate-180' : 'rotate-45'}`} /> :
                        <ChevronUp className={`ml-auto transition-transform duration-200 ${isOpen ? 'rotate-180' : 'rotate-45'}`} />}
                      </div>
                      
                      {isOpen && (
                        <>
                          <div className="nav-sub-item">Stock</div>
                          <div className="nav-sub-item">Cryptocurrency</div>
                          <div className="nav-sub-item">Mutual Fund</div>
                          <div className="nav-sub-item">Gold</div>
                        </>
                      )}
                    </div>
              </div>
              
            </nav>
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

          </div>
        </div>
    <div className="indicator-main-container">
      <h1 className="text-xl font-bold">Stock Impact Predictor</h1>
      <input 
        type="text"
        placeholder="Company Name"
        className="inputbox1"
        value={company}
        onChange={(e) => setCompany(e.target.value)}
      />
      <input
        type="text"
        placeholder="Stock Ticker"
        className="inputbox2"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
      />
      <div className="checkbox-container">
        <input
          type="checkbox"
          checked={ownedStock}
          onChange={(e) => setOwnedStock(e.target.checked)}
        />
        <h5 className="label1">Do you own this stock?</h5>
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
    </div>
    </div>
  );
}

export default StockAnalyzer;