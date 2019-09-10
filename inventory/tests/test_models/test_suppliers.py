from django.core.exceptions import ValidationError
from django.test import TestCase

from inventory import models


class TestSupplierContactModel(TestCase):
    def setUp(self):
        super().setUp()
        self.supplier = models.Supplier.objects.create(
            name="Stock Inc", product_option_value_ID="165415"
        )
        self.supplier_contact = models.SupplierContact.objects.create(
            supplier=self.supplier,
            name="Jeff",
            email="jeff@stockinc.com",
            phone="0742156456",
            notes="A note about the supplier",
        )

    def tearDown(self):
        models.SupplierContact.objects.all().delete()
        models.Supplier.objects.all().delete()
        super().tearDown()

    def test_str_method(self):
        self.assertEqual(str(self.supplier_contact), "Stock Inc - Jeff")

    def test_str_method_wihtout_name(self):
        self.supplier_contact.name = None
        self.supplier_contact.save()
        self.assertEqual(str(self.supplier_contact), "Stock Inc")

    def test_clean_method(self):
        contact = models.SupplierContact(supplier=self.supplier)
        with self.assertRaises(ValidationError):
            contact.save()
