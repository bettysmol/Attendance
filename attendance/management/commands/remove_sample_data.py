from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import UserProfile, Student, Course, AttendanceSession, Attendance


class Command(BaseCommand):
    help = 'Remove seeded sample users, students, courses, sessions and attendance records'

    def handle(self, *args, **options):
        usernames = ['instructor1'] + [f'student{i}' for i in range(1, 11)]
        course_codes = ['CS101', 'MATH101', 'ENG101']

        self.stdout.write('Removing seeded sample data...')

        users_qs = User.objects.filter(username__in=usernames)
        self.stdout.write(f'Users found for deletion: {users_qs.count()}')

        students_qs = Student.objects.filter(user__username__in=usernames)
        self.stdout.write(f'Student profiles found for deletion: {students_qs.count()}')

        courses_qs = Course.objects.filter(code__in=course_codes)
        self.stdout.write(f'Courses found for deletion: {courses_qs.count()}')

        # Delete attendance records tied to sessions of the targeted courses
        sessions_qs = AttendanceSession.objects.filter(course__in=courses_qs)
        attendance_count = Attendance.objects.filter(session__in=sessions_qs).count()
        if attendance_count:
            Attendance.objects.filter(session__in=sessions_qs).delete()
        self.stdout.write(f'Deleted {attendance_count} attendance records tied to target courses.')

        # Delete sessions
        sessions_count = sessions_qs.count()
        if sessions_count:
            sessions_qs.delete()
        self.stdout.write(f'Deleted {sessions_count} attendance sessions for target courses.')

        # Delete courses
        courses_count = courses_qs.count()
        if courses_count:
            courses_qs.delete()
        self.stdout.write(f'Deleted {courses_count} courses with codes: {course_codes}')

        # Delete Student model entries
        students_count = students_qs.count()
        if students_count:
            students_qs.delete()
        self.stdout.write(f'Deleted {students_count} Student records.')

        # Delete related user profiles
        upro_qs = UserProfile.objects.filter(user__username__in=usernames)
        upro_count = upro_qs.count()
        if upro_count:
            upro_qs.delete()
        self.stdout.write(f'Deleted {upro_count} UserProfile records for sample users.')

        # Finally delete User accounts
        users_count = users_qs.count()
        if users_count:
            users_qs.delete()
        self.stdout.write(f'Deleted {users_count} User accounts (sample).')

        self.stdout.write(self.style.SUCCESS('Seeded sample data removal complete.'))
