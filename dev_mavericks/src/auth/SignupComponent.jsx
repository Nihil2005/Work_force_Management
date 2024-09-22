import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; 
import EmailActivationComponent from './EmailActivationComponent'; 

const SignupComponent = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
  });
  const [message, setMessage] = useState(null); 
  const navigate = useNavigate(); 

  const handleChange = (e) => {
    if (e.target.type === 'file') {
      setFormData({ ...formData, [e.target.name]: e.target.files[0] });
    } else {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formDataToSend = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        formDataToSend.append(key, value);
      });
      const response = await axios.post('http://192.168.223.1:8000/signup/', formDataToSend);
      setMessage({ type: 'success', content: 'User signed up successfully.' });

      navigate('/activate');

   
      setFormData({
        email: '',
        password: '',
        first_name: '',
        last_name: '',
      });
    } catch (error) {
      setMessage({ type: 'error', content: error.response.data.detail });
    }
  };

  return (
    <div className="relative flex justify-center items-center h-screen overflow-hidden">
      <video 
        className="absolute inset-0 w-full h-full object-cover"
        src='WhatsApp Video 2024-09-21 at 8.48.23 AM.mp4'
        autoPlay
        loop
        muted
      />
      <form onSubmit={handleSubmit} className="relative z-10 w-full max-w-md rounded-lg shadow-md p-8">
        <h2 className="text-2xl text-red-400 mb-6 text-center font-bold">Sign Up</h2>
        {message && (
          <div className={`mb-4 ${message.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
            {message.content}
          </div>
        )}
        <div className="mb-4">
          <label htmlFor="email" className="block text-white text-sm font-bold mb-2">Email</label>
          <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required />
        </div>
        <div className="mb-4">
          <label htmlFor="password" className="block text-white text-sm font-bold mb-2">Password</label>
          <input type="password" id="password" name="password" value={formData.password} onChange={handleChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required />
        </div>
        <div className="mb-4">
          <label htmlFor="firstName" className="block text-white text-sm font-bold mb-2">First Name</label>
          <input type="text" id="firstName" name="first_name" value={formData.first_name} onChange={handleChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required />
        </div>
        <div className="mb-4">
          <label htmlFor="lastName" className="block text-white text-sm font-bold mb-2">Last Name</label>
          <input type="text" id="lastName" name="last_name" value={formData.last_name} onChange={handleChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required />
        </div>
        <div className="flex justify-center">
          <button type="submit" className="bg-red-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-2xl focus:outline-none focus:shadow-outline">Sign Up</button>
        </div>
      </form>
    </div>
  );
};

export default SignupComponent;
