import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { IoArrowBackSharp } from "react-icons/io5";
const Shifts = () => {
    const [workerData, setWorkerData] = useState(null);
    const [shiftData, setShiftData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const formatDate = (date) => format(date, 'MMMM d, yyyy');
    const parseDate = (date) => parse(date, 'MMMM d, yyyy', new Date());
    const startOfWeekFn = (date) => startOfWeek(date, { weekStartsOn: 0 });
    const getDayFn = (date) => getDay(date);

    const localizer = dateFnsLocalizer({
        format: formatDate,
        parse: parseDate,
        startOfWeek: startOfWeekFn,
        getDay: getDayFn,
        locales: { 'en-US': enUS },
    });

    useEffect(() => {
        fetchWorkerData();
    }, []);

    const fetchWorkerData = async () => {
        try {
            const token = localStorage.getItem('token');

            if (!token) {
                setError('Authentication required. Redirecting to login.');
                navigate('/login');
                return;
            }

            const [workerResponse, shiftResponse] = await Promise.all([
                axios.get('http://192.168.223.1:8000/workers/me/', { headers: { Authorization: `Token ${token}` } }),
                axios.get('http://192.168.223.1:8000/workers/me/shifts/', { headers: { Authorization: `Token ${token}` } }),
            ]);

            setWorkerData(workerResponse.data);
            setShiftData(shiftResponse.data.map(shift => {
                const startTime = new Date(shift.start_time);
                const endTime = new Date(shift.end_time);
                const allocatedDate = new Date(shift.allocated_date);

                
                if (isNaN(startTime) || isNaN(endTime) || isNaN(allocatedDate)) {
                    console.error('Invalid date values:', {
                        start_time: shift.start_time,
                        end_time: shift.end_time,
                        allocated_date: shift.allocated_date,
                    });
                    return null; 
                }

                return {
                    id: shift.id,
                    title: `Shift: ${startTime.toLocaleTimeString()} - ${endTime.toLocaleTimeString()} on ${formatDate(allocatedDate)}`,
                    start: startTime,
                    end: endTime,
                    className: 'bg-blue-500 text-white rounded-lg p-2 shadow-md',
                };
            }).filter(shift => shift !== null)); 

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

    const eventStyleGetter = (event) => {
        const backgroundColor = event.className.includes('bg-')
            ? event.className
            : 'bg-green-500';
        return {
            className: backgroundColor,
        };
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div className="p-6 bg-white shadow-lg rounded-2xl transition-transform transform hover:-translate-y-1 hover:shadow-2xl">
             <button>
             <a href='/profile'><IoArrowBackSharp className='h-8 w-8' /></a>
        </button>
            <h3 className="text-xl font-bold mb-4">Shifts</h3>
            <Calendar
                localizer={localizer}
                events={shiftData}
                startAccessor="start"
                endAccessor="end"
                style={{ height: 600 }}
                selectable
                onSelectEvent={(event) => alert(event.title)}
                onSelectSlot={(slotInfo) => alert(`Selected slot: ${formatDate(slotInfo.start)} to ${formatDate(slotInfo.end)}`)}
                eventPropGetter={eventStyleGetter}
            />
        </div>
    );
};

export default Shifts;
