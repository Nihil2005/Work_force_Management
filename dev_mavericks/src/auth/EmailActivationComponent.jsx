import React, { useState } from 'react';
import axios from 'axios';

const EmailActivationComponent = () => {
  const [activationCode, setActivationCode] = useState('');
  const [message, setMessage] = useState(null); 

  const handleChange = (e) => {
    setActivationCode(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://192.168.223.1:8000/activate-account/', { code: activationCode });
      console.log(response.data);
      setMessage({ type: 'success', content: 'Account activated. Proceed to login.' });
      
      setTimeout(() => {
        window.location.href = '/login'; 
      }, 2000);
    } catch (error) {
      console.error(error.response.data);
      setMessage({ type: 'error', content: error.response.data.error || 'Failed to activate account.' });
    }
  };

  return (
    <div className="flex justify-center items-center h-screen">
      <form onSubmit={handleSubmit} className="w-full max-w-sm">
        <h2 className="text-2xl mb-6 text-center font-bold">Email Activation</h2>
        {message && (
          <div className={`mb-4 ${message.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
            {message.content}
          </div>
        )}
        <div className="mb-4">
          <label htmlFor="activationCode" className="block text-gray-700 text-sm font-bold mb-2">Activation Code</label>
          <input type="text" id="activationCode" value={activationCode} onChange={handleChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
        </div>
        
        <div className="flex items-center justify-between">
          <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">Activate</button>
        </div>
      </form>
    </div>
  );
};

export default EmailActivationComponent;
