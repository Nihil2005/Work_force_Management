from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from .models import Shift, Attendance, PerformanceMetric, Worker,Event

def send_notification(worker, subject, template_name, context):
    from_email = 'felk@gmail.com' 
    to_email = worker.email
    message = render_to_string(template_name, context)

    try:
        email = EmailMessage(subject, message, from_email, [to_email])
        email.content_subtype = 'html' 
        email.send(fail_silently=False)
        print(f'Email sent successfully to {to_email}')
    except Exception as e:
        print(f'Failed to send email: {e}')

@receiver(post_save, sender=Shift)
def notify_worker_of_shift_change(sender, instance, created, **kwargs):
    print(f'Shift post_save signal received for Shift object ({instance.id}) with created={created}')
    
    worker = instance.worker
    if created: 
        subject = _('Your Shift Has Been Created')
        context = {
            'worker': worker,
            'shift': instance
        }
        send_notification(worker, subject, 'shift_report.html', context)
    else: 
        subject = _('Your Shift Has Been Updated')
        context = {
            'worker': worker,
            'shift': instance
        }
        send_notification(worker, subject, 'shift_update.html', context)

@receiver(post_save, sender=Attendance)
def notify_worker_of_attendance_update(sender, instance, created, **kwargs):
    print(f'Attendance post_save signal received for {instance} with created={created}')
    
    worker = instance.worker
    if created:
        subject = _('Your Attendance Record Has Been Created')
        context = {
            'worker': worker,
            'attendance': instance
        }
    else:
        subject = _('Your Attendance Record Has Been Updated')
        context = {
            'worker': worker,
            'attendance': instance
        }
    
    send_notification(worker, subject, 'attendance_update.html', context)

@receiver(post_save, sender=PerformanceMetric)
def notify_worker_of_performance_update(sender, instance, created, **kwargs):
    print(f'PerformanceMetric post_save signal received for {instance} with created={created}')
    
    worker = instance.worker
    if created:
        subject = _('Your Performance Metric Has Been Created')
        context = {
            'worker': worker,
            'performance_metric': instance
        }
    else:
        subject = _('Your Performance Metric Has Been Updated')
        context = {
            'worker': worker,
            'performance_metric': instance
        }
    
    send_notification(worker, subject, 'performance_update.html', context)

@receiver(post_save, sender=Attendance)
def calculate_performance_metric(sender, instance, created, **kwargs):
  
    shift = instance.shift
    if not shift:
        return

   
    late_minutes = max((instance.clock_in_time - shift.start_time).total_seconds() / 60, 0)
    punctuality = max(100 - late_minutes, 0)

   
    scheduled_duration = (shift.end_time - shift.start_time).total_seconds() / 3600
    actual_duration = (instance.clock_out_time - instance.clock_in_time).total_seconds() / 3600 if instance.clock_out_time else 0
    work_hours_accuracy = min((actual_duration / scheduled_duration) * 100, 100) if scheduled_duration else 0

    PerformanceMetric.objects.update_or_create(
        worker=instance.worker,
        shift=instance.shift,
        metric_name="Punctuality",
        defaults={'value': punctuality}
    )
    PerformanceMetric.objects.update_or_create(
        worker=instance.worker,
        shift=instance.shift,
        metric_name="Work Hours Accuracy",
        defaults={'value': work_hours_accuracy}
    )


def send_event_notification(worker, subject, template_name, context, image_path=None):
    from_email = 'your_verified_email@example.com'
    to_email = worker.email
    message = render_to_string(template_name, context)

    try:
        email = EmailMessage(subject, message, from_email, [to_email])
        email.content_subtype = 'html'
        if image_path:
            email.attach_file(image_path)  
        email.send(fail_silently=False)
        print(f'Email sent successfully to {to_email}')
    except Exception as e:
        print(f'Failed to send email: {e}')

@receiver(post_save, sender=Event)
def notify_workers_of_event(sender, instance, created, **kwargs):
    if created:
        subject = f"New Event: {instance.title}"
        context = {
            'title': instance.title,
            'description': instance.description,
            'event_date': instance.event_date,
        }
        
    
        workers = Worker.objects.all()
        for worker in workers:
            send_event_notification(
                worker,
                subject,
                'event_notification.html',
                context,
                image_path=instance.image.path if instance.image else None 
            )