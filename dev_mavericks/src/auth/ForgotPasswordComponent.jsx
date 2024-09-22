import React, { useState } from 'react';
import axios from 'axios';

const ForgotPasswordComponent = () => {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState(null);
  const [step, setStep] = useState(1); 
  const [resetSuccess, setResetSuccess] = useState(false); 

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'email') setEmail(value);
    else if (name === 'code') setCode(value);
    else if (name === 'newPassword') setNewPassword(value);
  };

  const handleSubmitEmail = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://192.168.223.1:8000/password-reset/', { email });
      console.log(response.data);
      setMessage({ type: 'success', content: response.data.success });
      setStep(2); 
    } catch (error) {
      console.error(error.response ? error.response.data : error.message);
      setMessage({ type: 'error', content: error.response ? error.response.data.error : error.message });
    }
  };

  const handleSubmitCodePassword = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://192.168.223.1:8000/password-reset/verify/', { code, new_password: newPassword });
      console.log(response.data);
      setMessage({ type: 'success', content: response.data.success });
      setResetSuccess(true); 
    } catch (error) {
      console.error(error.response ? error.response.data : error.message);
      setMessage({ type: 'error', content: error.response ? error.response.data.error : error.message });
    }
  };

 
  if (resetSuccess) {
    setTimeout(() => {
      window.location.href = '/login';
    }, 2000);
  }

  return (
    <div className="flex justify-center items-center h-screen">
      <form onSubmit={step === 1 ? handleSubmitEmail : handleSubmitCodePassword} className="w-full max-w-sm">
        <h2 className="text-2xl mb-6 text-center font-bold">Forgot Password</h2>
        {message && (
          <div className={`mb-4 ${message.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
            {message.content}
          </div>
        )}
        {step === 1 && (
          <div className="mb-4">
            <label htmlFor="email" className="block text-white text-sm font-bold mb-2">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={email}
              onChange={handleChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-white leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
        )}
        {step === 2 && (
          <>
            <div className="mb-4">
              <label htmlFor="code" className="block text-white text-sm font-bold mb-2">Verification Code</label>
              <input
                type="text"
                id="code"
                name="code"
                value={code}
                onChange={handleChange}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            <div className="mb-4">
              <label htmlFor="newPassword" className="block text-gray-700 text-sm font-bold mb-2">New Password</label>
              <input
                type="password"
                id="newPassword"
                name="newPassword"
                value={newPassword}
                onChange={handleChange}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
          </>
        )}
        <div className="flex items-center justify-between">
          <button type="submit" className="bg-green-400 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
            {step === 1 ? 'Submit' : 'Reset Password'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ForgotPasswordComponent;
