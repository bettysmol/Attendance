
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Avg
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import timedelta
import csv
from .models import Student, Course, AttendanceSession, Attendance, UserProfile, RecurringSession, StudentImportLog
from .forms import (
    UserRegistrationForm, CustomLoginForm, ProfileUpdateForm,
    StudentForm, CourseForm, AttendanceSessionForm, RecurringSessionForm, StudentImportForm
)
from .utils import (
    export_attendance_csv, get_attendance_statistics, get_student_absence_count,
    get_course_analytics, get_student_course_analytics, get_attendance_trends, import_students_from_csv,
    generate_attendance_report, generate_student_attendance_report, generate_course_attendance_report,
    export_report_to_csv, export_report_to_pdf
)

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def manual_attendance(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    students = session.course.students.all()
    # Prepare attendance info for each student
    for student in students:
        attendance = Attendance.objects.filter(session=session, student=student).first()
        student.attendance_status = attendance.status if attendance else 'absent'
        student.attendance_remarks = attendance.remarks if attendance else ''
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}', 'absent')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            Attendance.objects.update_or_create(
                session=session,
                student=student,
                defaults={'status': status, 'remarks': remarks}
            )
        messages.success(request, 'Attendance updated successfully!')
        return redirect('session_detail', session_id=session.id)
    context = {'session': session, 'students': students}
    return render(request, 'attendance/manual_attendance.html', context)

@login_required
def my_sessions(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Only students can access this page.')
        return redirect('dashboard')
    student = request.user.student
    now = timezone.now()
    sessions = AttendanceSession.objects.filter(
        course__in=student.courses.all(),
        date=now.date(),
    ).order_by('start_time')
    session_list = []
    for session in sessions:
        start_dt = timezone.make_aware(timezone.datetime.combine(session.date, session.start_time))
        end_dt = timezone.make_aware(timezone.datetime.combine(session.date, session.end_time))
        is_open = start_dt <= now <= end_dt
        checked_in = Attendance.objects.filter(session=session, student=student, status='present').exists()
        session.is_open = is_open
        session.checked_in = checked_in
        session_list.append(session)
    context = {'sessions': session_list}
    return render(request, 'attendance/my_sessions.html', context)
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Avg
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Student, Course, AttendanceSession, Attendance, UserProfile
from .forms import (
    UserRegistrationForm, CustomLoginForm, ProfileUpdateForm,
    StudentForm, CourseForm, AttendanceSessionForm
)

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def session_create(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = AttendanceSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.course = course
            session.save()
            messages.success(request, 'Session created successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = AttendanceSessionForm(initial={'course': course})
        form.fields['course'].widget = forms.HiddenInput()
    context = {'form': form, 'course': course}
    return render(request, 'attendance/session_form.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Avg
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Student, Course, AttendanceSession, Attendance, UserProfile
from .forms import (
    UserRegistrationForm, CustomLoginForm, ProfileUpdateForm,
    StudentForm, CourseForm, AttendanceSessionForm
)

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def mark_student_present(request, session_id, student_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    student = get_object_or_404(Student, id=student_id)
    # Only allow if student is enrolled in the course
    if not session.course.students.filter(id=student.id).exists():
        messages.error(request, 'Student is not enrolled in this course.')
        return redirect('session_detail', session_id=session.id)
    Attendance.objects.update_or_create(
        session=session,
        student=student,
        defaults={'status': 'present'}
    )
    messages.success(request, f"Marked {student.first_name} {student.last_name} as present.")
    return redirect('session_detail', session_id=session.id)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Avg
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Student, Course, AttendanceSession, Attendance, UserProfile
from .forms import (
    UserRegistrationForm, CustomLoginForm, ProfileUpdateForm,
    StudentForm, CourseForm, AttendanceSessionForm
)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    context = {'form': form}
    return render(request, 'attendance/auth/register.html', context)

@login_required
def welcome_view(request):
    return render(request, 'attendance/welcome.html')

@login_required
def help_view(request):
    return render(request, 'attendance/help.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(1209600)
                
                messages.success(request, f'Welcome back, {user.first_name}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    
    context = {'form': form}
    return render(request, 'attendance/auth/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)
    
    student_data = None
    if hasattr(request.user, 'student'):
        student = request.user.student
        total_attendances = student.attendances.count()
        present_count = student.attendances.filter(status='present').count()
        attendance_rate = round((present_count / total_attendances * 100), 1) if total_attendances > 0 else 0
        
        student_data = {
            'student': student,
            'total_attendances': total_attendances,
            'attendance_rate': attendance_rate,
        }
    
    context = {
        'form': form,
        'profile': profile,
        'student_data': student_data,
    }
    return render(request, 'attendance/auth/profile.html', context)

@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if profile.role == 'student' and hasattr(request.user, 'student'):
        student = request.user.student
        courses = student.courses.all()
        recent_attendances = student.attendances.all()[:5]
        
        context = {
            'role': 'student',
            'courses': courses,
            'recent_attendances': recent_attendances,
            'student_profile': student,
        }
    elif profile.role == 'instructor':
        courses = Course.objects.filter(instructor=request.user)
        recent_sessions = AttendanceSession.objects.filter(course__instructor=request.user)[:5]
        
        context = {
            'role': 'instructor',
            'courses': courses,
            'recent_sessions': recent_sessions,
        }
    else:
        total_students = Student.objects.count()
        total_courses = Course.objects.count()
        today_sessions = AttendanceSession.objects.filter(date=timezone.now().date()).count()
        
        context = {
            'role': 'admin',
            'total_students': total_students,
            'total_courses': total_courses,
            'today_sessions': today_sessions,
        }
    
    return render(request, 'attendance/dashboard.html', context)

@login_required
def student_list(request):
    search_query = request.GET.get('search', '')
    students = Student.objects.all()
    
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )
    
    paginator = Paginator(students, 10)
    page = request.GET.get('page')
    students = paginator.get_page(page)
    
    context = {'students': students}
    return render(request, 'attendance/student_list.html', context)

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendances = student.attendances.all()[:20]
    
    total_attendances = student.attendances.count()
    present_count = student.attendances.filter(status='present').count()
    attendance_rate = round((present_count / total_attendances * 100), 1) if total_attendances > 0 else 0
    
    context = {
        'student': student,
        'attendances': attendances,
        'attendance_rate': attendance_rate,
    }
    return render(request, 'attendance/student_detail.html', context)

@login_required
def mark_attendance(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    students = session.course.students.all()
    
    if request.method == 'POST':
        updated = False
        for student in students:
            status = request.POST.get(f'status_{student.id}', None)
            remarks = request.POST.get(f'remarks_{student.id}', '')
            if status:
                Attendance.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={'status': status, 'remarks': remarks}
                )
                updated = True
        if updated:
            messages.success(request, 'Attendance marked successfully!')
        else:
            messages.warning(request, 'No attendance was updated. Please select a status.')
        return redirect('session_detail', session_id=session.id)
    
    context = {
        'session': session,
        'students': students,
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
def student_checkin(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)

    # Ensure the user is a student and is enrolled in the course
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Only students can check in.')
        return redirect('session_detail', session_id=session.id)

    student = request.user.student
    if not session.course.students.filter(id=student.id).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('session_detail', session_id=session.id)

    # Optional: enforce check-in time window if session has start_time/end_time
    now = timezone.now()
    if getattr(session, 'start_time', None) and getattr(session, 'end_time', None):
        # combine date with times if date fields are present
        try:
            start_dt = timezone.make_aware(timezone.datetime.combine(session.date, session.start_time))
            end_dt = timezone.make_aware(timezone.datetime.combine(session.date, session.end_time))
        except Exception:
            start_dt = None
            end_dt = None

        if start_dt and end_dt and not (start_dt <= now <= end_dt):
            messages.error(request, 'Check-in is not open at this time.')
            return redirect('session_detail', session_id=session.id)

    # Record attendance as 'present' for the checking student
    # If the session requires a check-in code, validate it
    required_code = getattr(session, 'checkin_code', None)
    if required_code:
        entered = request.POST.get('checkin_code', '').strip()
        if not entered or entered != str(required_code):
            messages.error(request, 'Invalid or missing check-in code.')
            return redirect('session_detail', session_id=session.id)

    Attendance.objects.update_or_create(
        session=session,
        student=student,
        defaults={'status': 'present'}
    )

    messages.success(request, 'Checked in — attendance recorded.')
    return redirect('session_detail', session_id=session.id)

@login_required
def session_detail(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    attendances = session.attendances.all()
    
    stats = {
        'present': attendances.filter(status='present').count(),
        'absent': attendances.filter(status='absent').count(),
        'late': attendances.filter(status='late').count(),
        'excused': attendances.filter(status='excused').count(),
    }
    
    total = sum(stats.values())
    stats['present_percentage'] = round((stats['present'] / total * 100), 1) if total > 0 else 0
    # Determine whether the current user can self check-in
    can_checkin = False
    student_absences = 0
    if request.user.is_authenticated and hasattr(request.user, 'student'):
        student = request.user.student
        if session.course.students.filter(id=student.id).exists():
            now = timezone.now()
            start_dt = None
            end_dt = None
            if getattr(session, 'start_time', None) and getattr(session, 'end_time', None):
                try:
                    start_dt = timezone.make_aware(timezone.datetime.combine(session.date, session.start_time))
                    end_dt = timezone.make_aware(timezone.datetime.combine(session.date, session.end_time))
                except Exception:
                    start_dt = None
                    end_dt = None

            if (start_dt and end_dt and (start_dt <= now <= end_dt)) or (not start_dt and not end_dt):
                can_checkin = True
            
            # Get student absence count
            student_absences = get_student_absence_count(student)

    context = {
        'session': session,
        'attendances': attendances,
        'stats': stats,
        'can_checkin': can_checkin,
        'student_absences': student_absences,
    }
    return render(request, 'attendance/session_detail.html', context)

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def export_attendance(request, session_id):
    """Export session attendance as CSV."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    return export_attendance_csv(session)

def is_admin_or_instructor(user):
    if user.is_superuser:
        return True
    if hasattr(user, 'profile') and user.profile.role in ['admin', 'instructor']:
        return True
    return False

@login_required
def course_list(request):
    search_query = request.GET.get('search', '')
    courses = Course.objects.all()
    
    if search_query:
        courses = courses.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(courses, 10)
    page = request.GET.get('page')
    courses = paginator.get_page(page)
    
    context = {'courses': courses}
    return render(request, 'attendance/course_list.html', context)

@login_required
@user_passes_test(is_admin_or_instructor)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            if not course.instructor:
                course.instructor = request.user
            course.save()
            form.save_m2m()
            messages.success(request, f'Course {course.code} created successfully!')
            return redirect('course_detail', course_id=course.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm()
    
    context = {'form': form, 'title': 'Add Course'}
    return render(request, 'attendance/course_form.html', context)

@login_required
@user_passes_test(is_admin_or_instructor)
def course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check permission: only admin or course instructor can edit
    if request.user != course.instructor and not is_admin_or_instructor(request.user):
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('course_detail', course_id=course_id)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course {course.code} updated successfully!')
            return redirect('course_detail', course_id=course.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm(instance=course)
    
    context = {'form': form, 'title': 'Edit Course', 'course': course}
    return render(request, 'attendance/course_form.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.students.all()
    sessions = course.sessions.all()[:10]
    
    context = {
        'course': course,
        'students': students,
        'sessions': sessions,
        'enrollment_percentage': course.get_enrollment_percentage(),
    }
    return render(request, 'attendance/course_detail.html', context)

@login_required
@user_passes_test(is_admin_or_instructor)
def attendance_report(request):
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    course_id = request.GET.get('course')
    
    attendances = Attendance.objects.all()
    
    if date_from:
        attendances = attendances.filter(session__date__gte=date_from)
    if date_to:
        attendances = attendances.filter(session__date__lte=date_to)
    if course_id:
        attendances = attendances.filter(session__course_id=course_id)
    
    stats = {
        'total': attendances.count(),
        'present': attendances.filter(status='present').count(),
        'absent': attendances.filter(status='absent').count(),
        'late': attendances.filter(status='late').count(),
        'excused': attendances.filter(status='excused').count(),
    }
    
    stats['present_percentage'] = round((stats['present'] / stats['total'] * 100), 1) if stats['total'] > 0 else 0
    
    courses = Course.objects.all()
    
    context = {
        'attendances': attendances[:50],
        'stats': stats,
        'courses': courses,
        'date_from': date_from,
        'date_to': date_to,
        'course_id': course_id,
    }
    return render(request, 'attendance/attendance_report.html', context)

@login_required
def student_statistics(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendances = student.attendances.all()
    courses = student.courses.all()
    
    by_status = {
        'present': attendances.filter(status='present').count(),
        'absent': attendances.filter(status='absent').count(),
        'late': attendances.filter(status='late').count(),
        'excused': attendances.filter(status='excused').count(),
    }
    
    total = attendances.count()
    attendance_rate = round((by_status['present'] / total * 100), 1) if total > 0 else 0
    
    course_stats = []
    for course in courses:
        course_attendances = attendances.filter(session__course=course)
        course_present = course_attendances.filter(status='present').count()
        course_total = course_attendances.count()
        course_rate = round((course_present / course_total * 100), 1) if course_total > 0 else 0
        
        course_stats.append({
            'course': course,
            'total': course_total,
            'present': course_present,
            'rate': course_rate,
        })
    
    context = {
        'student': student,
        'total_sessions': total,
        'attendance_rate': attendance_rate,
        'by_status': by_status,
        'course_stats': course_stats,
    }
    return render(request, 'attendance/student_statistics.html', context)

@login_required
@user_passes_test(is_admin_or_instructor)
def admin_dashboard(request):
    if not is_admin_or_instructor(request.user):
        return redirect('dashboard')
    
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_sessions = AttendanceSession.objects.count()
    total_attendance_records = Attendance.objects.count()
    
    today = timezone.now().date()
    today_sessions = AttendanceSession.objects.filter(date=today)
    week_ago = today - timedelta(days=7)
    week_sessions = AttendanceSession.objects.filter(date__gte=week_ago)
    
    active_students = Student.objects.filter(status='active').count()
    avg_attendance = 0
    if total_attendance_records > 0:
        present_count = Attendance.objects.filter(status='present').count()
        avg_attendance = round((present_count / total_attendance_records * 100), 1)
    
    recent_sessions = AttendanceSession.objects.all()[:5]
    top_courses = Course.objects.annotate(
        student_count=Count('students')
    ).order_by('-student_count')[:5]
    
    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_sessions': total_sessions,
        'total_attendance_records': total_attendance_records,
        'today_sessions': today_sessions.count(),
        'week_sessions': week_sessions.count(),
        'active_students': active_students,
        'avg_attendance': avg_attendance,
        'recent_sessions': recent_sessions,
        'top_courses': top_courses,
    }
    return render(request, 'attendance/admin_dashboard.html', context)


# Phase 2: Medium Effort Features

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def detailed_attendance_report(request):
    """Detailed attendance report with filtering."""
    filters = {}
    courses = Course.objects.all()
    
    if request.GET.get('course'):
        filters['course_id'] = request.GET.get('course')
    if request.GET.get('student'):
        filters['student_id'] = request.GET.get('student')
    if request.GET.get('date_from'):
        filters['date_from'] = request.GET.get('date_from')
    if request.GET.get('date_to'):
        filters['date_to'] = request.GET.get('date_to')
    if request.GET.get('status'):
        filters['status'] = request.GET.get('status')
    
    report_data = generate_attendance_report(filters if filters else None)
    
    # Get students for dropdown
    students = Student.objects.all()
    
    # Export handling
    export_format = request.GET.get('export')
    if export_format == 'csv':
        return export_report_to_csv(report_data, 'general')
    elif export_format == 'pdf':
        return export_report_to_pdf(report_data, 'general')
    
    # Pagination
    paginator = Paginator(report_data, 50)
    page = request.GET.get('page')
    report_page = paginator.get_page(page)
    
    context = {
        'report': report_page,
        'courses': courses,
        'students': students,
        'filters': filters,
        'total_records': len(report_data),
        'status_choices': Attendance.STATUS_CHOICES,
    }
    return render(request, 'attendance/detailed_report.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def course_attendance_report(request, course_id):
    """Detailed attendance report for a specific course."""
    course = get_object_or_404(Course, id=course_id)
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    report_data = generate_course_attendance_report(course, date_from, date_to)
    
    # Export handling
    export_format = request.GET.get('export')
    if export_format == 'csv':
        return export_report_to_csv(report_data, 'course')
    elif export_format == 'pdf':
        return export_report_to_pdf(report_data, 'course')
    
    context = {
        'course': course,
        'report': report_data,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'attendance/course_report.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def student_attendance_report(request, student_id):
    """Detailed attendance report for a specific student."""
    student = get_object_or_404(Student, id=student_id)
    report_data = generate_student_attendance_report(student)
    
    # Export handling
    export_format = request.GET.get('export')
    if export_format == 'csv':
        return export_report_to_csv(report_data, 'student')
    elif export_format == 'pdf':
        return export_report_to_pdf(report_data, 'student')
    
    context = {
        'student': student,
        'report': report_data,
    }
    return render(request, 'attendance/student_report.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def course_analytics(request, course_id):
    """Display analytics for a course."""
    course = get_object_or_404(Course, id=course_id)
    analytics = get_course_analytics(course)
    trends = get_attendance_trends(course, days=30)
    
    # Per-student analytics
    student_analytics = []
    for student in course.students.all():
        student_analytics.append({
            'student': student,
            'analytics': get_student_course_analytics(student, course)
        })
    
    context = {
        'course': course,
        'analytics': analytics,
        'trends': trends,
        'student_analytics': student_analytics,
    }
    return render(request, 'attendance/course_analytics.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def recurring_session_create(request, course_id):
    """Create recurring sessions for a course."""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        form = RecurringSessionForm(request.POST)
        if form.is_valid():
            recurring_session = form.save(commit=False)
            recurring_session.course = course
            recurring_session.save()
            
            # Generate individual sessions
            session_dates = recurring_session.generate_sessions()
            created_count = 0
            
            for session_date in session_dates:
                try:
                    AttendanceSession.objects.create(
                        course=course,
                        date=session_date,
                        start_time=recurring_session.start_time,
                        end_time=recurring_session.end_time,
                        notes=recurring_session.notes,
                        is_recurring=True,
                    )
                    created_count += 1
                except Exception:
                    pass
            
            messages.success(request, f'Created {created_count} attendance sessions from recurring template.')
            return redirect('course_detail', course_id=course.id)
    else:
        form = RecurringSessionForm(initial={'course': course})
    
    context = {'form': form, 'course': course}
    return render(request, 'attendance/recurring_session_form.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def bulk_import_students(request, course_id):
    """Import students to a course via CSV file."""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        form = StudentImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                file_content = csv_file.read()
                successful, errors = import_students_from_csv(file_content, course)
                
                # Create import log
                StudentImportLog.objects.create(
                    course=course,
                    uploaded_by=request.user,
                    file_name=csv_file.name,
                    status='completed',
                    total_records=successful + len(errors),
                    successful_imports=successful,
                    failed_imports=len(errors),
                    error_details='\n'.join(errors) if errors else '',
                )
                
                messages.success(request, f'Successfully imported {successful} student(s).')
                if errors:
                    messages.warning(request, f'{len(errors)} record(s) had errors. Check the import log.')
                
                return redirect('course_detail', course_id=course.id)
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = StudentImportForm()
        form.fields['course'].initial = course
        form.fields['course'].queryset = Course.objects.filter(id=course.id)
    
    context = {'form': form, 'course': course}
    return render(request, 'attendance/bulk_import_form.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.role in ['instructor', 'admin'])
def import_logs(request, course_id):
    """View import logs for a course."""
    course = get_object_or_404(Course, id=course_id)
    logs = course.import_logs.all().order_by('-created_at')
    
    paginator = Paginator(logs, 20)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    context = {'course': course, 'logs': logs}
    return render(request, 'attendance/import_logs.html', context)