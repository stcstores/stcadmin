import logging
import sys

from django.core.management.base import BaseCommand

from profit_loss.models import UpdateOrderProfit

logger = logging.getLogger('management_commands')


class Command(BaseCommand):
    help = 'Updates Print Audit'

    def handle(self, *args, **options):
        try:
            UpdateOrderProfit()
        except Exception as e:
            logger.error(
                'Admin Command Error: %s', ' '.join(sys.argv),
                exc_info=sys.exc_info())
            raise e
