# Quick Reference Guide - Attendance System Features

## 🚀 Quick Start

### Access Reports
- **Detailed Report**: `/reports/detailed/`
- **Course Report**: `/reports/course/{course_id}/`
- **Student Report**: `/reports/student/{student_id}/`

### Course Management
- **Create Session**: `/courses/{id}/sessions/create/`
- **Create Recurring**: `/courses/{id}/recurring/create/`
- **Import Students**: `/courses/{id}/import/`
- **View Analytics**: `/courses/{id}/analytics/`

### Attendance Marking
- **Manual Attendance**: `/sessions/{id}/manual/`
- **Session Detail**: `/sessions/{id}/`
- **My Sessions** (Student): `/my-sessions/`

---

## 📊 Report Types

### 1. General Attendance Report
**Access**: `/reports/detailed/`
**Filters**: Course, Student, Status, Date Range
**Export**: CSV, PDF
**Best For**: Finding specific attendance records

**Query Examples**:
```
/reports/detailed/?course=1
/reports/detailed/?date_from=2025-01-01&date_to=2025-12-31
/reports/detailed/?status=absent
/reports/detailed/?student=5&export=csv
```

### 2. Course Report
**Access**: `/reports/course/{course_id}/`
**Filters**: Date Range
**Export**: CSV, PDF
**Best For**: Course-level analysis and student breakdown

**Shows**:
- Session attendance breakdown (session by session)
- Per-student summary (all students)
- Attendance rates for each session
- Individual student records

### 3. Student Report
**Access**: `/reports/student/{student_id}/`
**Filters**: None
**Export**: CSV, PDF
**Best For**: Individual student tracking

**Shows**:
- Student information
- Summary statistics (total, present, absent, late, excused)
- Per-course breakdown
- Detailed session log

---

## 🔧 Features by Phase

### Phase 1: Quick Wins ✅
```
Session Code Display          → Show code in session_detail.html
CSV Export                    → Export button on session_detail.html
Countdown Timer               → Real-time timer on my_sessions.html
Student Search                → Search box on manual_attendance.html
Absence Alert                 → Yellow alert on session_detail.html
```

### Phase 2: Medium Effort ✅
```
Analytics Dashboard           → /courses/{id}/analytics/
Recurring Sessions            → /courses/{id}/recurring/create/
Bulk Student Import           → /courses/{id}/import/
Late Cutoff Automation        → Set late_cutoff_minutes on sessions
Session Notes                 → Notes field on session form
```

### Phase 3: Detailed Reports ✅
```
General Report                → /reports/detailed/
Course Report                 → /reports/course/{id}/
Student Report                → /reports/student/{id}/
CSV Export                    → ?export=csv on any report
PDF Export                    → ?export=pdf on any report
```

---

## 📋 Model Fields

### AttendanceSession
```python
course                # ForeignKey to Course
date                  # DateField
start_time, end_time  # TimeField
checkin_code          # CharField (optional)
notes                 # TextField (optional)
late_cutoff_minutes   # IntegerField (default=15) [NEW]
is_recurring          # BooleanField (default=False) [NEW]
duration              # IntegerField
```

### Attendance
```python
session               # ForeignKey to AttendanceSession
student               # ForeignKey to Student
status                # CharField (present/absent/late/excused)
remarks               # TextField (optional)
recorded_at           # DateTimeField (auto)
checkin_time          # TimeField (optional) [NEW]
```

### RecurringSession [NEW]
```python
course                # ForeignKey to Course
start_date, end_date  # DateField
start_time, end_time  # TimeField
frequency             # CharField (daily/weekly/biweekly/monthly)
day_of_week           # IntegerField (0=Mon, 6=Sun)
notes                 # TextField (optional)
is_active             # BooleanField
```

### StudentImportLog [NEW]
```python
course                # ForeignKey to Course
uploaded_by           # ForeignKey to User
file_name             # CharField
status                # CharField (pending/processing/completed/failed)
total_records         # IntegerField
successful_imports    # IntegerField
failed_imports        # IntegerField
error_details         # TextField (optional)
```

---

## 📝 CSV Import Format

### Required Columns
```csv
student_id,first_name,last_name,email
STU001,John,Doe,john@example.com
STU002,Jane,Smith,jane@example.com
```

### Optional Columns
```csv
student_id,first_name,last_name,email,phone,department,major
STU001,John,Doe,john@example.com,1234567890,Engineering,CS
```

---

## 🔐 Permission Requirements

### Student Routes
- `/my-sessions/` - View own sessions, check in
- `/sessions/{id}/` - View session, self check-in

### Instructor/Admin Routes
- `/courses/{id}/` - Manage course
- `/courses/{id}/analytics/` - View analytics
- `/courses/{id}/recurring/create/` - Create recurring sessions
- `/courses/{id}/import/` - Bulk import students
- `/courses/{id}/imports/` - View import logs
- `/sessions/{id}/manual/` - Mark attendance manually
- `/sessions/{id}/export/` - Export attendance to CSV
- `/reports/detailed/` - View detailed report
- `/reports/course/{id}/` - View course report
- `/reports/student/{id}/` - View student report
- `/admin/` - View admin dashboard

---

## 🎯 Common Tasks

### Export Session Attendance
1. Go to session detail: `/sessions/{id}/`
2. Click "Export CSV" button (top right)
3. File downloads as `attendance_SESSION_ID_DATE.csv`

### Create Recurring Sessions
1. Go to course: `/courses/{id}/`
2. Click "Recurring" button
3. Set: Start/End dates, times, frequency
4. Click "Create Sessions"
5. System generates all sessions automatically

### Bulk Import Students
1. Go to course: `/courses/{id}/`
2. Click "Import" button
3. Download CSV template or use format above
4. Upload CSV file
5. Review import log in "Logs" tab

### Generate Course Report
1. Go to course: `/courses/{id}/`
2. Click "Report" button
3. Set optional date filters
4. Click "Apply Filters"
5. Export to CSV or PDF as needed

### Track Student Attendance
1. Go to course: `/courses/{id}/`
2. Click "Analytics" button
3. Find student in "Student Attendance Summary"
4. Click student name to view detailed report
5. See session-by-session breakdown

---

## 📱 Mobile Features

### Responsive Design
- ✅ All templates mobile-optimized
- ✅ Tables scroll on small screens
- ✅ Buttons stack on mobile
- ✅ Touch-friendly input sizes
- ✅ Readable font sizes

### Mobile-Friendly Features
1. **Countdown Timer** - Large, easy-to-read timer on `/my-sessions/`
2. **Search Filter** - Quick student lookup on manual attendance
3. **Status Badges** - Color-coded, easy-to-distinguish attendance status
4. **Responsive Tables** - Horizontal scroll on small screens
5. **Touch Targets** - Buttons and links sized for touch

---

## ⚙️ Configuration

### Late Cutoff Minutes
- Default: 15 minutes after session start
- Configurable per session: `late_cutoff_minutes` field
- Used for: Auto-marking students who check in late

### Session Code
- Optional field: `checkin_code`
- Leave blank if not using code-based check-in
- Students enter code to check themselves in

### Recurring Session Frequencies
- **Daily**: Generate one session per day
- **Weekly**: Generate on specific day of week
- **Biweekly**: Generate every 2 weeks on specified day
- **Monthly**: Generate on same date each month

---

## 🐛 Troubleshooting

### Reports Not Showing Data
**Solution**: 
- Ensure attendances exist for the session
- Check date filters are not excluding data
- Verify student is enrolled in course

### CSV Import Fails
**Solution**:
- Check CSV format matches template
- Verify required fields: student_id, first_name, last_name, email
- Look in import logs for specific error messages
- Email must be unique per student

### PDF Export Not Working
**Solution**:
- Install reportlab: `pip install reportlab`
- Fallback to CSV export if not available
- Check console for error messages

### Countdown Timer Not Showing
**Solution**:
- Ensure session.end_time is set
- Check browser console for JavaScript errors
- Verify session is open (current time between start and end)

---

## 📈 Performance Tips

### For Large Classes (500+ students)
1. Use bulk import instead of manual entry
2. Use recurring sessions for scheduling
3. Paginate attendance marking (50 at a time)
4. Use filters on general report instead of viewing all

### For Large Courses (20+ sessions per semester)
1. Use recurring sessions (create 15 weeks in one form)
2. Use course report instead of general report
3. Set late cutoff to automate marking
4. Export data to spreadsheet for analysis

### Export Recommendations
- **CSV Export**: Fast, spreadsheet-compatible, no dependencies
- **PDF Export**: Professional, distributable, requires reportlab

---

## 🔄 Workflow Examples

### Typical Instructor Workflow
1. Start of semester: Import all students via CSV
2. Create recurring sessions (15 weeks, MWF)
3. Each class: Mark attendance manually or students self-check
4. Mid-semester: View analytics to identify at-risk students
5. End of semester: Generate course report and export to PDF
6. Share final report with department

### Typical Student Workflow
1. See open sessions on `/my-sessions/`
2. Check countdown timer to see deadline
3. Enter session code or click check-in button
4. See confirmation that they're checked in
5. Later: View absence alerts if they have 3+ absences

### Typical Admin Workflow
1. View admin dashboard: `/admin/`
2. Check today's sessions
3. View average attendance across all courses
4. Click "Detailed Report" for drill-down analysis
5. Export filtered data for institutional reporting

---

## 📊 Data Retention

### Automatic Data
- All attendance records are kept indefinitely
- Historical session data preserved
- Import logs retained for audit trail

### Export Data
- CSV files: Store as backups or analysis
- PDF reports: Distribute to stakeholders
- Keep institutional copies per compliance needs

---

## 🚀 Getting Started

### First Time Setup
```bash
# Apply database migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Visit http://localhost:8000
```

### First Time Usage
1. Log in as admin
2. Create at least one course
3. Create or import students
4. Create or generate sessions
5. Test attendance marking
6. Generate sample report

---

## 📚 Further Reading

- **Phase 1 Details**: See `PHASE1_COMPLETION.md`
- **Phase 2 Details**: See `PHASE2_COMPLETION.md`
- **Phase 3 Details**: See `PHASE3_COMPLETION.md`
- **Project Overview**: See `PROJECT_COMPLETION_SUMMARY.md`

---

**Last Updated**: December 16, 2025  
**Version**: 3.0 (15 features, 3 phases complete)  
**Status**: ✅ Production Ready
