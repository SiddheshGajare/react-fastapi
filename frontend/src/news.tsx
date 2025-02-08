import { useState } from "react";
import { Bell, Mail, ChevronDown, Home, LayoutDashboard, Wallet, Newspaper, BarChart2, Users, Settings, Phone, ChevronUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import topUpImage from './assets/photo/topUp.png';
import './newImpact.css'
function NewspaperSec() {
  const navigate = useNavigate();
  const [ticker, setTicker] = useState("");
  const [impact, setImpact] = useState<number | null>(null);
  const [reasons, setReasons] = useState<{ sentiment: string; reason: string }[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  // ✅ Function to fetch news impact from FastAPI
  const fetchNewsImpact = async () => {
    if (!ticker) return;
    try {
      const response = await fetch(`http://localhost:8000/news-impact/${ticker}`);
      const data = await response.json();
      setImpact(data.impact);
      setReasons(data.reasons.map((r: [number, string]) => ({
        sentiment: r[0] > 0 ? "Positive" : r[0] < 0 ? "Negative" : "Neutral",
        reason: r[1]
      })));
    } catch (error) {
      console.error("Error fetching news impact:", error);
    }
  };

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
                <div className="nav-item" onClick={() => navigate('/')}>
                  <Home className="nav-icon" />
                  <span>Home</span>
                </div>
                <div className="nav-item" onClick={() => navigate('/dashboard')}>
                  <LayoutDashboard className="nav-icon" />
                  <span>Dashboard</span>
                </div>
                <div className="nav-item">
                  <Wallet className="nav-icon" />
                  <span>Wallet</span>
                </div>
                <div className="nav-item" onClick={() => navigate('/news')}>
                  <Newspaper className="nav-icon" />
                  <span>News</span>
                </div>

                <div>
                  <div className="nav-item" onClick={() => setIsOpen(!isOpen)}>
                    <BarChart2 className="nav-icon" />
                    <span>Stock & Fund</span>
                    {isOpen ? <ChevronUp className="ml-auto" /> : <ChevronDown className="ml-auto" />}
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
          <img src={topUpImage} alt="Search Icon" className="search-image" />
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

          {/* News Sentiment Impact Section */}
          <div className="news-impact-section">
            <h2>News Sentiment Impact</h2>
            <input 
              type="text" 
              value={ticker} 
              onChange={(e) => setTicker(e.target.value)} 
              placeholder="Enter stock ticker..."
              className="search-input"
            />
            <button onClick={fetchNewsImpact} className="search-button">Check News Impact</button>
            
            {impact !== null && (
              <div className="impact-results">
                <h3>Predicted News Impact: {impact}%</h3>
                <ul>
                  {reasons.map((r, index) => (
                    <div className="impact-list" key={index}>
                      <strong>[{r.sentiment}]</strong> {r.reason}
                    </div>
                  ))}
                </ul>
              </div>
            )}
          </div>
          
        </div>
      </div>
    </div>
  );
}

export default NewspaperSec;
