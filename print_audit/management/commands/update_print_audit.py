"""Management commands for the Print Audit app."""

import logging
import sys

from ccapi import CCAPI
from django.core.management.base import BaseCommand
from print_audit.models import CloudCommerceOrder

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update print audit."""

    help = "Updates Print Audit"

    def handle(self, *args, **options):
        """Update print audit."""
        try:
            print_logs = CCAPI.get_print_queue()
            new_order_count = 0
            for print_log in print_logs:
                order_exists = CloudCommerceOrder.objects.filter(
                    order_id=print_log.order_id
                ).exists()
                if not order_exists:
                    CloudCommerceOrder.create_from_print_queue(print_log)
                    new_order_count += 1
            print(new_order_count, file=sys.stderr)
        except Exception as e:
            logger.error(
                "Admin Command Error: %s", " ".join(sys.argv), exc_info=sys.exc_info()
            )
            raise e
