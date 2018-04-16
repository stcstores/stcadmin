from django.core.management.base import BaseCommand
from inventory.models import check_location_integrity


class Command(BaseCommand):
    help = 'Check integrity of product location database.'

    def handle(self, *args, **options):
        check_location_integrity()
