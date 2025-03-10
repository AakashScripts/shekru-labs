from django.core.management.base import BaseCommand
from aap_api.models import ExcelData

class Command(BaseCommand):
    help = 'Sets visibility for all ExcelData records'

    def handle(self, *args, **options):
        updated = ExcelData.objects.update(is_visible=True)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully made {updated} records visible')
        )