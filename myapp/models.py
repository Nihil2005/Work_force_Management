from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext as _
from django.utils import timezone

from random import randint

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUserProfile(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False, verbose_name=_('Email Confirmed'))
    email_verification_code = models.CharField(max_length=6, null=True, blank=True, verbose_name=_('Verification code'))

    username = models.CharField(max_length=30)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

class AccountActivation(models.Model):
    user = models.OneToOneField(CustomUserProfile, on_delete=models.CASCADE, related_name='email_confirmation')
    activation_code = models.CharField(max_length=6, null=True, blank=True, verbose_name=_('Activation Code'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('Creation Time'))

    def __str__(self):
        return f"Email Confirmation for {self.user.email}"

    def create_confirmation(self):
        code = str(randint(100000, 999999)) 
        self.activation_code = code
        self.save()
        return code

    def verify_confirmation(self, code):
        if self.activation_code == code:
            self.user.email_confirmed = True
            self.user.save()
            self.delete()  
            return True

    
        return False
    




class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name






class Worker(models.Model):
    user = models.OneToOneField(CustomUserProfile, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    date_of_birth = models.DateField()
    position = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    qualifications = models.TextField()
    date_joined = models.DateField(auto_now_add=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"





class Salary(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    date_generated = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_salary = self.basic_pay + self.allowances - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.worker} - {self.total_salary}"







class Shift(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 

    def __str__(self):
        return f"{self.worker} {self.start_time} - {self.end_time}"

        
class Attendance(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    clock_in_time = models.DateTimeField()
    clock_out_time = models.DateTimeField(null=True, blank=True)
    clock_in_location = models.CharField(max_length=255, blank=True, null=True)  # Location as a string
    clock_out_location = models.CharField(max_length=255, blank=True, null=True)

    def hours_worked(self):
        """Calculate hours worked based on clock-in and clock-out times."""
        if self.clock_out_time:
            return (self.clock_out_time - self.clock_in_time).total_seconds() / 3600
        return 0

    def __str__(self):
        
        return f"Attendance for {self.worker.first_name} {self.worker.last_name} on {self.shift.start_time}"

class PerformanceMetric(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    metric_name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=5, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.metric_name} for {self.worker.first_name} {self.worker.last_name}: {self.value}"

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    workers = models.ManyToManyField(Worker, related_name='events', blank=True)  # Relation to Worker  # Use ImageField for uploads

    def __str__(self):
        return self.title
    





class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.worker} - {self.leave_type} ({self.start_date} to {self.end_date})"


class Absence(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.TextField()
    is_excused = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.worker} - {self.date} ({'Excused' if self.is_excused else 'Unexcused'})"