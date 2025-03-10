from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from aap_api.models import ExcelData

class Command(BaseCommand):
    help = 'Setup permissions for admin users'

    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(ExcelData)
        permission = Permission.objects.get(
            codename='can_delete_null_records',
            content_type=content_type,
        )

        # Grant permission to all superusers
        for user in User.objects.filter(is_superuser=True):
            user.user_permissions.add(permission)
            self.stdout.write(f'Granted delete_null_records permission to {user.username}')