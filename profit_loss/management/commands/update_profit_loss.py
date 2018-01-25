from django.core.management.base import BaseCommand

from profit_loss.models import UpdateOrderProfit


class Command(BaseCommand):
    help = 'Updates Print Audit'

    def handle(self, *args, **options):
        UpdateOrderProfit()
