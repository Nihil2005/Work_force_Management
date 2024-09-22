import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Replace with your Django API URL

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    }
});

export const login = (data) => api.post('/login/', data);
export const signup = (data) => api.post('/signup/', data);
export const logout = () => api.post('/logout/');

export const getWorkers = () => api.get('/workers/');
export const getWorker = (id) => api.get(`/workers/${id}/`);
export const createWorker = (data) => api.post('/workers/', data);
export const updateWorker = (id, data) => api.put(`/workers/${id}/`, data);
export const deleteWorker = (id) => api.delete(`/workers/${id}/`);

export const getShifts = () => api.get('/shifts/');
export const getShift = (id) => api.get(`/shifts/${id}/`);
export const createShift = (data) => api.post('/shifts/', data);
export const updateShift = (id, data) => api.put(`/shifts/${id}/`, data);
export const deleteShift = (id) => api.delete(`/shifts/${id}/`);

export const getAttendance = () => api.get('/attendance/');
export const getAttendanceDetail = (id) => api.get(`/attendance/${id}/`);
export const createAttendance = (data) => api.post('/attendance/', data);
export const updateAttendance = (id, data) => api.put(`/attendance/${id}/`, data);
export const deleteAttendance = (id) => api.delete(`/attendance/${id}/`);

export const getPerformanceMetrics = () => api.get('/performance-metrics/');
export const getPerformanceMetric = (id) => api.get(`/performance-metrics/${id}/`);
export const createPerformanceMetric = (data) => api.post('/performance-metrics/', data);
export const updatePerformanceMetric = (id, data) => api.put(`/performance-metrics/${id}/`, data);
export const deletePerformanceMetric = (id) => api.delete(`/performance-metrics/${id}/`);
