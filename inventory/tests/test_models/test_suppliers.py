from django.core.exceptions import ValidationError

from inventory import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestSupplierContactModel(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.supplier = models.Supplier.objects.create(
            name="Stock Inc", product_option_value_ID="165415", factory_ID="28493782"
        )
        cls.supplier_contact = models.SupplierContact.objects.create(
            supplier=cls.supplier,
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
