from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Welcome
    path('welcome/', views.welcome_view, name='welcome'),
    
    # Help
    path('help/', views.help_view, name='help'),
    
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='attendance/auth/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='attendance/auth/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='attendance/auth/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='attendance/auth/password_reset_complete.html'),
         name='password_reset_complete'),
    
    # Dashboard and main URLs
    path('', views.dashboard, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Student URLs
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/statistics/', views.student_statistics, name='student_statistics'),
    
    # Course URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:course_id>/sessions/create/', views.session_create, name='session_create'),
    path('courses/<int:course_id>/analytics/', views.course_analytics, name='course_analytics'),
    path('courses/<int:course_id>/recurring/create/', views.recurring_session_create, name='recurring_session_create'),
    path('courses/<int:course_id>/import/', views.bulk_import_students, name='bulk_import_students'),
    path('courses/<int:course_id>/imports/', views.import_logs, name='import_logs'),
    
    # Session and Attendance URLs
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('sessions/<int:session_id>/export/', views.export_attendance, name='export_attendance'),
    path('sessions/<int:session_id>/mark/', views.mark_attendance, name='mark_attendance'),
    path('sessions/<int:session_id>/manual/', views.manual_attendance, name='manual_attendance'),
    path('sessions/<int:session_id>/checkin/', views.student_checkin, name='student_checkin'),

    # Reports
    path('reports/attendance/', views.attendance_report, name='attendance_report'),
    path('reports/detailed/', views.detailed_attendance_report, name='detailed_attendance_report'),
    path('reports/course/<int:course_id>/', views.course_attendance_report, name='course_attendance_report'),
    path('reports/student/<int:student_id>/', views.student_attendance_report, name='student_attendance_report'),

    # Student: My Sessions
    path('my-sessions/', views.my_sessions, name='my_sessions'),
]