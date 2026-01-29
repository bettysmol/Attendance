# Deployment Guide: GitHub to Render

## Step 1: Initial Setup & Git Configuration

### 1.1 Install Git (if not installed)
- Download from: https://git-scm.com/download/win
- Install with default settings

### 1.2 Configure Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 1.3 Initialize Git Repository
```bash
cd path/to/attendance_system3
git init
git add .
git commit -m "Initial commit: Attendance System"
```

## Step 2: Create GitHub Repository

### 2.1 Create Repository on GitHub
1. Go to https://github.com/new
2. Repository name: `attendance-system` (or your preferred name)
3. Description: "Django Attendance Management System"
4. Choose: Public (so Render can access it)
5. Click "Create repository"

### 2.2 Connect Local Repository to GitHub
```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/attendance-system.git
git push -u origin main
```

## Step 3: Prepare Django for Production

### 3.1 Update settings.py
Add these at the end of `attendance_system/settings.py`:

```python
# Production settings
import os
from pathlib import Path

if not DEBUG:
    # Security settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        "default-src": ("'self'",),
    }
    
    # Database from environment
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
    
    # Static files
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Allow Render domain
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')
```

### 3.2 Update requirements.txt
```
Django==5.2.7
python-dotenv==1.0.0
psycopg2-binary==2.9.9
dj-database-url==2.1.0
gunicorn==21.2.0
whitenoise==6.6.0
```

### 3.3 Create .env.example
Already created - shows environment variables needed

## Step 4: Deploy on Render

### 4.1 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub or email
3. Connect your GitHub account

### 4.2 Deploy Your Application
1. Click "New +" button
2. Select "Web Service"
3. Connect repository: Select `attendance-system`
4. Configure:
   - **Name**: attendance-system
   - **Environment**: Python 3
   - **Region**: Select closest to you
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn attendance_system.wsgi`

### 4.3 Set Environment Variables
In Render dashboard, go to "Environment" and add:
```
DEBUG=False
SECRET_KEY=generate-a-new-random-key
ALLOWED_HOSTS=your-app.onrender.com
DATABASE_URL=postgresql://...
```

### 4.4 Generate Secret Key
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 4.5 Create PostgreSQL Database (Optional)
1. In Render, create a PostgreSQL database
2. Copy the DATABASE_URL
3. Add to environment variables in web service

### 4.6 Run Migrations on Render
After initial deployment:
1. Go to "Shell" tab in Render dashboard
2. Run: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`

## Step 5: Verify Deployment
- Visit your Render URL: `https://your-app.onrender.com`
- Login with superuser account
- Check that static files load correctly

## Troubleshooting

### Static Files Not Loading
- Run: `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL settings

### Database Connection Issues
- Verify DATABASE_URL format
- Check PostgreSQL credentials in Render

### 500 Error
- Check logs in Render dashboard
- Review environment variables

## Important Notes
- Keep `.env` file with secrets locally, never commit to GitHub
- Update ALLOWED_HOSTS when you have your final domain
- Generate a new SECRET_KEY for production
- Don't use `DEBUG=True` in production
