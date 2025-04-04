import StockPrediction from "./components/StockPrediction.tsx";
import SignUpForm from '../src/SignUpForm';
import SignInPage from '../src/SignIn';
import NewspaperSec from "./news.tsx";
import SeggetionSec from "./suggetion.tsx";
import HomePage from "./HomePage.tsx"
import StockAnalyzer from "./Indicator.tsx";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
function App() {
  return (
    // <div className="p-6">
    //   <StockAnalyzer/>
    // </div>
    <Router>
      <Routes>
        <Route path="/about" element={<SignUpForm />} />
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<SignInPage />} />
        <Route path="/dashBoard" element={<StockPrediction />} />
        <Route path="/news" element={<NewspaperSec />} />
        <Route path="/suggetion" element={<SeggetionSec />} />
        <Route path="/StockAnalyzer" element={<StockAnalyzer />} />      
      </Routes>
    </Router>
  );
}

export default App;
