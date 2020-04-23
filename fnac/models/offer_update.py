"""Create an import file to create new products in FNAC."""

import csv
import io

from django.db import models, transaction
from django.utils import timezone

from .fnac_product import FnacProduct


class OfferUpdateManager(models.Manager):
    """Manager for the OfferUpdate model."""

    def is_in_progress(self):
        """Return True if there is an export being created, otherwise False."""
        return self.get_queryset().filter(status=OfferUpdate.IN_PROGRESS).exists()

    def get_filename(self):
        """Return a filename for an export."""
        date_string = timezone.now().strftime("%Y-%m-%d")
        return f"fnac_offer_update_{date_string}.csv"

    def create_export(self):
        """Create a missing information export."""
        with transaction.atomic():
            if self.is_in_progress():
                raise OfferUpdate.AlreadyInProgress()
            export = self.create()
        try:
            export_file = create_offer_update_export()
            export.export.save(self.get_filename(), export_file)
        except Exception as e:
            export.status = export.ERROR
            export.save()
            raise e
        else:
            export.status = export.COMPLETE
        export.save()


class OfferUpdate(models.Model):
    """Model for offer update export files."""

    class AlreadyInProgress(Exception):
        """Exception raised when an export is created with one already in progress."""

        def __init__(self, *args, **kwargs):
            """Raise the exception."""
            return super().__init__(self, "An export is already being created.")

    COMPLETE = "complete"
    ERROR = "error"
    IN_PROGRESS = "in_progress"
    STATUSES = ((COMPLETE, "Complete"), (ERROR, "Error"), (IN_PROGRESS, "In Progress"))

    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUSES, default=IN_PROGRESS)
    export = models.FileField(upload_to="fnac/offer_update_exports/", null=True)

    objects = OfferUpdateManager()


class CommentManager(models.Manager):
    """Manager for the FnacComment model."""

    def get_comment(self):
        """Return the comment object."""
        comment, _ = self.get_or_create(id=1)
        return comment

    def set_comment_text(self, text):
        """Update the FNAC comment."""
        comment = self.get_comment()
        comment.comment = text
        comment.save()

    def get_comment_text(self):
        """Return the comment."""
        comment = self.get_comment()
        return comment.comment


class Comment(models.Model):
    """Model for storing the FNAC shipping comment."""

    comment = models.TextField()

    objects = CommentManager()


def create_offer_update_export():
    """Return a new product upload file."""
    return _ProductUpdate().create()


class _ProductUpdate:
    BARCODE = "id-produit"
    SKU = "sku-vendeur"
    PRICE = "prix"
    STOCK = "stock"
    CONDITION = "condition"
    COMMENT = "comment"
    CATEGORY = "logistic-type-id"
    IS_SHIPPING_FREE = "is-shipping-free"

    HEADER = [
        BARCODE,
        SKU,
        PRICE,
        STOCK,
        CONDITION,
        COMMENT,
        "treatment",
        "type-id-produit",
        "commentaire-interne",
        "numero-vitrine",
        "constructeur",
        CATEGORY,
        IS_SHIPPING_FREE,
        "promotion-type",
        "promotion-uid",
        "promotion-starts-at",
        "promotion-ends-at",
        "promotion-discount-type",
        "promotion-discount-value",
        "promotion-trigger-cart-type",
        "promotion-trigger-cart-value",
        "promotion-trigger-customer-type",
        "promotion-trigger-promotion-code",
        "promotion-sales-period-reference",
    ]

    def get_row_for_product(self, product):
        row = [""] * len(self.HEADER)
        data = {
            self.SKU: product.sku,
            self.BARCODE: product.barcode,
            self.STOCK: product.stock_level,
            self.CONDITION: 11,
            self.PRICE: f"{float(product.price)/100:.2f}",
            self.CATEGORY: "201",
            self.COMMENT: self.comment,
            self.IS_SHIPPING_FREE: "0",
        }
        for key, value in data.items():
            row[self.HEADER.index(key)] = value
        return row

    def get_products(self):
        return FnacProduct.objects.filter(created=True, price__isnull=False)

    def create(self):
        self.comment = Comment.objects.get_comment_text()
        rows = [self.HEADER]
        for product in self.get_products():
            rows.append(self.get_row_for_product(product))
        stream = io.StringIO()
        writer = csv.writer(stream, delimiter=";")
        writer.writerows(rows)
        return stream
