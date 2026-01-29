from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Run migrations with retry logic for database availability'

    def handle(self, *args, **options):
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Test database connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                
                self.stdout.write(self.style.SUCCESS('✓ Database connection successful'))
                
                # Run migrations
                self.stdout.write('Running migrations...')
                call_command('migrate', verbosity=2)
                
                self.stdout.write(self.style.SUCCESS('✓ Migrations completed successfully'))
                return
                
            except OperationalError as e:
                retry_count += 1
                if retry_count < max_retries:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Database not ready (attempt {retry_count}/{max_retries}). Retrying in 5 seconds...'
                        )
                    )
                    import time
                    time.sleep(5)
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to connect to database after {max_retries} attempts'))
                    raise
