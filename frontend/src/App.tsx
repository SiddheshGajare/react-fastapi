import StockPrediction from "./components/StockPrediction.tsx";
import SignUpForm from '../src/SignUpForm';
import SignInPage from '../src/SignIn';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
function App() {
  return (
    <div className="p-6">
      <StockPrediction/>
    </div>
  );
}

export default App;
