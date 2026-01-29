from django.contrib import admin
from .models import UserProfile, Student, Course, AttendanceSession, Attendance

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'email', 'department', 'status', 'semester', 'enrollment_date']
    list_filter = ['status', 'department', 'semester', 'enrollment_date']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'student_id', 'email', 'phone')
        }),
        ('Academic Information', {
            'fields': ('department', 'major', 'semester', 'status')
        }),
        ('Enrollment', {
            'fields': ('user', 'enrollment_date'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'instructor', 'capacity', 'credits', 'semester', 'student_count']
    list_filter = ['semester', 'credits', 'created_at']
    search_fields = ['code', 'name', 'description']
    filter_horizontal = ['students']
    fieldsets = (
        ('Course Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Course Details', {
            'fields': ('instructor', 'capacity', 'credits', 'semester')
        }),
        ('Students', {
            'fields': ('students',),
        }),
    )
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Enrolled Students'

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['course', 'date', 'start_time', 'end_time', 'duration', 'attendance_rate']
    list_filter = ['date', 'course', 'course__instructor']
    search_fields = ['course__code', 'course__name', 'notes']
    readonly_fields = ['created_at', 'attendance_rate']
    fieldsets = (
        ('Session Information', {
            'fields': ('course', 'date', 'start_time', 'end_time', 'duration')
        }),
        ('Notes', {
            'fields': ('notes',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'attendance_rate'),
            'classes': ('collapse',)
        }),
    )
    
    def attendance_rate(self, obj):
        rate = obj.get_attendance_percentage()
        return f"{rate}%"
    attendance_rate.short_description = 'Attendance Rate'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status_badge', 'recorded_at']
    list_filter = ['status', 'session__date', 'session__course']
    search_fields = ['student__student_id', 'student__first_name', 'student__last_name']
    readonly_fields = ['recorded_at']
    fieldsets = (
        ('Attendance Record', {
            'fields': ('session', 'student', 'status')
        }),
        ('Details', {
            'fields': ('remarks', 'recorded_at'),
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'present': 'green',
            'absent': 'red',
            'late': 'orange',
            'excused': 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return f'<span style="background-color: {color}; color: white; padding: 3px 10px; border-radius: 3px;">{obj.get_status_display()}</span>'
    status_badge.allow_tags = True
    status_badge.short_description = 'Status'