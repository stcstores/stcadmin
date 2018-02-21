from django.core.management.base import BaseCommand
from tabler import CSV, Table

from stock_check import models


class Command(BaseCommand):
    help = 'Update Stock Check Database'

    def add_arguments(self, parser):
        parser.add_argument('inventory_file_path', type=str)

    def handle(self, *args, **options):
        inventory_table_path = options.get('inventory_file_path')
        print(inventory_table_path)
        inventory_table = Table(inventory_table_path, table_type=CSV())
        models.update_stock_check(inventory_table)
