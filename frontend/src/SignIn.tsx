import React from 'react';
import './SignIn.css';
import investmentImage from './assets/photo/potosss.jpg';


const SignInPage = () => {
  const [formData, setFormData] = React.useState({
    name: '',
    email: '',
    password: '',
    birthDate: {
      day: '',
      month: '',
      year: ''
    },
    gender: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('birth')) {
      const dateField = name.split('_')[1];
      setFormData(prev => ({
        ...prev,
        birthDate: {
          ...prev.birthDate,
          [dateField]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  return (
    <div className="signup-container">
      <div className="main-content">
        {/* Left side content */}
        <div className="left-content">
          <h1>Trade Your Plan Not Emotion!</h1>
          <p>Join our community of investors and share your investment journey</p>
          <img src={investmentImage} alt="Investment illustration" />
        </div>

        {/* Right side form */}
        <div className="form-wrapper">
        <div className="form-container">
          <h2>Welcome back</h2>
          <p>Welcome back! Please enter your details.</p>
          <form onSubmit={handleSubmit}>
            <label htmlFor="email">Email</label>
            <div className="form-fields">
            <input 
              type="email" 
              id="email" 
              name="email"
              placeholder="Enter your email" 
              required 
              value={formData.email} 
              onChange={handleInputChange} 
            />
            
            <label htmlFor="password">Password</label>
            <input 
              type="password" 
              id="password" 
              name="password"
              placeholder="Password" 
              required 
              value={formData.password} 
              onChange={handleInputChange} 
            />
            </div>
            
            <a href="#" className="forgot-password">Forgot password</a>
            
            <button type="submit" className="submit-btn">Login</button>
            
            <button className="google-btn">
                  <svg viewBox="0 0 24 24" className="google-icon">
                    <path fill="#EA4335" d="M12 5.04c1.44 0 2.88.49 4.13 1.46l3.01-3.02C17.12 1.77 14.63.85 12 .85c-4.1 0-7.65 2.34-9.38 5.75l3.52 2.73c.84-2.51 3.18-4.29 5.86-4.29z"/>
                    <path fill="#34A853" d="M23.15 12.34c0-.81-.07-1.59-.21-2.34H12v4.42h6.29c-.27 1.44-1.09 2.66-2.32 3.48l3.36 2.61c1.96-1.82 3.09-4.49 3.09-7.67z"/>
                    <path fill="#FBBC05" d="M5.14 14.48c-.21-.63-.33-1.31-.33-2.01c0-.7.12-1.37.33-2.01l-3.52-2.73c-.72 1.44-1.12 3.06-1.12 4.74s.4 3.3 1.12 4.74l3.52-2.73z"/>
                    <path fill="#4285F4" d="M12 23.15c3.04 0 5.59-1.01 7.45-2.73l-3.36-2.61c-.93.62-2.12.99-4.09.99c-2.68 0-5.02-1.78-5.86-4.29l-3.52 2.73c1.73 3.41 5.28 5.75 9.38 5.75z"/>
                  </svg>
            </button>
          </form>
          <p>Don't have an account? <a href="#">Sign up for free</a></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignInPage;














