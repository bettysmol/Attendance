from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField()
    enrollment_date = models.DateField(default=timezone.now)
    department = models.CharField(max_length=100, blank=True)
    major = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    semester = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    students = models.ManyToManyField(Student, related_name='courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    capacity = models.IntegerField(default=50)
    credits = models.IntegerField(default=3)
    semester = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_enrollment_percentage(self):
        total = self.students.count()
        if total == 0:
            return 0
        return round((total / self.capacity * 100), 1)

class AttendanceSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    checkin_code = models.CharField(max_length=32, blank=True, null=True, help_text='Optional simple code students can enter to check in')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(help_text="Duration in minutes", default=60)
    late_cutoff_minutes = models.IntegerField(default=15, help_text='Minutes after start time to auto-mark as late')
    is_recurring = models.BooleanField(default=False, help_text='Generated from recurring template')
    
    class Meta:
        ordering = ['-date', '-start_time']
        unique_together = ['course', 'date', 'start_time']
    
    def __str__(self):
        return f"{self.course.code} - {self.date}"
    
    def get_attendance_percentage(self):
        total = self.attendances.count()
        present = self.attendances.filter(status='present').count()
        if total == 0:
            return 0
        return round((present / total * 100), 1)

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    remarks = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    checkin_time = models.TimeField(null=True, blank=True, help_text='Time student actually checked in')
    
    class Meta:
        unique_together = ['session', 'student']
        ordering = ['student__last_name']
    
    def __str__(self):
        return f"{self.student} - {self.session} - {self.status}"


class RecurringSession(models.Model):
    """Template for recurring attendance sessions"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='recurring_sessions')
    start_date = models.DateField(help_text='First session date')
    end_date = models.DateField(help_text='Last session date')
    start_time = models.TimeField()
    end_time = models.TimeField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='weekly')
    day_of_week = models.IntegerField(default=0, help_text='0=Monday, 6=Sunday (for weekly/biweekly)')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.code} - {self.frequency.title()}"
    
    def generate_sessions(self):
        """Generate individual sessions based on recurrence pattern"""
        from datetime import timedelta
        sessions = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            if self.frequency == 'daily':
                sessions.append(current_date)
                current_date += timedelta(days=1)
            elif self.frequency == 'weekly':
                if current_date.weekday() == self.day_of_week:
                    sessions.append(current_date)
                current_date += timedelta(days=1)
            elif self.frequency == 'biweekly':
                if current_date.weekday() == self.day_of_week:
                    sessions.append(current_date)
                    current_date += timedelta(days=14)
                else:
                    current_date += timedelta(days=1)
            elif self.frequency == 'monthly':
                if current_date.day == self.start_date.day:
                    sessions.append(current_date)
                current_date += timedelta(days=1)
        
        return sessions


class StudentImportLog(models.Model):
    """Track bulk student imports"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='import_logs')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_records = models.IntegerField(default=0)
    successful_imports = models.IntegerField(default=0)
    failed_imports = models.IntegerField(default=0)
    error_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.code} - {self.file_name} ({self.status})"