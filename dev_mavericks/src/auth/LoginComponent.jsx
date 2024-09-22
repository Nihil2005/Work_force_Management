import React, { useState } from 'react';
import axios from 'axios';
import ProfileComponent from './ProfileComponent'; 
import ForgotPasswordComponent from './ForgotPasswordComponent'; 

const LoginComponent = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [userData, setUserData] = useState(null);
  const [message, setMessage] = useState(null);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://192.168.223.1:8000/login/', formData);
      if (response && response.data && response.data.token && response.data.success) {
        const token = response.data.token;
        localStorage.setItem('token', token);
        setUserData(response.data);
        setMessage({ type: 'success', content: 'User authenticated.' });
      } else {
        throw new Error('Token not found in response');
      }
    } catch (error) {
      setMessage({ type: 'error', content: error.response ? error.response.data.error : error.message });
    } finally {
      setLoading(false);
    }
  };

  if (userData) {
    return <ProfileComponent userData={userData} />;
  }

  if (showForgotPassword) {
    return <ForgotPasswordComponent />;
  }

  return (
    <div className="relative flex justify-center items-center h-screen overflow-hidden">
      <video 
        className="absolute inset-0 w-full h-full object-cover"
        src='WhatsApp Video 2024-09-21 at 8.48.23 AM.mp4'
        autoPlay
        loop
        muted
      />
      <div className="relative z-10 w-full max-w-sm">
        <form onSubmit={handleSubmit}>
          <h2 className="text-2xl text-red-400 mb-6 text-center font-bold">Login</h2>
          {message && (
            <div className={`mb-4 ${message.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
              {message.content}
            </div>
          )}
          <div className="mb-4">
            <label htmlFor="email" className="block text-white text-sm font-bold mb-2">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-red-700 leading-tight focus:outline-none focus:shadow-outline"
              required 
            />
          </div>
          <div className="mb-4">
            <label htmlFor="password" className="block text-white text-sm font-bold mb-2">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-red-700 leading-tight focus:outline-none focus:shadow-outline"
              required 
            />
          </div>
          <div className="flex items-center justify-between">
            <button
              type="submit"
              className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-2xl focus:outline-none focus:shadow-outline"
              disabled={loading}
            >
              {loading ? 'Loading...' : 'Login'}
            </button>
            <button
              type="button"
              onClick={() => setShowForgotPassword(true)}
              className="text-sm text-white"
            >
              Forgot Password?
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginComponent;
