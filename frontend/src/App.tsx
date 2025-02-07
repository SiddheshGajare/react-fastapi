import StockPrediction from "./components/StockPrediction.tsx";
import SignUpForm from '../src/SignUpForm';
import SignInPage from '../src/SignIn';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
function App() {
  return (
    /*<div className="p-6">
      <StockPrediction/>
    </div>*/
    <Router>
      <Routes>
        <Route path="/" element={<SignUpForm />} />
        <Route path="/about" element={<SignInPage />} />
        <Route path="/dashBoard" element={<StockPrediction />} />
      </Routes>
    </Router>
  );
}

export default App;
