#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
    
    # Set PostgreSQL database URL if not already set
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'postgresql://attendance_db_uix1_user:l0PXwUm7kpwSaAB1e0K2L6OcrRdLYXqk@dpg-d5tdj9dactks73a5cv40-a/attendance_db_uix1'
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
