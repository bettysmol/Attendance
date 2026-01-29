from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Ensure all migrations are applied'

    def handle(self, *args, **options):
        try:
            call_command('migrate', '--noinput', verbosity=2)
            self.stdout.write(self.style.SUCCESS('✓ Migrations completed successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Migration error: {str(e)}'))
            raise
