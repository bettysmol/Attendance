# Attendance System - Quick Reference

## 🚀 Quick Start (30 seconds)

```bash
cd c:\Users\User\attendance_system
python manage.py runserver
```

Then open: **http://localhost:8000**

---

## 📍 Important URLs

| What | URL |
|------|-----|
| **Homepage/Dashboard** | `http://localhost:8000/` |
| **Admin Panel** | `http://localhost:8000/admin/` |
| **Register** | `http://localhost:8000/register/` |
| **Login** | `http://localhost:8000/login/` |
| **Courses** | `http://localhost:8000/courses/` |
| **Students** | `http://localhost:8000/students/` |
| **Attendance Reports** | `http://localhost:8000/reports/attendance/` |
| **Admin Dashboard** | `http://localhost:8000/admin/` |

---

## 🔐 Default Login

After creating a superuser:
```bash
python manage.py createsuperuser
```

Use those credentials to login.

---

## 👥 User Roles & Access

### Student
- Dashboard (personal)
- View courses
- Check attendance
- View statistics

### Instructor  
- Dashboard
- Manage courses
- Mark attendance
- View reports
- Admin dashboard

### Admin
- Full access to everything
- Manage users
- Manage courses
- Manage students
- View all reports

---

## ⚙️ Essential Commands

```bash
# Start server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Apply migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Collect static files
python manage.py collectstatic

# Access shell
python manage.py shell

# Check system
python manage.py check
```

---

## 📊 Key Features

✅ Student registration & login  
✅ Course management  
✅ Attendance tracking  
✅ Real-time statistics  
✅ Comprehensive reports  
✅ Role-based access control  
✅ Admin interface  
✅ Mobile responsive  
✅ Professional UI  
✅ Search & filtering  

---

## 🗂️ Project Structure

```
attendance_system/
├── attendance/           # Main app
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── urls.py          # URL routes
│   ├── forms.py         # Form definitions
│   ├── admin.py         # Admin interface
│   └── migrations/      # Database migrations
├── templates/           # HTML templates
│   ├── base.html        # Main template
│   └── attendance/      # App-specific templates
├── static/              # Static files
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript
│   └── images/         # Images
├── db.sqlite3          # Database
├── manage.py           # Django management
└── attendance_system/  # Project settings
```

---

## 🎨 Customization

### Change Theme Colors
Edit: `static/css/styles.css`

### Update Navigation
Edit: `templates/base.html`

### Add New Pages
1. Create view in `attendance/views.py`
2. Add URL in `attendance/urls.py`
3. Create template in `templates/attendance/`

---

## ❌ Troubleshooting

### Server won't start
```bash
python manage.py check
python manage.py migrate
```

### Can't login
- Make sure superuser is created
- Check user has UserProfile
- Verify user role is set

### Attendance won't save
- Check user has permission
- Verify student exists
- Check course enrollment

### Static files not loading
```bash
python manage.py collectstatic --noinput
```

---

## 📈 System Workflow

1. **Admin** creates courses and sessions
2. **Instructor** marks attendance in sessions
3. **System** tracks attendance automatically
4. **Students** view their attendance
5. **Reports** generated for analysis

---

## 🔒 Security Notes

- Use strong passwords
- Set DEBUG=False in production
- Use HTTPS
- Change SECRET_KEY
- Restrict ALLOWED_HOSTS
- Use environment variables

---

## 📞 Quick Help

- **Database:** SQLite (db.sqlite3)
- **Framework:** Django 5.2.6
- **Python:** 3.13+
- **Port:** 8000 (default)

---

Last Updated: November 18, 2025
System Status: ✅ FULLY FUNCTIONAL
