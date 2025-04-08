"""Tools for calculating FBA profit/loss."""

import csv
import time
from dataclasses import dataclass

import requests
from amapi import request
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils import timezone

from inventory.models import BaseProduct
from stcadmin import settings

from .fba import FBARegion
from .fba_order import FBAOrder


class FBAProfitFile(models.Model):
    """Model for FBA profit imports."""

    import_date = models.DateField(default=timezone.now)

    class FBAProfitFileManager(models.Manager):
        """Model manager for the FBAProfitFile model."""

        def update_from_exports(self):
            """Update FBAFee records."""
            exports = [FeeEstimateFileUK(), FeeEstimateFileUS()]
            with transaction.atomic():
                import_record = self.create()
                objects = []
                for export in exports:
                    for fee in export.fees:
                        obj = self.create_from_fee(import_record, fee)
                        if obj:
                            objects.append(obj)
                FBAProfit.objects.bulk_create(objects)

        def create_from_fee(self, import_record, fee):
            """Create an FBAProfit object from fees."""
            try:
                return _FBAProfitCalculation(fee).to_object(import_record)
            except ObjectDoesNotExist:
                return None

    objects = FBAProfitFileManager()

    class Meta:
        """Metaclass for the FBAProfitFile model."""

        verbose_name = "FBA Profit File"
        verbose_name_plural = "FBA Profit Files"
        get_latest_by = "import_date"
        ordering = ("import_date",)

    def __str__(self):
        return f"FBA Profit File {self.import_date}"


class FBAProfit(models.Model):
    """Model for FBA profit calculations."""

    import_record = models.ForeignKey(
        FBAProfitFile, on_delete=models.CASCADE, related_name="product_profit"
    )
    product = models.ForeignKey(
        BaseProduct, on_delete=models.CASCADE, related_name="fba_profit"
    )
    region = models.ForeignKey(
        FBARegion, on_delete=models.CASCADE, related_name="fba_profit"
    )
    last_order = models.ForeignKey(
        FBAOrder, on_delete=models.CASCADE, related_name="fba_profit"
    )
    exchange_rate = models.FloatField()
    channel_sku = models.CharField(max_length=255)
    asin = models.CharField(max_length=10)
    listing_name = models.TextField()
    sale_price = models.PositiveIntegerField()
    referral_fee = models.PositiveIntegerField()
    closing_fee = models.PositiveIntegerField()
    handling_fee = models.PositiveIntegerField()
    placement_fee = models.PositiveIntegerField()
    purchase_price = models.PositiveIntegerField()
    shipping_price = models.PositiveIntegerField()
    profit = models.IntegerField()

    class FBAProfitManager(models.Manager):
        """Manager for the FBAProfit model."""

        def current(self):
            """Return a queryset of profit records from the latest import."""
            latest_import = FBAProfitFile.objects.latest()
            return self.get_queryset().filter(import_record=latest_import)

    objects = FBAProfitManager()

    GBP_CURRENCY_SYMBOL = "£"

    class Meta:
        """Meta class for the FBAProfit model."""

        verbose_name = "FBA Profit"
        verbose_name_plural = "FBA Profit"

    def __str__(self):
        return f"{self.product.sku} - {self.import_record.import_date}"

    @staticmethod
    def _format_price(symbol, value):
        _value = value / 100
        if value < 0:
            sign = "-"
        else:
            sign = " "
        return f"{sign}{symbol}{(abs(_value)):.2f}"

    def _local_price(self, value):
        return self._format_price(
            self.region.currency.symbol, value / self.exchange_rate
        )

    def _gbp_price(self, value):
        return self._format_price(self.GBP_CURRENCY_SYMBOL, value)

    def sale_price_gbp(self):
        """Return the sale price in GBP as a formatted string."""
        return self._gbp_price(self.sale_price)

    def sale_price_local(self):
        """Return the sale price in local currency as a formatted string."""
        return self._local_price(self.sale_price)

    def referral_fee_gbp(self):
        """Return the referral fee in GBP as a formatted string."""
        return self._gbp_price(self.referral_fee)

    def referral_fee_local(self):
        """Return the referral fee in local currency as a formatted string."""
        return self._local_price(self.referral_fee)

    def closing_fee_gbp(self):
        """Return the closing fee in GBP as a formatted string."""
        return self._gbp_price(self.closing_fee)

    def closing_fee_local(self):
        """Return the closing fee in local currency as a formatted string."""
        return self._local_price(self.closing_fee)

    def handling_fee_gbp(self):
        """Return the handling fee in GBP as a formatted string."""
        return self._gbp_price(self.handling_fee)

    def handling_fee_local(self):
        """Return the handling fee in local currency as a formatted string."""
        return self._local_price(self.handling_fee)

    def placement_fee_gbp(self):
        """Return the placement fee in GBP as a formatted string."""
        return self._gbp_price(self.placement_fee)

    def placement_fee_local(self):
        """Return the placement fee in local currency as a formatted string."""
        return self._local_price(self.placement_fee)

    def purchase_price_gbp(self):
        """Return the purchase price in GBP as a formatted string."""
        return self._gbp_price(self.purchase_price)

    def purchase_price_local(self):
        """Return the purchase price in local currency as a formatted string."""
        return self._local_price(self.purchase_price)

    def shipping_price_gbp(self):
        """Return the shipping price in GBP as a formatted string."""
        return self._gbp_price(self.shipping_price)

    def shipping_price_local(self):
        """Return the shipping price in local currency as a formatted string."""
        return self._local_price(self.shipping_price)

    def profit_gbp(self):
        """Return the profit in GBP as a formatted string."""
        return self._gbp_price(self.profit)

    def profit_local(self):
        """Return the profit in local currency as a formatted string."""
        return self._local_price(self.profit)


@dataclass
class _FBAFee:
    channel_sku: str
    asin: str
    country: str
    listing_name: str
    selling_price: int
    total_fee: int
    referral_fee: int
    closing_fee: int
    handling_fee: int


class _FBAProfitCalculation:
    """Calculate profit for an FBA order."""

    def __init__(self, fee):
        self.fee = fee
        self.last_order = self._get_order_for_fee()
        self.product = self.last_order.product
        self.region = FBARegion.objects.get(country__ISO_code=fee.country)
        self.exchange_rate = float(self.region.currency.exchange_rate())
        self.placement_fee = self._to_gbp(self.region.placement_fee)
        self.sale_price = self._to_gbp(self.fee.selling_price)
        self.referral_fee = self._to_gbp(self.fee.referral_fee)
        self.closing_fee = self._to_gbp(self.fee.closing_fee)
        self.handling_fee = self._to_gbp(self.fee.handling_fee)
        self.purchase_price = int(self.product.purchase_price * 100)
        self.shipping_price = self.calculate_shipping_price()
        self.profit = self._profit()

    def calculate_shipping_price(self):
        """Return the caclulated price to post to FBA."""
        quantity_sent = self.last_order.quantity_sent
        shipped_weight = self.product.weight_grams * quantity_sent
        return int(self.region.calculate_shipping(shipped_weight) / quantity_sent)

    def _get_order_for_fee(self):
        return (
            FBAOrder.objects.fulfilled()
            .filter(product_asin=self.fee.asin)
            .latest("closed_at")
        )

    def _to_gbp(self, value):
        return value * self.exchange_rate

    def _costs(self):
        return sum(
            (
                self.placement_fee,
                self.referral_fee,
                self.closing_fee,
                self.handling_fee,
                self.purchase_price,
                self.shipping_price,
            )
        )

    def _profit(self):
        return self.sale_price - self._costs()

    def to_object(self, import_record):
        return FBAProfit(
            import_record=import_record,
            product=self.product,
            region=self.region,
            last_order=self.last_order,
            exchange_rate=self.exchange_rate,
            channel_sku=self.fee.channel_sku,
            asin=self.fee.asin,
            listing_name=self.fee.listing_name,
            sale_price=self.sale_price,
            referral_fee=self.referral_fee,
            closing_fee=self.closing_fee,
            handling_fee=self.handling_fee,
            placement_fee=self.placement_fee,
            purchase_price=self.purchase_price,
            shipping_price=self.shipping_price,
            profit=self.profit,
        )


class BaseFeeEstimateFile:
    """Base class for reading Amazon FBA fee estimate files."""

    SKU = "sku"
    FNSKU = "fnsku"
    ASIN = "asin"
    COUNTRY = "amazon-store"
    NAME = "product-name"
    PRICE = "your-price"
    TOTAL_FEE = "estimated-fee-total"
    REFERRAL_FEE = "estimated-referral-fee-per-unit"
    CLOSING_FEE = "estimated-variable-closing-fee"
    HANDLING_FEE = "estimated-order-handling-fee-per-order"

    REPORT_TYPE = "GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA"
    timeout = 60

    def __init__(self):
        """Open and read an Amazon FBA fee file."""
        document = self.get_file()
        self.header, self.rows = self.read_file(document)
        self.fees = self._create_fba_fee_objects()

    def get_file(self):
        """Download and return a report file."""
        with self.session() as s:
            report_id = request.request_generate_report(
                session=s, report_type=self.REPORT_TYPE
            )
            time.sleep(self.timeout)
            document_id = request.request_document_id(s, report_id=report_id)
            document_url = request.request_document_url(s, document_id=document_id)
        document = requests.get(document_url).text
        return document

    def read_file(self, document):
        """
        Return the file header and row data.

        Returns:
            list[str]: The header row from the csv file.
            list[dict[str: Any]]: A list of dicts where each item is a row in the csv
                file as a dict of column headers and values.
        """
        rows = []
        reader = csv.reader(document.split("\n"), delimiter="\t")
        for i, row in enumerate(reader):
            if i == 0:
                header = row
            else:
                row_dict = {key: value for key, value in zip(header, row, strict=True)}
                if row_dict[self.COUNTRY] in self.countries:
                    rows.append(row_dict)
        return header, rows

    def _create_fba_fee_objects(self):
        return [self._create_fba_fee(row) for row in self.rows]

    def _create_fba_fee(self, row):
        return _FBAFee(
            channel_sku=row[self.SKU],
            asin=row[self.ASIN],
            country=row[self.COUNTRY],
            listing_name=row[self.NAME],
            selling_price=self._parse_currency_value(row[self.PRICE]),
            total_fee=self._parse_currency_value(row[self.TOTAL_FEE]),
            referral_fee=self._parse_currency_value(row[self.REFERRAL_FEE]),
            closing_fee=self._parse_currency_value(row[self.CLOSING_FEE]),
            handling_fee=self._parse_currency_value(row[self.HANDLING_FEE]),
        )

    def _parse_currency_value(self, value):
        if value == "--":
            return 0
        else:
            return int(float(value) * 100)


class FeeEstimateFileUK(BaseFeeEstimateFile):
    """Reader for UK Amazon FBA fee estimate files."""

    countries = ["GB"]
    session = settings.AmapiSessionUK


class FeeEstimateFileUS(BaseFeeEstimateFile):
    """Reader for US Amazon FBA fee estimate files."""

    countries = ["US"]
    session = settings.AmapiSessionUS
