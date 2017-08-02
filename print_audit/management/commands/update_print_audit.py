from django.core.management.base import BaseCommand
from print_audit.models import CloudCommerceOrder

from ccapi import CCAPI


class Command(BaseCommand):
    help = 'Updates Print Audit'

    def handle(self, *args, **options):
        print_logs = CCAPI.get_print_queue()
        new_order_count = 0
        for print_log in print_logs:
            order_exists = CloudCommerceOrder.objects.filter(
                order_id=print_log.order_id).exists()
            if not order_exists:
                CloudCommerceOrder.create_from_print_queue(print_log)
                new_order_count += 1
        print(new_order_count)
