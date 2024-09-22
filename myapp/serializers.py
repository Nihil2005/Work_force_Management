from datetime import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'first_name', 'last_name')


class ProfileChangeSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if user:
                if not user.email_confirmed:
                    raise serializers.ValidationError(_('Email not confirmed. Please activate your account.'))

                data['user'] = user
                return data
            else:
                raise serializers.ValidationError(_('Invalid email or password.'))
        else:
            raise serializers.ValidationError(_('Must include "email" and "password".'))


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


class AccountActivationSerializer(serializers.Serializer):
    code = serializers.CharField()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    

class PasswordResetVerifySerializer(serializers.Serializer):
    code = serializers.CharField()
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, validators=[validate_password])


class EmailChangeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class EmailChangeVerifySerializer(serializers.Serializer):
    code = serializers.CharField()
    new_email = serializers.EmailField()


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, validators=[validate_password], style={'input_type': 'password'})





from .models import Absence, LeaveRequest, LeaveType, Worker, Shift, Attendance, PerformanceMetric

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

class ShiftSerializer(serializers.ModelSerializer):
    worker = WorkerSerializer(read_only=True)

    class Meta:
        model = Shift
        fields = '__all__'



class AttendanceSerializer(serializers.ModelSerializer):
    worker_id = serializers.PrimaryKeyRelatedField(queryset=Worker.objects.all(), source='worker', write_only=True)
    worker_name = serializers.StringRelatedField(source='worker', read_only=True)  

    class Meta:
        model = Attendance
        fields = ['id', 'worker_id', 'clock_in_time', 'clock_in_location', 'clock_out_time', 'clock_out_location', 'worker_name']

    def create(self, validated_data):
        
        return Attendance.objects.create(**validated_data)
    











class PerformanceMetricSerializer(serializers.ModelSerializer):
    worker = WorkerSerializer(read_only=True)

    class Meta:
        model = PerformanceMetric
        fields = '__all__'



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_attendance(request):
    worker = request.user.worker  
    shift_id = request.data.get('shift')
    clock_in_location = request.data.get('clock_in_location')
    
    if not shift_id:
        return Response({'error': 'Shift is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        shift = Shift.objects.get(id=shift_id)
    except Shift.DoesNotExist:
        return Response({'error': 'Invalid shift.'}, status=status.HTTP_400_BAD_REQUEST)
    
    attendance = Attendance.objects.create(
        worker=worker,
        shift=shift,
        clock_in_time=timezone.now(),  
        clock_in_location=clock_in_location
    )

    serializer = AttendanceSerializer(attendance)
    return Response(serializer.data, status=status.HTTP_201_CREATED)





class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'description']

class LeaveRequestSerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer()  
    worker = serializers.StringRelatedField() 

    class Meta:
        model = LeaveRequest
        fields = ['id', 'worker', 'leave_type', 'start_date', 'end_date', 'reason', 'status', 'created_at', 'updated_at']

class AbsenceSerializer(serializers.ModelSerializer):
    worker = serializers.StringRelatedField() 

    class Meta:
        model = Absence
        fields = ['id', 'worker', 'date', 'reason', 'is_excused', 'created_at']





class LeaveRequestListCreateView(generics.ListCreateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer

    def perform_create(self, serializer):
        serializer.save(worker=self.request.user.worker)

class LeaveRequestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer