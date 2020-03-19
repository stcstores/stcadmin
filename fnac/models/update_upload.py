"""Create an import file to create new products in FNAC."""

import csv
import io

from django.db import models

from .fnac_product import FnacProduct


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


def create_update_upload():
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
        return FnacProduct.objects.filter(created=True)

    def create(self):
        self.comment = Comment.objects.get_comment_text()
        rows = [self.HEADER]
        for product in self.get_products():
            rows.append(self.get_row_for_product(product))
        stream = io.StringIO()
        writer = csv.writer(stream, delimiter=";")
        writer.writerows(rows)
        return stream
