from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, Student, Course, AttendanceSession, RecurringSession

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)
    phone = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'role':
                field.widget.attrs['class'] = 'form-select'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone=self.cleaned_data.get('phone', '')
            )
            
            if self.cleaned_data['role'] == 'student':
                Student.objects.create(
                    user=user,
                    student_id=f"STU{user.id:05d}",
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    phone=self.cleaned_data.get('phone', ''),
                    date_of_birth=timezone.now().date()
                )
        
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(required=False, initial=True)

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'avatar']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
        
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            
            if commit:
                self.user.save()
                profile.save()
        
        return profile

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'department', 'major', 'status', 'semester']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '8'}),
        }
        help_texts = {
            'student_id': 'Unique identifier for the student. Format: STU followed by numbers (auto-generated if empty).',
            'first_name': 'Student\'s first name.',
            'last_name': 'Student\'s last name.',
            'email': 'Valid university or personal email address.',
            'phone': 'Contact phone number (10-15 digits).',
            'date_of_birth': 'Student\'s date of birth.',
            'department': 'Academic department (e.g., Engineering, Business, Arts).',
            'major': 'Field of study or specialization.',
            'status': 'Current enrollment status. Active = enrolled, Inactive = not enrolled, Graduated = completed, Suspended = temporarily inactive.',
            'semester': 'Current semester number (1-8). Updates annually.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.__class__ not in [forms.Select, forms.DateInput]:
                field.widget.attrs['class'] = 'form-control'

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'description', 'instructor', 'students', 'capacity', 'credits', 'semester']
        widgets = {
            'students': forms.CheckboxSelectMultiple(),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '6'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '8'}),
        }
        help_texts = {
            'code': 'Unique course code (e.g., CS101, MATH201). Letters + numbers format.',
            'name': 'Full course name (e.g., Introduction to Computer Science).',
            'description': 'Brief course description for students.',
            'instructor': 'Select the instructor assigned to this course.',
            'students': 'Select students enrolled in this course. Leave empty to add later.',
            'capacity': 'Maximum number of students allowed in this course (10-500).',
            'credits': 'Number of credit hours (1-6). Affects student workload calculation.',
            'semester': 'Academic semester (1-8). Help identify course level.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.__class__ not in [forms.CheckboxSelectMultiple]:
                field.widget.attrs['class'] = 'form-control'

class AttendanceSessionForm(forms.ModelForm):
    class Meta:
        model = AttendanceSession
        fields = ['course', 'date', 'start_time', 'end_time', 'notes', 'duration', 'late_cutoff_minutes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'max': '240'}),
            'late_cutoff_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '5', 'max': '60'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'course': 'Select the course for this attendance session.',
            'date': 'Session date (YYYY-MM-DD format).',
            'start_time': 'Session start time. Format: HH:MM (e.g., 09:00 for 9 AM).',
            'end_time': 'Session end time. Must be after start time.',
            'notes': 'Optional notes about the session (e.g., Topics covered, special announcements).',
            'duration': 'Session duration in minutes (15-240). Auto-calculated from start/end times.',
            'late_cutoff_minutes': 'Minutes after start time to automatically mark late arrivals.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.__class__ not in [forms.DateInput, forms.TimeInput]:
                if not hasattr(field.widget, 'attrs') or 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'


class RecurringSessionForm(forms.ModelForm):
    class Meta:
        model = RecurringSession
        fields = ['course', 'start_date', 'end_date', 'start_time', 'end_time', 'frequency', 'day_of_week', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}, choices=[
                (0, 'Monday'),
                (1, 'Tuesday'),
                (2, 'Wednesday'),
                (3, 'Thursday'),
                (4, 'Friday'),
                (5, 'Saturday'),
                (6, 'Sunday'),
            ]),
            'course': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'course': 'Select the course for this recurring session.',
            'start_date': 'First session date.',
            'end_date': 'Last session date.',
            'start_time': 'Session start time.',
            'end_time': 'Session end time.',
            'frequency': 'How often the session repeats.',
            'day_of_week': 'For weekly/biweekly: which day of the week.',
            'notes': 'Optional notes about these sessions.',
        }


class StudentImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload CSV with columns: student_id, first_name, last_name, email, (optional) phone, department, major'
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label='Course',
        help_text='Select the course to add imported students to'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'