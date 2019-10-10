from django.utils import timezone

from inventory import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestBarcode(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.create_user()
        barcodes = [str(8114165461 + i) for i in range(50)]
        models.Barcode.objects.bulk_create(
            [models.Barcode(barcode=_) for _ in barcodes]
        )

    def test_create_barcode(self):
        barcode = models.Barcode.objects.get(barcode="8114165461")
        self.assertTrue(barcode.available)

    def test_mark_used_method(self):
        barcode = models.Barcode.objects.get(barcode="8114165461")
        barcode.mark_used(self.user, used_for="test_text")
        barcode = models.Barcode.objects.get(barcode="8114165461")
        self.assertFalse(barcode.available)
        self.assertIsNotNone(barcode.used_on)
        self.assertEqual(barcode.used_by, self.user)
        self.assertEqual(barcode.used_for, "test_text")

    def test_mark_used_on_used_barcode(self):
        barcode = models.Barcode.objects.get(barcode="8114165461")
        barcode.mark_used(self.user, used_for="test_text")
        barcode.save()
        with self.assertRaises(models.Barcode.BarcodeUsed):
            barcode.mark_used(self.user, used_for="test_text")

    def test_get_barcode_method(self):
        models.Barcode.objects.filter(barcode__in=["8114165461", "8114165462"]).update(
            available=False, used_by=self.user, used_on=timezone.now()
        )
        expected_barcode = models.Barcode.objects.get(barcode="8114165463")
        self.assertTrue(expected_barcode.available)
        returned_barcode = models.Barcode.get_barcode(self.user, used_for="test_text")
        self.assertEqual(returned_barcode, expected_barcode.barcode)
        barcode = models.Barcode.objects.get(barcode=returned_barcode)
        self.assertFalse(barcode.available)
        self.assertIsNotNone(barcode.used_on)
        self.assertEqual(barcode.used_by, self.user)
        self.assertEqual(barcode.used_for, "test_text")

    def test_get_barcodes_method(self):
        models.Barcode.objects.filter(barcode__in=["8114165461", "8114165462"]).update(
            available=False, used_by=self.user, used_on=timezone.now()
        )
        barcodes = models.Barcode.get_barcodes(
            count=5, user=self.user, used_for="test_text"
        )
        self.assertEqual(
            barcodes,
            ["8114165463", "8114165464", "8114165465", "8114165466", "8114165467"],
        )
        queryset = models.Barcode.objects.filter(barcode__in=barcodes)
        self.assertEqual(queryset.count(), 5)
        for barcode in queryset:
            self.assertFalse(barcode.available)
            self.assertIsNotNone(barcode.used_on)
            self.assertEqual(barcode.used_by, self.user)
            self.assertEqual(barcode.used_for, "test_text")

    def test_get_too_many_barcodes(self):
        with self.assertRaises(models.Barcode.NotEnoughBarcodes):
            models.Barcode.get_barcodes(count=500, user=self.user)
