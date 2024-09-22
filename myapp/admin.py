# admin.py
from django.db.models import Avg
import csv
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import Absence, CustomUserProfile, LeaveRequest, LeaveType, Salary, Worker, Attendance, Shift, PerformanceMetric, Department, Event
from .pdf_report import generate_pdf_report
from io import StringIO
from django.conf import settings
import pandas as pd

from django.db.models import Avg
import os
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.urls import path

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'email_confirmed', 'email_verification_code')
    list_filter = ('is_staff', 'is_active', 'email_confirmed')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'email_confirmed', 'email_verification_code')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'is_staff', 'email_confirmed')}),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.register(CustomUserProfile, CustomUserAdmin)


from django.db.models import Count

from django.db.models import Sum 





@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('profile_picture_tag', 'first_name', 'last_name', 'total_hours_worked', 'average_performance_score')
    actions = ['generate_pdf', 'export_as_csv', 'export_as_pdf']

    def profile_picture_tag(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_picture.url)
        return "No Image"
    profile_picture_tag.short_description = 'Profile Picture'

    # total hours work
    def total_hours_worked(self, obj):
        attendances = obj.attendance_set.all()
        total_hours = sum([attendance.hours_worked() for attendance in attendances])
        return round(total_hours, 2)
    total_hours_worked.short_description = 'Total Hours Worked'

    # average performance 
    def average_performance_score(self, obj):
        metrics = obj.performancemetric_set.all()
        if metrics.exists():
            avg_score = metrics.aggregate(Avg('value'))['value__avg'] 
            return round(avg_score, 2)
        return "No Metrics"
    average_performance_score.short_description = 'Average Performance Score'

    def generate_pdf(self, request, queryset):
        return generate_pdf_report(queryset)
    generate_pdf.short_description = "Generate PDF for selected Workers"

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=workers.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)

        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    def export_as_pdf(self, request, queryset):
        workers = queryset
        html = render_to_string('worker_pdf.html', {'workers': workers})

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=workers.pdf'

        pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')

        return response

    def link_callback(self, uri, rel):
        if uri.startswith(settings.MEDIA_URL):
            path = uri[len(settings.MEDIA_URL):]
            return os.path.join(settings.MEDIA_ROOT, path)
        return uri

    export_as_csv.short_description = "Export selected workers as CSV"
    export_as_pdf.short_description = "Export selected workers as PDF"



class ShiftAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if change:
            print(f'Updating Shift: {obj.id}') 
        super().save_model(request, obj, form, change)

admin.site.register(Shift, ShiftAdmin)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'formatted_image', 'is_active', 'worker_list')
    search_fields = ('title', 'description')
    list_filter = ('event_date', 'is_active')
    ordering = ('-event_date',)
    readonly_fields = ('formatted_image',)

    def formatted_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px; height: auto;" />', obj.image.url)
        return "No Image"
    formatted_image.short_description = "Event Image"

    def worker_list(self, obj):
        return ", ".join(worker.get_full_name() for worker in obj.workers.all())
    worker_list.short_description = 'Assigned Workers'

admin.site.register(Department)
admin.site.register(Attendance)
admin.site.register(PerformanceMetric)

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('worker', 'basic_pay', 'allowances', 'deductions', 'total_salary', 'date_generated')
    actions = ['generate_salary_slips', 'export_salary_slips_as_pdf', 'send_salary_slips_email']
    
    def generate_salary_slips(self, request, queryset):
        """Custom action to generate salary slips for the selected workers"""
        for salary in queryset:
    
            salary.save()
        self.message_user(request, "Salary slips have been generated.")
    generate_salary_slips.short_description = "Generate Salary Slips"
    
    def export_salary_slips_as_pdf(self, request, queryset):
        """Export selected salary slips as a PDF file."""
        salaries = queryset
        html = render_to_string('salary_slip_pdf.html', {'salaries': salaries})
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=salary_slips.pdf'
        
        pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')

        return response

    def send_salary_slips_email(self, request, queryset):
        """Send salary slips via email to the selected workers."""
        for salary in queryset:
            worker = salary.worker
            salary_data = [{
                'worker': {
                    'first_name': worker.first_name,
                    'last_name': worker.last_name,
                    'position': worker.position,
                    'department': worker.department,
                    'email': worker.email
                },
                'date_generated': salary.date_generated.strftime('%Y-%m-%d'),
                'basic_pay': salary.basic_pay,
                'allowances': salary.allowances,
                'deductions': salary.deductions,
                'total_salary': salary.total_salary
            }]
            
            html_content = render_to_string('salary_slip_pdf.html', {'salaries': salary_data})
            
            email = EmailMessage(
                subject='Your Salary Slip',
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[worker.email],
            )
            email.content_subtype = 'html'
            try:
                email.send()
                self.message_user(request, f"Salary slip sent to {worker.email}.")
            except Exception as e:
                self.message_user(request, f"Error sending salary slip to {worker.email}: {e}")

    def link_callback(self, uri, rel):
        """Callback for resolving relative URIs in PDF rendering."""
        import os

        if uri.startswith(settings.MEDIA_URL):
            path = uri[len(settings.MEDIA_URL):]
            return os.path.join(settings.MEDIA_ROOT, path)
        return uri
    
    send_salary_slips_email.short_description = "Send Salary Slips via Email"
    export_salary_slips_as_pdf.short_description = "Export Salary Slips as PDF"







