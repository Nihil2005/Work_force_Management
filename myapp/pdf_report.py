import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from django.http import HttpResponse
from .models import Attendance, Shift, PerformanceMetric, Worker
from django.conf import settings
import os

def generate_pie_chart(labels, sizes, title):
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax.axis('equal')  
    plt.title(title)

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def generate_bar_chart(x_data, y_data, x_label, y_label, title):
    fig, ax = plt.subplots()
    ax.bar(x_data, y_data, color=plt.cm.Paired.colors)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def generate_pdf_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="workforce_management_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    section_style = styles['Heading2']

    
    custom_style = ParagraphStyle(
        'CustomStyle',
        parent=normal_style,
        fontSize=12,
        textColor=colors.black,
        spaceAfter=12,
        spaceBefore=12
    )

    
    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=150, height=150)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("DevMavericks Workforce Management Report", title_style))
    elements.append(Spacer(1, 24))

    
    attendance_count = {}
    performance_metric_count = {}

    for worker in Worker.objects.all():
        for attendance in Attendance.objects.filter(worker=worker):
            attendance_count[worker] = attendance_count.get(worker, 0) + 1
        for metric in PerformanceMetric.objects.filter(worker=worker):
            performance_metric_count[worker] = performance_metric_count.get(worker, 0) + metric.value

    
    best_worker = max(performance_metric_count, key=performance_metric_count.get, default=None)
    poor_worker = min(performance_metric_count, key=performance_metric_count.get, default=None)

    
    labels = [f"{worker.first_name} {worker.last_name}" for worker in attendance_count.keys()]
    data = list(attendance_count.values())
    pie_chart_buffer = generate_pie_chart(labels, data, "Attendance Distribution")
    pie_chart_image = Image(pie_chart_buffer, width=400, height=300)
    pie_chart_image.hAlign = 'CENTER'
    elements.append(pie_chart_image)
    elements.append(Spacer(1, 24))

    
    workers = [f"{worker.first_name} {worker.last_name}" for worker in performance_metric_count.keys()]
    metric_values = list(performance_metric_count.values())
    performance_chart_buffer = generate_bar_chart(workers, metric_values, "Worker", "Performance Metric Value", "Worker Performance")
    performance_chart_image = Image(performance_chart_buffer, width=400, height=300)
    performance_chart_image.hAlign = 'CENTER'
    elements.append(performance_chart_image)
    elements.append(Spacer(1, 24))

    
    for worker in Worker.objects.all():
        elements.append(Paragraph(f"Details for {worker.first_name} {worker.last_name}", section_style))
        elements.append(Spacer(1, 12))

        if worker.profile_picture:
            profile_picture = Image(worker.profile_picture.path, width=100, height=100)
            profile_picture.hAlign = 'LEFT'
            elements.append(profile_picture)

        elements.append(Paragraph(f"Email: {worker.email}", custom_style))
        elements.append(Paragraph(f"Position: {worker.position}", custom_style))
        elements.append(Paragraph(f"Department: {worker.department.name if worker.department else 'N/A'}", custom_style))
        elements.append(Paragraph(f"Date of Birth: {worker.date_of_birth}", custom_style))
        elements.append(Paragraph(f"Address: {worker.address}", custom_style))
        elements.append(Spacer(1, 12))

        
        elements.append(Paragraph("Attendance Details", section_style))
        attendance_data = [["Shift", "Clock In", "Clock Out"]]
        for attendance in Attendance.objects.filter(worker=worker):
            attendance_data.append([
                f"{attendance.shift.start_time} - {attendance.shift.end_time}",
                attendance.clock_in_time.strftime("%Y-%m-%d %H:%M") if attendance.clock_in_time else "N/A",
                attendance.clock_out_time.strftime("%Y-%m-%d %H:%M") if attendance.clock_out_time else "N/A"
            ])
        attendance_table = Table(attendance_data)
        attendance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(attendance_table)
        elements.append(Spacer(1, 24))

        
        elements.append(Paragraph("Performance Metrics", section_style))
        performance_data = [["Metric", "Value", "Recorded At"]]
        for metric in PerformanceMetric.objects.filter(worker=worker):
            performance_data.append([
                metric.metric_name,
                metric.value,
                metric.recorded_at.strftime("%Y-%m-%d %H:%M") if metric.recorded_at else "N/A"
            ])
        performance_table = Table(performance_data)
        performance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(performance_table)
        elements.append(Spacer(1, 24))

    
    if best_worker:
        elements.append(Paragraph(f"<b>Best Worker:</b> {best_worker.first_name} {best_worker.last_name}", normal_style))
    if poor_worker:
        elements.append(Paragraph(f"<b>Poor Worker:</b> {poor_worker.first_name} {poor_worker.last_name}", normal_style))

    doc.build(elements)
    return response
