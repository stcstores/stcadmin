from django.test import TestCase

from inventory import models


class TestBarcode(TestCase):
    def setUp(self):
        super().setUp()
        barcodes = ["8114165461", "8114165462", "8114165463", "8114165464"]
        models.Barcode.objects.bulk_create(
            [models.Barcode(barcode=_) for _ in barcodes]
        )

    def test_create_barcode(self):
        barcode = models.Barcode.objects.get(barcode="8114165461")
        self.assertFalse(barcode.used)

    def test_mark_used_method(self):
        barcode = models.Barcode.objects.get(barcode="8114165461")
        barcode.mark_used()
        barcode = models.Barcode.objects.get(barcode="8114165461")
        self.assertTrue(barcode.used)

    def test_mark_used_on_used_barcode(self):
        barcode = models.Barcode.objects.get(barcode="8114165461")
        barcode.used = True
        barcode.save()
        barcode.mark_used()
        barcode = models.Barcode.objects.get(barcode="8114165461")
        self.assertTrue(barcode.used)

    def test_get_barcode(self):
        models.Barcode.objects.filter(barcode__in=["8114165461", "8114165462"]).update(
            used=True
        )
        expected_barcode = models.Barcode.objects.get(barcode="8114165463")
        self.assertFalse(expected_barcode.used)
        returned_barcode = models.get_barcode()
        self.assertEqual(returned_barcode, expected_barcode.barcode)
        self.assertTrue(models.Barcode.objects.get(barcode="8114165463").used)
