from django.core.management.base import BaseCommand
from spring_manifest.models import update_spring_orders


class Command(BaseCommand):
    help = 'Update Spring Manifest Orders'

    def handle(self, *args, **options):
        update_spring_orders()
