from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from .views import (


    AbsenceListCreateView,
    AbsenceRetrieveUpdateDestroyView,
    ClockInView,
    ClockOutView,
    GenerateCSVReport,
    GeneratePDFReport,
    LeaveRequestListCreateView,
    LeaveRequestRetrieveUpdateDestroyView,
    LeaveTypeListCreateView,
    LeaveTypeRetrieveUpdateDestroyView,
    WorkerListCreateView,
    WorkerRetrieveUpdateDestroyView,
    ShiftListCreateView,
    ShiftRetrieveUpdateDestroyView,
    AttendanceListCreateView,
    AttendanceRetrieveUpdateDestroyView,
    PerformanceMetricListCreateView,
    PerformanceMetricRetrieveUpdateDestroyView,
    WorkerAttendanceListView,
    WorkerShiftsListView,
    WorkerPerformanceMetricsListView,
    download_report,
    worker_analysis,
 


    

    
)

urlpatterns = [
    path('', views.Account.as_view(), name = 'accounts'),
    path('edit-details/', views.AccountChange.as_view(), name='edit-details'),
    path('login/', views.Login.as_view(),name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('activate-account/', views.AccountActivationView.as_view(), name='account-activation'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password-reset/verify/', views.PasswordResetVerifyView.as_view(), name='password-reset-verify'),
    path('email-change/', views.EmailChangeView.as_view(), name='email-change'),
    path('email-change/verify/', views.EmailChangeVerifyView.as_view(), name='email-change-verify'),



     # Worker URLs
    path('workers/', WorkerListCreateView.as_view(), name='worker-list-create'),
    path('workers/<int:pk>/', WorkerRetrieveUpdateDestroyView.as_view(), name='worker-detail'),
    
    # Shift URLs
    path('shifts/', ShiftListCreateView.as_view(), name='shift-list-create'),
    path('shifts/<int:pk>/', ShiftRetrieveUpdateDestroyView.as_view(), name='shift-detail'),
    
    # Attendance URLs
    path('attendance/', AttendanceListCreateView.as_view(), name='attendance-list-create'),
    path('attendance/<int:pk>/', AttendanceRetrieveUpdateDestroyView.as_view(), name='attendance-detail'),
    
    # Performance Metric URLs
    path('performance-metrics/', PerformanceMetricListCreateView.as_view(), name='performance-metric-list-create'),
    path('performance-metrics/<int:pk>/', PerformanceMetricRetrieveUpdateDestroyView.as_view(), name='performance-metric-detail'),



    path('workers/<int:worker_id>/attendance/', WorkerAttendanceListView.as_view(), name='worker-attendance-list'),
    path('workers/<int:worker_id>/shifts/', WorkerShiftsListView.as_view(), name='worker-shifts-list'),
    path('workers/<int:worker_id>/performance-metrics/', WorkerPerformanceMetricsListView.as_view(), name='worker-performance-metrics-list'),


    path('workers/me/', views.WorkerDetailView.as_view(), name='worker-detail-me'),
    path('workers/me/attendance/', WorkerAttendanceListView.as_view(), name='worker-attendance-list'),
    path('workers/me/shifts/', WorkerShiftsListView.as_view(), name='worker-shifts-list'),
    path('workers/me/performance-metrics/', WorkerPerformanceMetricsListView.as_view(), name='worker-performance-metrics-list'),

    path('workers/me/report/pdf/', GeneratePDFReport.as_view(), name='generate_pdf_report'),
    path('workers/me/report/csv/', GenerateCSVReport.as_view(), name='generate_csv_report'),
   
    path('download-report/', download_report, name='download_report'),

    path('clock-in/', ClockInView.as_view(), name='clock_in'),
    path('clock-out/', ClockOutView.as_view(), name='clock_out'),


    path('worker-analysis/', worker_analysis, name='worker_analysis'),










    path('leave_requests/', LeaveRequestListCreateView.as_view(), name='leave-request-list-create'),
    path('leave_requests/<int:pk>/', LeaveRequestRetrieveUpdateDestroyView.as_view(), name='leave-request-detail'),

    path('absences/', AbsenceListCreateView.as_view(), name='absence-list-create'),
    path('absences/<int:pk>/', AbsenceRetrieveUpdateDestroyView.as_view(), name='absence-detail'),

    path('leave_types/', LeaveTypeListCreateView.as_view(), name='leave-type-list-create'),
    path('leave_types/<int:pk>/', LeaveTypeRetrieveUpdateDestroyView.as_view(), name='leave-type-detail'),


    




   



    
]

urlpatterns = format_suffix_patterns(urlpatterns)