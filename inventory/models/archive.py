"""Methods for archiving products."""

from django.db.models import Count, Q

from linnworks.models import StockManager

from .product import BaseProduct


class Archiver:
    """Provides methods for archiving products."""

    @classmethod
    def get_product_queryset(cls):
        """Return products that are not archived, EOL and not in any active FBA orders."""
        return (
            BaseProduct.objects.filter(is_end_of_line=True, is_archived=False)
            .annotate(
                open_fba_orders=Count(
                    "fba_orders",
                    filter=Q(
                        Q(fba_orders__on_hold=True)
                        | Q(fba_orders__closed_at__isnull=True)
                    ),
                )
            )
            .exclude(open_fba_orders__gt=0)
        )

    @classmethod
    def filter_out_of_stock_products(cls, qs):
        """Return a queryset of products in qs that are out of stock."""
        chunks = [qs[i : i + 100] for i in range(0, qs.count(), 100)]
        to_archive = []
        for chunk in chunks:
            chunk_stock_levels = StockManager.get_stock_levels(chunk)
            for product in chunk:
                if chunk_stock_levels[product.sku].available == 0:
                    to_archive.append(product.id)
        return qs.filter(id__in=to_archive)

    @classmethod
    def get_archivable_products(cls):
        """Return a queryset of products that are ready to be archived."""
        qs = cls.get_product_queryset()
        qs = cls.filter_out_of_stock_products(qs)
        return qs

    @classmethod
    def archive_products(cls):
        """Update archivable products."""
        for product in cls.get_archivable_products():
            product.set_archived()
