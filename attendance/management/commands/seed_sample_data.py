from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import UserProfile, Student, Course, AttendanceSession, Attendance
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Seed the database with sample users, students, courses, sessions and attendance records'

    def handle(self, *args, **options):
        self.stdout.write('Seeding sample data...')

        # Create instructor user
        instructor, created = User.objects.get_or_create(username='instructor1', defaults={
            'email': 'instructor1@example.com',
            'first_name': 'Alex',
            'last_name': 'Instructor'
        })
        if created:
            instructor.set_password('password')
            instructor.save()
            UserProfile.objects.create(user=instructor, role='instructor')

        # Create students
        students = []
        for i in range(1, 11):
            username = f'student{i}'
            user, created = User.objects.get_or_create(username=username, defaults={
                'email': f'{username}@example.com',
                'first_name': f'Student{i}',
                'last_name': 'Sample'
            })
            if created:
                user.set_password('password')
                user.save()
                UserProfile.objects.create(user=user, role='student')
            student, _ = Student.objects.get_or_create(user=user, student_id=f'STU{i:04d}', defaults={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'date_of_birth': timezone.now().date()
            })
            students.append(student)

        # Create courses
        course_data = [
            ('CS101', 'Intro to Computer Science'),
            ('MATH101', 'Calculus I'),
            ('ENG101', 'English Literature')
        ]
        courses = []
        for code, name in course_data:
            course, created = Course.objects.get_or_create(code=code, defaults={
                'name': name,
                'instructor': instructor,
                'capacity': 30,
                'credits': 3,
                'semester': 1,
            })
            # Enroll a subset of students
            for s in random.sample(students, k=6):
                course.students.add(s)
            course.save()
            courses.append(course)

        # Create sessions for the past 5 days
        for course in courses:
            for days_ago in range(5, 0, -1):
                date = timezone.now().date() - timezone.timedelta(days=days_ago)
                start_time = timezone.now().time().replace(hour=9, minute=0, second=0, microsecond=0)
                end_time = timezone.now().time().replace(hour=10, minute=0, second=0, microsecond=0)
                session, created = AttendanceSession.objects.get_or_create(course=course, date=date, start_time=start_time, defaults={
                    'end_time': end_time,
                    'duration': 60,
                })

                # Create attendance records for enrolled students
                for student in course.students.all():
                    status = random.choices(['present', 'absent', 'late', 'excused'], weights=[70,20,7,3])[0]
                    Attendance.objects.update_or_create(session=session, student=student, defaults={
                        'status': status,
                        'remarks': ''
                    })

        self.stdout.write(self.style.SUCCESS('Sample data seeded successfully.'))
