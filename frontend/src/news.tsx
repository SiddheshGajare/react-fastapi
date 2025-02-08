import { useState } from "react";
import { Bell, Mail, ChevronDown, Home, LayoutDashboard, Wallet, Newspaper, BarChart2, Users, Settings, Phone, ChevronUp } from 'lucide-react';
import './components/StockDashboard.css';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
const date = new Date();
const formattedDate = date.toLocaleDateString('en-CA', { month: '2-digit', day: '2-digit',year: 'numeric' });


interface StockDataPoint {
  date: string;
  price: number;
  type: 'historical' | 'prediction';
}

function NewspaperSec() {
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

  const handleBlur = () => {
    if (ticker && !ticker.endsWith(".NS")) {
      setTicker(ticker + ".NS"); // Save with ".NS" on blur
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
                <div className="nav-item">
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
              <button onClick={fetchPredictions} className="search-button">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-search" viewBox="0 0 16 16">
                  <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/>
                </svg>
              </button>
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

        </div>
      </div>
    </div>
  );
}

export default NewspaperSec;