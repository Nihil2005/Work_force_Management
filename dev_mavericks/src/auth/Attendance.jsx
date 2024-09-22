import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

import { IoArrowBackSharp } from "react-icons/io5";



const Attendance = () => {
  const [workerData, setWorkerData] = useState(null);
  const [attendanceData, setAttendanceData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchWorkerData();
    getGeolocation();
  }, []);

  const fetchWorkerData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Redirecting to login.');
        navigate('/login');
        return;
      }

      const [workerResponse, attendanceResponse] = await Promise.all([
        axios.get('http://192.168.223.1:8000/workers/me/', { headers: { Authorization: `Token ${token}` } }),
        axios.get('http://192.168.223.1:8000/workers/me/attendance/', { headers: { Authorization: `Token ${token}` } }),
      ]);

      setWorkerData(workerResponse.data);
      setAttendanceData(attendanceResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error.message);
      setError('Failed to fetch data.');
    } finally {
      setLoading(false);
    }
  };

  const getGeolocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => console.log(position),
        (error) => setError('Unable to retrieve location.')
      );
    } else {
      setError('Geolocation is not supported by this browser.');
    }
  };

  const attendanceChartData = {
    labels: attendanceData.map((item) => new Date(item.clock_in_time).toLocaleDateString()),
    datasets: [{
      label: 'Attendance Hours',
      data: attendanceData.map((item) => (new Date(item.clock_out_time) - new Date(item.clock_in_time)) / (1000 * 60 * 60)),
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 2
    }]
  };

  if (loading) return <div className="text-center py-6">Loading...</div>;
  if (error) return <div className="text-red-500 text-center py-6">{error}</div>;

  return (
    <div className="p-6">

        <button>
             <a href='/profile'><IoArrowBackSharp className='h-8 w-8' /></a>
        </button>
      <h2 className="text-2xl font-bold mb-4 text-center">Attendance Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white shadow-lg rounded-lg p-6 transition-all transform hover:-translate-y-1 hover:shadow-2xl">
          <h3 className="text-xl font-bold mb-4">Attendance Chart</h3>
          <div className="h-64">
            <Line data={attendanceChartData} options={{ responsive: true }} />
          </div>
        </div>
        
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">Attendance Details</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full border-collapse">
              <thead>
                <tr>
                  <th className="border-b-2 border-gray-200 px-4 py-2 text-left">Date</th>
                  <th className="border-b-2 border-gray-200 px-4 py-2 text-left">Clock In</th>
                  <th className="border-b-2 border-gray-200 px-4 py-2 text-left">Clock Out</th>
                  <th className="border-b-2 border-gray-200 px-4 py-2 text-left">Hours</th>
                </tr>
              </thead>
              <tbody>
                {attendanceData.map((item, index) => (
                  <tr key={index} className="hover:bg-gray-100 transition-colors">
                    <td className="border-b px-4 py-2">{new Date(item.clock_in_time).toLocaleDateString()}</td>
                    <td className="border-b px-4 py-2">{new Date(item.clock_in_time).toLocaleTimeString()}</td>
                    <td className="border-b px-4 py-2">{new Date(item.clock_out_time).toLocaleTimeString()}</td>
                    <td className="border-b px-4 py-2">
                      {((new Date(item.clock_out_time) - new Date(item.clock_in_time)) / (1000 * 60 * 60)).toFixed(2)} hrs
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Attendance;
