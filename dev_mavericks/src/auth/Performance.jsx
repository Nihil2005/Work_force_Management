import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { IoArrowBackSharp } from "react-icons/io5";
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Performance = () => {
    const [performanceMetrics, setPerformanceMetrics] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                setError('Authentication required. Redirecting to login.');
                navigate('/login');
                return;
            }

            try {
                const response = await axios.get('http://192.168.223.1:8000/workers/me/performance-metrics/', {
                    headers: { Authorization: `Token ${token}` }
                });
                setPerformanceMetrics(response.data);
            } catch (err) {
                setError('Failed to fetch data.');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [navigate]);

    const performanceChartData = {
        labels: performanceMetrics.map(metric => new Date(metric.recorded_at).toLocaleDateString()),
        datasets: [{
            label: 'Performance Metrics',
            data: performanceMetrics.map(metric => metric.value),
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 2
        }]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false, 
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Performance Metrics',
            },
        },
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="error-message">{error}</div>;

    return (
        <div className="bg-white P-32 shadow-lg rounded-2xl p-6 sm:p-8 transition-all transform hover:-translate-y-1 hover:shadow-2xl">
             <button>
             <a href='/profile'><IoArrowBackSharp className='h-8 w-8' /></a>
        </button>
            <h3 className="text-xl sm:text-2xl font-bold mb-4">Performance</h3>
            <div className="w-full h-64 sm:h-96">
                <Bar data={performanceChartData} options={chartOptions} />
            </div>
        </div>
    );
};

export default Performance;
