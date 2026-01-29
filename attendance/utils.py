import csv
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import io

def export_attendance_csv(session):
    """Generate CSV export of attendance for a session."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{session.id}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Email', 'Status', 'Remarks', 'Recorded At'])
    
    attendances = session.attendances.all().select_related('student')
    for att in attendances:
        writer.writerow([
            att.student.student_id,
            f"{att.student.first_name} {att.student.last_name}",
            att.student.email,
            att.status.capitalize(),
            att.remarks,
            att.recorded_at.strftime('%Y-%m-%d %H:%M:%S') if att.recorded_at else ''
        ])
    
    return response

def get_attendance_statistics(session):
    """Calculate attendance statistics for a session."""
    attendances = session.attendances.all()
    total = attendances.count()
    
    if total == 0:
        return {
            'total': 0,
            'present': 0,
            'absent': 0,
            'late': 0,
            'excused': 0,
            'present_pct': 0,
            'absent_pct': 0,
            'late_pct': 0,
            'excused_pct': 0,
        }
    
    stats = {
        'total': total,
        'present': attendances.filter(status='present').count(),
        'absent': attendances.filter(status='absent').count(),
        'late': attendances.filter(status='late').count(),
        'excused': attendances.filter(status='excused').count(),
    }
    
    stats['present_pct'] = round((stats['present'] / total * 100), 1)
    stats['absent_pct'] = round((stats['absent'] / total * 100), 1)
    stats['late_pct'] = round((stats['late'] / total * 100), 1)
    stats['excused_pct'] = round((stats['excused'] / total * 100), 1)
    
    return stats

def get_student_absence_count(student):
    """Get number of absences for a student."""
    return student.attendances.filter(status='absent').count()


# Phase 2 Analytics Functions

def get_course_analytics(course):
    """Get comprehensive analytics for a course."""
    from .models import AttendanceSession, Attendance
    
    sessions = course.sessions.all()
    total_sessions = sessions.count()
    
    if total_sessions == 0:
        return {
            'total_sessions': 0,
            'average_attendance': 0,
            'total_students': course.students.count(),
            'enrollment_percentage': 0,
        }
    
    total_attendance_records = Attendance.objects.filter(session__course=course).count()
    present_count = Attendance.objects.filter(session__course=course, status='present').count()
    
    attendance_pct = round((present_count / total_attendance_records * 100), 1) if total_attendance_records > 0 else 0
    
    return {
        'total_sessions': total_sessions,
        'average_attendance': attendance_pct,
        'total_students': course.students.count(),
        'enrollment_percentage': course.get_enrollment_percentage(),
    }


def get_student_course_analytics(student, course):
    """Get student's attendance analytics for a specific course."""
    from .models import AttendanceSession, Attendance
    
    sessions = course.sessions.all()
    total_sessions = sessions.count()
    
    if total_sessions == 0:
        return {
            'total_sessions': 0,
            'present': 0,
            'absent': 0,
            'late': 0,
            'excused': 0,
            'attendance_rate': 0,
        }
    
    attendances = Attendance.objects.filter(session__course=course, student=student)
    
    return {
        'total_sessions': total_sessions,
        'present': attendances.filter(status='present').count(),
        'absent': attendances.filter(status='absent').count(),
        'late': attendances.filter(status='late').count(),
        'excused': attendances.filter(status='excused').count(),
        'attendance_rate': round((attendances.filter(status='present').count() / total_sessions * 100), 1),
    }


def get_attendance_trends(course, days=30):
    """Get attendance trends over the last N days."""
    from .models import AttendanceSession, Attendance
    
    cutoff_date = timezone.now().date() - timedelta(days=days)
    sessions = course.sessions.filter(date__gte=cutoff_date).order_by('date')
    
    trends = []
    for session in sessions:
        stats = get_attendance_statistics(session)
        trends.append({
            'date': session.date,
            'session': session,
            'stats': stats,
        })
    
    return trends


def import_students_from_csv(file_content, course):
    """Import students from CSV file to a course.
    
    Expected CSV columns: student_id, first_name, last_name, email, (optional) phone, department, major
    Returns: (successful_count, error_list)
    """
    from .models import Student
    
    csv_file = io.StringIO(file_content.decode('utf-8'))
    reader = csv.DictReader(csv_file)
    
    successful = 0
    errors = []
    
    for idx, row in enumerate(reader, 1):
        try:
            student_id = row.get('student_id', '').strip()
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()
            email = row.get('email', '').strip()
            
            if not all([student_id, first_name, last_name, email]):
                errors.append(f"Row {idx}: Missing required fields")
                continue
            
            # Get or create student
            student, created = Student.objects.get_or_create(
                student_id=student_id,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': row.get('phone', ''),
                    'department': row.get('department', ''),
                    'major': row.get('major', ''),
                }
            )
            
            # Add to course if not already enrolled
            if not course.students.filter(id=student.id).exists():
                course.students.add(student)
            
            successful += 1
        except Exception as e:
            errors.append(f"Row {idx}: {str(e)}")
    
    return successful, errors


# Phase 3: Detailed Reports

def generate_attendance_report(filters=None):
    """Generate detailed attendance report with optional filtering.
    
    Parameters:
    - filters (dict): Optional filters
      - course_id: Filter by course
      - student_id: Filter by student
      - date_from: Start date (YYYY-MM-DD)
      - date_to: End date (YYYY-MM-DD)
      - status: Filter by status (present, absent, late, excused)
    
    Returns: List of dicts with attendance details
    """
    from .models import Attendance
    
    query = Attendance.objects.select_related('student', 'session', 'session__course')
    
    if filters:
        if filters.get('course_id'):
            query = query.filter(session__course_id=filters['course_id'])
        if filters.get('student_id'):
            query = query.filter(student_id=filters['student_id'])
        if filters.get('date_from'):
            query = query.filter(session__date__gte=filters['date_from'])
        if filters.get('date_to'):
            query = query.filter(session__date__lte=filters['date_to'])
        if filters.get('status'):
            query = query.filter(status=filters['status'])
    
    report_data = []
    for att in query.order_by('session__date', 'student__last_name'):
        report_data.append({
            'student_id': att.student.student_id,
            'student_name': f"{att.student.first_name} {att.student.last_name}",
            'email': att.student.email,
            'course_code': att.session.course.code,
            'course_name': att.session.course.name,
            'session_date': att.session.date,
            'session_time': f"{att.session.start_time.strftime('%H:%M')} - {att.session.end_time.strftime('%H:%M')}",
            'status': att.status,
            'remarks': att.remarks,
            'checkin_time': att.checkin_time,
            'recorded_at': att.recorded_at,
        })
    
    return report_data


def generate_student_attendance_report(student):
    """Generate comprehensive attendance report for a single student."""
    from .models import Attendance
    
    attendances = student.attendances.select_related('session', 'session__course').order_by('-session__date')
    
    courses_data = {}
    for att in attendances:
        course_id = att.session.course.id
        if course_id not in courses_data:
            courses_data[course_id] = {
                'course': att.session.course,
                'total_sessions': 0,
                'present': 0,
                'absent': 0,
                'late': 0,
                'excused': 0,
                'attendance_rate': 0,
                'sessions': [],
            }
        
        courses_data[course_id]['total_sessions'] += 1
        courses_data[course_id]['sessions'].append({
            'date': att.session.date,
            'time': f"{att.session.start_time.strftime('%H:%M')} - {att.session.end_time.strftime('%H:%M')}",
            'status': att.status,
            'remarks': att.remarks,
        })
        
        if att.status == 'present':
            courses_data[course_id]['present'] += 1
        elif att.status == 'absent':
            courses_data[course_id]['absent'] += 1
        elif att.status == 'late':
            courses_data[course_id]['late'] += 1
        elif att.status == 'excused':
            courses_data[course_id]['excused'] += 1
    
    # Calculate rates
    for course_data in courses_data.values():
        total = course_data['total_sessions']
        if total > 0:
            course_data['attendance_rate'] = round(((course_data['present'] + course_data['late']) / total * 100), 1)
    
    return {
        'student': student,
        'courses': courses_data,
        'total_sessions': sum(c['total_sessions'] for c in courses_data.values()),
        'total_present': sum(c['present'] for c in courses_data.values()),
        'total_absent': sum(c['absent'] for c in courses_data.values()),
        'total_late': sum(c['late'] for c in courses_data.values()),
        'total_excused': sum(c['excused'] for c in courses_data.values()),
    }


def generate_course_attendance_report(course, date_from=None, date_to=None):
    """Generate detailed attendance report for a course."""
    from .models import Attendance
    
    sessions = course.sessions.all()
    if date_from:
        sessions = sessions.filter(date__gte=date_from)
    if date_to:
        sessions = sessions.filter(date__lte=date_to)
    
    report_data = []
    students_summary = {}
    
    for session in sessions.order_by('date'):
        session_stats = {
            'date': session.date,
            'time': f"{session.start_time.strftime('%H:%M')} - {session.end_time.strftime('%H:%M')}",
            'total_students': 0,
            'present': 0,
            'absent': 0,
            'late': 0,
            'excused': 0,
            'attendance_rate': 0,
            'students': [],
        }
        
        attendances = session.attendances.select_related('student').order_by('student__last_name')
        for att in attendances:
            student_key = att.student.id
            if student_key not in students_summary:
                students_summary[student_key] = {
                    'student': att.student,
                    'total': 0,
                    'present': 0,
                    'absent': 0,
                    'late': 0,
                    'excused': 0,
                }
            
            students_summary[student_key]['total'] += 1
            session_stats['total_students'] += 1
            
            session_stats['students'].append({
                'student_id': att.student.student_id,
                'name': f"{att.student.first_name} {att.student.last_name}",
                'status': att.status,
                'remarks': att.remarks,
            })
            
            if att.status == 'present':
                session_stats['present'] += 1
                students_summary[student_key]['present'] += 1
            elif att.status == 'absent':
                session_stats['absent'] += 1
                students_summary[student_key]['absent'] += 1
            elif att.status == 'late':
                session_stats['late'] += 1
                students_summary[student_key]['late'] += 1
            elif att.status == 'excused':
                session_stats['excused'] += 1
                students_summary[student_key]['excused'] += 1
        
        if session_stats['total_students'] > 0:
            session_stats['attendance_rate'] = round(
                ((session_stats['present'] + session_stats['late']) / session_stats['total_students'] * 100), 1
            )
        
        report_data.append(session_stats)
    
    # Calculate student summary rates
    for summary in students_summary.values():
        total = summary['total']
        if total > 0:
            summary['attendance_rate'] = round(((summary['present'] + summary['late']) / total * 100), 1)
    
    return {
        'course': course,
        'sessions': report_data,
        'students_summary': sorted(students_summary.values(), key=lambda x: x['student'].last_name),
        'date_range': {
            'from': date_from,
            'to': date_to,
        },
    }


def export_report_to_csv(report_data, report_type='general'):
    """Export report to CSV format.
    
    Parameters:
    - report_data: Report dict from report generation functions
    - report_type: 'general', 'student', or 'course'
    
    Returns: HttpResponse with CSV data
    """
    response = HttpResponse(content_type='text/csv')
    filename = f'attendance_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    if report_type == 'student':
        # Student-focused report
        student = report_data['student']
        writer.writerow(['Attendance Report for:', f"{student.first_name} {student.last_name}"])
        writer.writerow(['Student ID:', student.student_id])
        writer.writerow(['Email:', student.email])
        writer.writerow([])
        writer.writerow(['Course', 'Total Sessions', 'Present', 'Absent', 'Late', 'Excused', 'Attendance Rate'])
        
        for course_id, course_data in report_data['courses'].items():
            writer.writerow([
                course_data['course'].code,
                course_data['total_sessions'],
                course_data['present'],
                course_data['absent'],
                course_data['late'],
                course_data['excused'],
                f"{course_data['attendance_rate']}%",
            ])
        
        writer.writerow([])
        writer.writerow(['Summary', '', '', '', '', ''])
        writer.writerow(['Total Sessions', report_data['total_sessions']])
        writer.writerow(['Total Present', report_data['total_present']])
        writer.writerow(['Total Absent', report_data['total_absent']])
        writer.writerow(['Total Late', report_data['total_late']])
        writer.writerow(['Total Excused', report_data['total_excused']])
    
    elif report_type == 'course':
        # Course-focused report
        course = report_data['course']
        writer.writerow(['Attendance Report for:', course.code, '-', course.name])
        if report_data['date_range']['from']:
            writer.writerow(['Date Range:', report_data['date_range']['from'], 'to', report_data['date_range']['to']])
        writer.writerow([])
        writer.writerow(['Date', 'Time', 'Total', 'Present', 'Absent', 'Late', 'Excused', 'Attendance Rate'])
        
        for session in report_data['sessions']:
            writer.writerow([
                session['date'],
                session['time'],
                session['total_students'],
                session['present'],
                session['absent'],
                session['late'],
                session['excused'],
                f"{session['attendance_rate']}%",
            ])
        
        writer.writerow([])
        writer.writerow(['Student Summary', '', '', '', '', ''])
        writer.writerow(['Name', 'Student ID', 'Total', 'Present', 'Absent', 'Late', 'Excused', 'Attendance Rate'])
        
        for summary in report_data['students_summary']:
            writer.writerow([
                f"{summary['student'].first_name} {summary['student'].last_name}",
                summary['student'].student_id,
                summary['total'],
                summary['present'],
                summary['absent'],
                summary['late'],
                summary['excused'],
                f"{summary['attendance_rate']}%",
            ])
    
    else:
        # General report
        writer.writerow(['Student ID', 'Name', 'Email', 'Course', 'Date', 'Time', 'Status', 'Remarks'])
        for record in report_data:
            writer.writerow([
                record['student_id'],
                record['student_name'],
                record['email'],
                f"{record['course_code']} - {record['course_name']}",
                record['session_date'],
                record['session_time'],
                record['status'],
                record['remarks'],
            ])
    
    return response


def export_report_to_pdf(report_data, report_type='general'):
    """Export report to PDF format.
    
    Note: Requires reportlab package. Install with: pip install reportlab
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.units import inch
    except ImportError:
        raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")
    
    response = HttpResponse(content_type='application/pdf')
    filename = f'attendance_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    if report_type == 'student':
        student = report_data['student']
        elements.append(Paragraph(f"Attendance Report: {student.first_name} {student.last_name}", styles['Title']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Student info
        info_data = [
            ['Student ID:', student.student_id],
            ['Email:', student.email],
        ]
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Course summary
        elements.append(Paragraph("Course Summary", styles['Heading2']))
        course_data = [['Course', 'Sessions', 'Present', 'Absent', 'Late', 'Excused', 'Rate']]
        for course_id, course_info in report_data['courses'].items():
            course_data.append([
                course_info['course'].code,
                str(course_info['total_sessions']),
                str(course_info['present']),
                str(course_info['absent']),
                str(course_info['late']),
                str(course_info['excused']),
                f"{course_info['attendance_rate']}%",
            ])
        
        course_table = Table(course_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch])
        course_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(course_table)
    
    elif report_type == 'course':
        course = report_data['course']
        elements.append(Paragraph(f"Attendance Report: {course.code} - {course.name}", styles['Title']))
        if report_data['date_range']['from']:
            elements.append(Paragraph(
                f"From {report_data['date_range']['from']} to {report_data['date_range']['to']}",
                styles['Normal']
            ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Session summary
        elements.append(Paragraph("Session Summary", styles['Heading2']))
        session_data = [['Date', 'Time', 'Total', 'Present', 'Absent', 'Late', 'Excused', 'Rate']]
        for session in report_data['sessions']:
            session_data.append([
                str(session['date']),
                session['time'],
                str(session['total_students']),
                str(session['present']),
                str(session['absent']),
                str(session['late']),
                str(session['excused']),
                f"{session['attendance_rate']}%",
            ])
        
        session_table = Table(session_data, colWidths=[1*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        session_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(session_table)
    
    doc.build(elements)
    return response
