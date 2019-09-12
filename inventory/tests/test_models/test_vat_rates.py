from django.core.exceptions import ValidationError
from django.test import TestCase

from inventory import models


class TestVATRate(TestCase):
    def test_maximum_percentage(self):
        VAT_rate = models.VATRate(VAT_rate_ID="5", name="Standard", percentage=1.1)
        with self.assertRaises(ValidationError):
            VAT_rate.full_clean()

    def test_minimum_percentage(self):
        VAT_rate = models.VATRate(VAT_rate_ID="5", name="Standard", percentage=-0.1)
        with self.assertRaises(ValidationError):
            VAT_rate.full_clean()

    def test_str_method(self):
        VAT_rate = models.VATRate.objects.create(
            VAT_rate_ID="5", name="Standard", percentage=0.5
        )
        self.assertEqual(str(VAT_rate), VAT_rate.name)
