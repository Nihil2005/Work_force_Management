import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import {
  FaHome,
  FaUser,
  FaCalendarAlt,
  FaClock,
  FaChartLine,
  FaSignOutAlt,
  FaFileCsv,
  FaFilePdf,
  FaBars,
  FaTimes,
} from 'react-icons/fa';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const ProfileComponent = () => {
  const [workerData, setWorkerData] = useState(null);
  const [attendanceData, setAttendanceData] = useState([]);
  const [shiftData, setShiftData] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentLocation, setCurrentLocation] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchWorkerData();
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          console.error('Error getting location:', error);
          setError('Unable to retrieve location.');
        }
      );
    } else {
      setError('Geolocation is not supported by this browser.');
    }
  }, []);

  const fetchWorkerData = async () => {
    try {
      const token = localStorage.getItem('token');

      if (!token) {
        setError('Authentication required. Redirecting to login.');
        navigate('/login');
        return;
      }

      const [workerResponse, attendanceResponse, shiftResponse, metricsResponse] =
        await Promise.all([
          axios.get('http://192.168.223.1:8000/workers/me/', {
            headers: { Authorization: `Token ${token}` },
          }),
          axios.get('http://192.168.223.1:8000/workers/me/attendance/', {
            headers: { Authorization: `Token ${token}` },
          }),
          axios.get('http://192.168.223.1:8000/workers/me/shifts/', {
            headers: { Authorization: `Token ${token}` },
          }),
          axios.get('http://192.168.223.1:8000/workers/me/performance-metrics/', {
            headers: { Authorization: `Token ${token}` },
          }),
        ]);

      setWorkerData(workerResponse.data);
      setAttendanceData(attendanceResponse.data);
      setShiftData(shiftResponse.data);
      setPerformanceMetrics(metricsResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error.message);
      handleFetchError(error);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchError = (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        setError('Unauthorized access. Redirecting to login.');
        navigate('/login');
      } else {
        setError('An error occurred while fetching data.');
      }
    } else if (error.request) {
      setError('No response from the server.');
    } else {
      setError('Request error: ' + error.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setSuccessMessage('You have been logged out.');
    navigate('/login');
  };

  const toggleSidebar = () => {
    setSidebarOpen((prevState) => !prevState);
  };

  const downloadFile = async (type) => {
    const token = localStorage.getItem('token');
    const userId = workerData ? workerData.id : null;

    if (!token || !userId) {
      setError('Authentication or user data required. Redirecting to login.');
      navigate('/login');
      return;
    }

    try {
      const response = await axios.get(
        `http://192.168.223.1:8000/workers/me/report/${type}/?user_id=${userId}`,
        {
          headers: { Authorization: `Token ${token}` },
          responseType: 'blob',
        }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `user_report.${type}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error(`Error downloading ${type}:`, error);
      setError(`Failed to download ${type}.`);
    }
  };

  const handleClockIn = async () => {
    const token = localStorage.getItem('token');
    const workerId = workerData ? workerData.id : null;

    if (!token || !workerId || !currentLocation) {
      setError('Authentication, user ID, or location data required.');
      return;
    }

    try {
      await axios.post(
        'http://192.168.223.1:8000/clock-in/',
        {
          worker_id: workerId,
          shift_id: shiftData[0]?.id,
          location: `${currentLocation.latitude},${currentLocation.longitude}`,
        },
        { headers: { Authorization: `Token ${token}` } }
      );

      setSuccessMessage('Clocked in successfully');
    } catch (error) {
      console.error('Error clocking in:', error);
      if (error.response) {
        setError(`Failed to clock in: ${error.response.data.detail || 'Unknown error'}`);
      } else {
        setError('Failed to clock in.');
      }
    }
  };

  const handleClockOut = async () => {
    const token = localStorage.getItem('token');
    const workerId = workerData ? workerData.id : null;

    if (!token || !workerId || !currentLocation) {
      setError('Authentication, user ID, or location data required.');
      return;
    }

    try {
      await axios.post(
        'http://192.168.223.1:8000/clock-out/',
        {
          worker_id: workerId,
          location: `${currentLocation.latitude},${currentLocation.longitude}`,
        },
        { headers: { Authorization: `Token ${token}` } }
      );

      setSuccessMessage('Clocked out successfully');
    } catch (error) {
      console.error('Error clocking out:', error);
      if (error.response) {
        setError(`Failed to clock out: ${error.response.data.detail || 'Unknown error'}`);
      } else {
        setError('Failed to clock out.');
      }
    }
  };

  const attendanceChartData = {
    labels: attendanceData.map((item) => new Date(item.clock_in_time).toLocaleDateString()),
    datasets: [
      {
        label: 'Attendance Hours',
        data: attendanceData.map(
          (item) => (new Date(item.clock_out_time) - new Date(item.clock_in_time)) / (1000 * 60 * 60)
        ),
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        fill: true,
      },
    ],
  };

  const performanceChartData = {
    labels: performanceMetrics.map((metric) => new Date(metric.recorded_at).toLocaleDateString()),
    datasets: [
      {
        label: 'Performance Metrics',
        data: performanceMetrics.map((metric) => metric.value),
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2,
        fill: true,
      },
    ],
  };

  const shiftsChartData = {
    labels: shiftData.map((shift) => new Date(shift.start_time).toLocaleDateString()),
    datasets: [
      {
        label: 'Shift Hours',
        data: shiftData.map(
          (shift) => (new Date(shift.end_time) - new Date(shift.start_time)) / (1000 * 60 * 60)
        ),
        backgroundColor: 'rgba(255, 159, 64, 0.2)',
        borderColor: 'rgba(255, 159, 64, 1)',
        borderWidth: 2,
        fill: true,
      },
    ],
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="loader ease-linear rounded-full border-8 border-t-8 border-gray-200 h-64 w-64"></div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className={`bg-gray-800 text-white w-64 ${sidebarOpen ? 'block' : 'hidden'} md:block`}>
        <div className="flex items-center justify-center mt-8">
          <img src="/lox.png" alt="Company Logo" className="w-20 h-20" />
        </div>
        <nav className="mt-10 space-y-2">
          <Link to="/profile" className="flex items-center px-6 py-2 hover:bg-gray-700 rounded">
            <FaUser className="mr-3" />
            Profile
          </Link>
          <Link to="/profile/attendence" className="flex items-center px-6 py-2 hover:bg-gray-700 rounded">
            <FaCalendarAlt className="mr-3" />
            Attendance
          </Link>
          <Link to="/profile/shifts" className="flex items-center px-6 py-2 hover:bg-gray-700 rounded">
            <FaClock className="mr-3" />
            Shifts
          </Link>
          <Link to="/profile/performanace" className="flex items-center px-6 py-2 hover:bg-gray-700 rounded">
            <FaChartLine className="mr-3" />
            Performance
          </Link>
          <button
            onClick={handleLogout}
            className="flex items-center px-6 py-2 hover:bg-gray-700 rounded"
          >
            <FaSignOutAlt className="mr-3" />
            Logout
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <header className="flex items-center justify-between px-6 py-4 bg-white shadow-md">
          <h1 className="text-2xl font-semibold text-gray-700">Worker Dashboard</h1>
          <button onClick={toggleSidebar} className="md:hidden text-gray-600">
            {sidebarOpen ? <FaTimes /> : <FaBars />}
          </button>
        </header>

        <main className="flex-1 p-6">
          {/* Notifications */}
          <div className="space-y-4">
            {error && <Notification message={error} type="error" />}
            {successMessage && <Notification message={successMessage} type="success" />}
          </div>

          {/* Profile Card */}
          <div className="bg-white shadow-md rounded-lg p-6 mt-4">
            <div className="flex flex-col sm:flex-row items-center">
            <img
  src={workerData?.profile_picture ? `http://192.168.223.1:8000/${workerData.profile_picture}` : '/default-avatar.png'}
  alt="Profile"
  className="w-24 h-24 rounded-full"
/>
              <div className="ml-4">
                <h2 className="text-xl font-semibold">{workerData?.first_name} {workerData?.last_name}</h2>
                <p className="text-gray-500">{workerData?.email}</p>
              </div>
            </div>
            <div className="mt-6 flex space-x-4">
              <Button onClick={handleClockIn} label="Clock In" />
              <Button onClick={handleClockOut} label="Clock Out" />
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
            <ChartCard title="Attendance" data={attendanceChartData} />
            <ChartCard title="Performance" data={performanceChartData} />
            <ChartCard title="Shifts" data={shiftsChartData} />
          </div>

          {/* Download Reports */}
          <div className="mt-6">
            <h3 className="text-lg font-semibold">Download Reports</h3>
            <div className="space-x-4">
              <Button onClick={() => downloadFile('csv')} label="Download CSV" />
              <Button onClick={() => downloadFile('pdf')} label="Download PDF" />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

const Button = ({ onClick, label }) => (
  <button
    onClick={onClick}
    className="bg-red-400 text-white py-2 px-4 rounded hover:bg-red-700 transition duration-200"
  >
    {label}
  </button>
);

const ChartCard = ({ title, data }) => (
  <div className="bg-white shadow-md rounded-lg p-4">
    <h4 className="font-semibold mb-2">{title}</h4>
    {title === 'Attendance' ? (
      <Line data={data} />
    ) : (
      <Bar data={data} />
    )}
  </div>
);

const Notification = ({ message, type }) => (
  <div className={`p-4 mb-4 text-white rounded ${type === 'error' ? 'bg-red-500' : 'bg-green-500'}`}>
    {message}
  </div>
);

export default ProfileComponent;
