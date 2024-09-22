import csv
from datetime import datetime
import os
import random
import string
import io
import csv
from venv import logger
from django.shortcuts import get_object_or_404, render
from django.views import View
from flask_login import login_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from reportlab.lib.units import inch 
from django.http import HttpResponse
import logging
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .serializers import AbsenceSerializer, LeaveRequestSerializer, LeaveTypeSerializer, WorkerSerializer, ShiftSerializer, AttendanceSerializer, PerformanceMetricSerializer
from rest_framework import generics
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django.contrib.auth import login, logout, get_user_model
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Absence, AccountActivation, LeaveRequest, LeaveType,Worker,Shift,PerformanceMetric,Attendance
from .serializers import (ProfileSerializer, PasswordResetVerifySerializer,
                          EmailChangeSerializer, EmailChangeVerifySerializer,
                          PasswordChangeSerializer, PasswordResetSerializer,
                          ProfileChangeSerializer, LoginSerializer,
                          SignupSerializer, AccountActivationSerializer)
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view, permission_classes
from myapp import serializers
class Account(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get(self, request, format=None):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

class AccountChange(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileChangeSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = request.user

            if 'first_name' in serializer.validated_data:
                user.first_name = serializer.validated_data['first_name']
            if 'last_name' in serializer.validated_data:
                user.last_name = serializer.validated_data['last_name']

            user.save()

            content = {'success': _('User information changed.')}
            return Response(content, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            token, created = Token.objects.get_or_create(user=user)

            if user is not None and user.email_confirmed:
                login(request, user)
                response_data = {
                    'user_id': user.id,
                    'success': _('User authenticated.'),
                    'token': token.key 
                    
                }
                
                
                response = Response(response_data, status=status.HTTP_200_OK)
                response['Authorization'] = f'Token {token.key}'
                return response
            elif user is not None and not user.email_confirmed:
                return Response({'error': _('Email not confirmed. Please activate your account.')}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': _('Invalid email or password.')}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Signup(APIView):
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

         
            if get_user_model().objects.filter(email=email).exists():
                return Response({'error': _('Email is already registered.')}, status=status.HTTP_400_BAD_REQUEST)

         
            user = serializer.save()
            
            
            Token.objects.create(user=user)

          
            email_confirmation = AccountActivation(user=user)
            confirmation_code = email_confirmation.create_confirmation()

            subject = _('Activate Your Account')
            message = f'Your account activation code is: {confirmation_code}'
            from_email = 'Your Email'  
            to_email = [email]

            try:
               
                send_mail(subject, message, from_email, to_email, fail_silently=True)
            except Exception as e:
              
                return Response({'error': _('Failed to send activation email.')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'success': _('User signed up successfully.')}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountActivationView(APIView):
    serializer_class = AccountActivationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            activation_code = serializer.validated_data.get('code')  

            email_confirmation = AccountActivation.objects.filter(activation_code=activation_code).first()

            if email_confirmation:
                if email_confirmation.verify_confirmation(activation_code):
                    return Response({'success': _('Account Activated. Proceed To Log in')}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': _('Invalid confirmation code.')}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': _('Invalid confirmation code.')}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)
        return Response({'success': 'User logged out successfully.'}, status=status.HTTP_200_OK)

# 6-digit code
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

class PasswordResetView(APIView):
    serializer_class = PasswordResetSerializer
    
    def post(self, request, format=None):
        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                
                user = get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                return Response({'error': _('User with this email does not exist.')}, status=status.HTTP_400_BAD_REQUEST)

          
            code = generate_verification_code()

      
            user.email_verification_code = code
            user.save()

         
            subject = _('Reset Your Password')
            message = f'Your verification code is: {code}'
            from_email = 'Your Email'  
            to_email = [email]

            try:
          
                send_mail(subject, message, from_email, to_email, fail_silently=True)
            except Exception as e:
             
                return Response({'error': _('Failed to send reset email.')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'success': _('Verification code sent successfully.')}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetVerifyView(APIView):
    serializer_class = PasswordResetVerifySerializer
    
    def post(self, request, format=None):
        serializer = PasswordResetVerifySerializer(data=request.data)

        if serializer.is_valid():
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']

            try:
                user = get_user_model().objects.get(email_verification_code=code)
            except get_user_model().DoesNotExist:
                return Response({'error': _('Invalid verification code.')}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.email_verification_code = None
            user.save()

            return Response({'success': _('Password reset successfully.')}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailChangeView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmailChangeSerializer

    def send_email_change_confirmation(self, user):
        code = get_random_string(length=6)
        user.email_verification_code = code
        user.save()

        subject = 'Confirm Email Change'
        message = f'Your verification code is: {code}'
        from_email = 'Your Email'  
        to_email = user.email


        send_mail(subject, message, from_email, [to_email], fail_silently=True)

    def post(self, request, format=None):
        serializer = EmailChangeSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            new_email = serializer.validated_data['email']

         
            if new_email != user.email:
                raise PermissionDenied("Provided email doesn't match the logged-in user's email.")

          
            self.send_email_change_confirmation(user)

            return Response({'success': 'Email change request sent successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailChangeVerifyView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmailChangeVerifySerializer
    
    def post(self, request, format=None):
        serializer = EmailChangeVerifySerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            code = serializer.validated_data['code']
            new_email = serializer.validated_data['new_email']

            if user.email_verification_code == code:
                user.email = new_email
                user.email_verification_code = None  
                user.save()
                return Response({'success': 'Email changed successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid or expired verification code.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = PasswordChangeSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

        
            if not user.check_password(old_password):
                return Response({'error': _('Current password is incorrect.')}, status=status.HTTP_400_BAD_REQUEST)

        
            user.set_password(new_password)
            user.save()

            
            return Response({'success': 'Password changed successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class WorkerListCreateView(generics.ListCreateAPIView):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer


class WorkerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer




class ShiftListCreateView(generics.ListCreateAPIView):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer


class ShiftRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer



class AttendanceListCreateView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class AttendanceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer



class PerformanceMetricListCreateView(generics.ListCreateAPIView):
    queryset = PerformanceMetric.objects.all()
    serializer_class = PerformanceMetricSerializer


class PerformanceMetricRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PerformanceMetric.objects.all()
    serializer_class = PerformanceMetricSerializer








class WorkerAttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        worker_id = self.kwargs['worker_id']
        return Attendance.objects.filter(worker_id=worker_id)
    
class WorkerShiftsListView(generics.ListAPIView):
    serializer_class = ShiftSerializer

    def get_queryset(self):
        worker_id = self.kwargs['worker_id']
        return Shift.objects.filter(worker_id=worker_id)
    

class WorkerPerformanceMetricsListView(generics.ListAPIView):
    serializer_class = PerformanceMetricSerializer

    def get_queryset(self):
        worker_id = self.kwargs['worker_id']
        return PerformanceMetric.objects.filter(worker_id=worker_id)
    


class WorkerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            worker = Worker.objects.get(user=request.user)
            serializer = WorkerSerializer(worker)
            return Response(serializer.data)
        except Worker.DoesNotExist:
            return Response({"detail": "Worker not found."}, status=404)





class WorkerAttendanceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            worker = Worker.objects.get(user=request.user)
            attendances = Attendance.objects.filter(worker=worker)
            serializer = AttendanceSerializer(attendances, many=True)
            return Response(serializer.data)
        except Worker.DoesNotExist:
            return Response({"detail": "Worker not found."}, status=404)

class WorkerShiftsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            worker = Worker.objects.get(user=request.user)
            shifts = Shift.objects.filter(worker=worker)
            serializer = ShiftSerializer(shifts, many=True)
            return Response(serializer.data)
        except Worker.DoesNotExist:
            return Response({"detail": "Worker not found."}, status=404)

class WorkerPerformanceMetricsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            worker = Worker.objects.get(user=request.user)
            metrics = PerformanceMetric.objects.filter(worker=worker)
            serializer = PerformanceMetricSerializer(metrics, many=True)
            return Response(serializer.data)
        except Worker.DoesNotExist:
            return Response({"detail": "Worker not found."}, status=404)


class GeneratePDFReport(View):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return HttpResponse("User ID is required", status=400)
        
        try:
            worker = Worker.objects.get(id=user_id)
        except Worker.DoesNotExist:
            return HttpResponse("Worker not found", status=404)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="worker_report.pdf"'
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.drawString(100, height - 100, "Worker Report")
        y = height - 140
        
        #  worker details
        p.drawString(100, y, f"Name: {worker.first_name} {worker.last_name}")
        y -= 20
        
        #  worker profile picture
        if worker.profile_picture:
            image_path = default_storage.path(worker.profile_picture.name)
            
            if os.path.exists(image_path):
                p.drawImage(image_path, 100, y - 50, width=1*inch, height=1*inch)
                y -= 70
            else:
                p.drawString(100, y, "Image not found")
                y -= 20
        else:
            p.drawString(100, y, "No Image Available")
            y -= 20
        
        p.showPage()
        p.save()
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response.write(pdf)
        return response


class GenerateCSVReport(View):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return HttpResponse("User ID is required", status=400)
        
        try:
            worker = Worker.objects.get(id=user_id)
        except Worker.DoesNotExist:
            return HttpResponse("Worker not found", status=404)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="worker_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Phone Number', 'Address'])
        
        writer.writerow([
            worker.first_name,
            worker.last_name,
            worker.email,
            worker.phone_number,
            worker.address,
        ])
        
        return response


from .pdf_report import generate_pdf_report

def download_report(request):
    return generate_pdf_report(request)



class ClockInView(APIView):
    def post(self, request, *args, **kwargs):
        worker_id = request.data.get('worker_id')
        shift_id = request.data.get('shift_id')
        location = request.data.get('location')

        if not worker_id or not shift_id or not location:
            return Response({"detail": "Missing required fields: worker_id, shift_id, and location are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            worker = Worker.objects.get(id=worker_id)
            shift = Shift.objects.get(id=shift_id)
        except Worker.DoesNotExist:
            return Response({"detail": "Worker not found."}, status=status.HTTP_404_NOT_FOUND)
        except Shift.DoesNotExist:
            return Response({"detail": "Shift not found."}, status=status.HTTP_404_NOT_FOUND)

        if Attendance.objects.filter(worker=worker, clock_out_time__isnull=True).exists():
            return Response({"detail": "Worker is already clocked in."}, status=status.HTTP_400_BAD_REQUEST)

        attendance = Attendance(
            worker=worker,
            shift=shift,
            clock_in_time=timezone.now(),
            clock_in_location=location
        )
        attendance.save()

        return Response({"detail": "Clocked in successfully."}, status=status.HTTP_200_OK)

class ClockOutView(APIView):
    def post(self, request, *args, **kwargs):
        worker_id = request.data.get('worker_id')
        location = request.data.get('location')

        if not worker_id or not location:
            return Response({"detail": "Missing required fields: worker_id and location are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            worker = Worker.objects.get(id=worker_id)
          
            attendance = Attendance.objects.filter(worker=worker, clock_out_time__isnull=True).latest('clock_in_time')
            attendance.clock_out_time = timezone.now()
            attendance.clock_out_location = location
            attendance.save()
        except Worker.DoesNotExist:
            return Response({"detail": "Worker not found."}, status=status.HTTP_404_NOT_FOUND)
        except Attendance.DoesNotExist:
            return Response({"detail": "No clock-in record found for this worker."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Clocked out successfully."}, status=status.HTTP_200_OK)

class LeaveTypeListCreateView(generics.ListCreateAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

class LeaveTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer

class LeaveRequestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer

class AbsenceListCreateView(generics.ListCreateAPIView):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer

class AbsenceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer





def worker_analysis(request):
    analysis_data = []
    
    workers = Worker.objects.all()
    
    for worker in workers:
        #  attendance data
        attendance_records = Attendance.objects.filter(worker=worker)
        attendance_days = attendance_records.count()
        total_hours_worked = sum(record.hours_worked() for record in attendance_records)
        
        #  performance metrics
        performance_metrics = PerformanceMetric.objects.filter(worker=worker)
        total_performance_value = sum(metric.value for metric in performance_metrics)
        average_performance_value = total_performance_value / performance_metrics.count() if performance_metrics.exists() else 0
        
        analysis_data.append({
            'worker': {
                'first_name': worker.first_name,
                'last_name': worker.last_name,
            },
            'attendance_days': attendance_days,
            'total_hours_worked': total_hours_worked,
            'total_performance_value': total_performance_value,
            'average_performance_value': average_performance_value,
        })

    context = {
        'analysis_data': analysis_data,
    }

    return render(request, 'worker_analysis.html', context)