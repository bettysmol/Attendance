from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'    
    def ready(self):
        # Only run migrations in production or when migrations are needed
        import os
        from django.db import connection
        from django.core.management import call_command
        
        # Skip this in certain scenarios to avoid infinite loops
        if os.environ.get('SKIP_MIGRATION_CHECK') == 'true':
            return
            
        # Don't run during collectstatic
        if 'collectstatic' in os.sys.argv:
            return
        
        # Don't run during migrations command itself
        if 'migrate' in os.sys.argv or 'makemigrations' in os.sys.argv:
            return
        
        try:
            # Check if auth_user table exists
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM auth_user LIMIT 1")
                except Exception:
                    # Table doesn't exist, run migrations
                    print("Database tables not initialized. Running migrations...")
                    os.environ['SKIP_MIGRATION_CHECK'] = 'true'
                    try:
                        call_command('migrate', verbosity=0, interactive=False)
                        print("✓ Migrations completed during app startup")
                    finally:
                        del os.environ['SKIP_MIGRATION_CHECK']
        except Exception as e:
            print(f"Warning during migration check: {e}")