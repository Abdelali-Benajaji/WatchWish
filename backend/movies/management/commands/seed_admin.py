from django.core.management.base import BaseCommand
from movies.models import User

class Command(BaseCommand):
    help = 'Seeds the database with an admin user'

    def handle(self, *args, **options):
        admin_username = 'admin'
        admin_email = 'admin@watchwish.com'
        admin_password = 'admin123'
        
        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(self.style.WARNING(f'Admin user "{admin_username}" already exists'))
            return
        
        admin_user = User.objects.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user'))
        self.stdout.write(f'Username: {admin_username}')
        self.stdout.write(f'Email: {admin_email}')
        self.stdout.write(f'Password: {admin_password}')
        self.stdout.write(f'Role: admin')
