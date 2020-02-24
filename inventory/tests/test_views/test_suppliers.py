from unittest.mock import Mock, patch

from django.shortcuts import reverse

from inventory import models
from inventory.tests import fixtures
from stcadmin.tests.stcadmin_test import ViewTests

from .test_views import InventoryViewTest


class TestSuppliersView(
    InventoryViewTest, fixtures.ProductRequirementsFixture, ViewTests
):
    fixtures = fixtures.ProductRequirementsFixture.fixtures
    URL = "/inventory/suppliers/suppliers/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.supplier.name)
        self.assertQuerysetEqual(
            response.context["suppliers"], map(repr, models.Supplier.objects.all())
        )


class TestSupplierView(
    InventoryViewTest, fixtures.ProductRequirementsFixture, ViewTests
):
    fixtures = fixtures.ProductRequirementsFixture.fixtures

    def get_URL(self):
        return f"/inventory/suppliers/{self.supplier.id}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.supplier.name)
        self.assertEqual(response.context["supplier"], self.supplier)
        self.assertQuerysetEqual(
            response.context["contacts"],
            map(repr, models.SupplierContact.objects.filter(supplier=self.supplier)),
        )
        self.assertContains(response, self.supplier_contact.name)


class TestCreateSupplierView(
    InventoryViewTest, fixtures.ProductRequirementsFixture, ViewTests
):
    fixtures = fixtures.ProductRequirementsFixture.fixtures
    URL = "/inventory/suppliers/create_supplier/"

    def factories_response(self, factories):
        response = []
        for name, id in factories:
            mock = Mock(name=name, id=id)
            mock.name = name
            response.append(mock)
        return response

    def make_post_request(self):
        form_data = {"name": "Supplier Name"}
        return self.client.post(self.get_URL(), form_data)

    @patch("inventory.models.suppliers.CCAPI")
    def test_get_method(self, mock_CCAPI):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Name")
        self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.models.suppliers.CCAPI")
    @patch("inventory.models.product_options.CCAPI")
    def test_post_method(self, mock_product_options_CCAPI, mock_suppliers_CCAPI):
        name = "New Supplier"
        factories = (("Socks R Us", "86166"), ("shoeseller", "843135"))
        mock_suppliers_CCAPI.get_factories.return_value = self.factories_response(
            factories
        )
        mock_suppliers_CCAPI.create_factory.return_value = Mock(name=name, id="513478")
        mock_product_options_CCAPI.create_option_value.return_value = "943154"
        self.assertFalse(models.Supplier.objects.filter(name=name).exists())
        response = self.client.post(self.URL, {"name": name})
        mock_suppliers_CCAPI.get_factories.assert_called_once()
        mock_suppliers_CCAPI.create_factory.assert_called_once_with(name)
        mock_product_options_CCAPI.create_option_value.assert_called_once_with(
            models.Supplier.PRODUCT_OPTION_ID, name
        )
        new_supplier = models.Supplier.objects.get(name=name)
        self.assertEqual(new_supplier.factory_ID, "513478")
        self.assertEqual(new_supplier.product_option_value_ID, "943154")
        self.assertRedirects(
            response,
            new_supplier.get_absolute_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        self.assertEqual(2, len(mock_suppliers_CCAPI.mock_calls))
        self.assertEqual(1, len(mock_product_options_CCAPI.mock_calls))

    @patch("inventory.models.suppliers.CCAPI")
    @patch("inventory.models.product_options.CCAPI")
    def test_create_supplier_with_existing_factory(
        self, mock_product_options_CCAPI, mock_suppliers_CCAPI
    ):
        name = "Another Supplier"
        factories = (
            ("Socks R Us", "86166"),
            ("shoeseller", "843135"),
            (name, "781546"),
        )
        mock_suppliers_CCAPI.get_factories.return_value = self.factories_response(
            factories
        )
        mock_product_options_CCAPI.create_option_value.return_value = "245578"
        self.client.post(reverse("inventory:create_supplier"), {"name": name})
        mock_product_options_CCAPI.create_option_value.assert_called_once_with(
            models.Supplier.PRODUCT_OPTION_ID, name
        )
        mock_suppliers_CCAPI.get_factories.assert_called_once()
        new_supplier = models.Supplier.objects.get(name=name)
        self.assertEqual(new_supplier.factory_ID, "781546")
        self.assertEqual(new_supplier.product_option_value_ID, "245578")
        self.assertEqual(1, len(mock_suppliers_CCAPI.mock_calls))
        self.assertEqual(1, len(mock_product_options_CCAPI.mock_calls))


class TestToggleSupplierActiveView(InventoryViewTest, ViewTests):
    fixtures = ("inventory/supplier",)

    def get_URL(self, supplier_id=1):
        return f"/inventory/toggle_supplier_active/{supplier_id}/"

    def test_get_method(self):
        supplier = models.Supplier.objects.get(id=1)
        response = self.make_get_request()
        self.assertRedirects(
            response,
            supplier.get_absolute_url(),
            status_code=302,
            target_status_code=200,
        )

    def test_post_method(self):
        supplier = models.Supplier.objects.get(id=1)
        response = self.make_post_request()
        self.assertRedirects(
            response,
            supplier.get_absolute_url(),
            status_code=302,
            target_status_code=200,
        )

    def test_set_inactive(self):
        supplier = models.Supplier.objects.get(id=1)
        self.assertFalse(supplier.inactive)
        self.make_get_request()
        supplier.refresh_from_db()
        self.assertTrue(supplier.inactive)

    def test_set_active(self):
        supplier = models.Supplier.objects.get(id=1)
        supplier = supplier
        supplier.inactive = True
        supplier.save()
        self.make_get_request()
        supplier.refresh_from_db()
        self.assertFalse(supplier.inactive)


class TestCreateSupplierContactView(InventoryViewTest, ViewTests):
    fixtures = ("inventory/supplier",)
    name = "Joe Bloggs"
    phone = "9584612455"
    email = "noeone@nowhere.com"
    notes = "Call in the morning"

    def get_URL(self, supplier_id=1):
        return f"/inventory/suppliers/create_contact/{supplier_id}/"

    def test_get_method(self):
        supplier = models.Supplier.objects.get(id=1)
        response = self.make_get_request()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, supplier.name)
        self.assertContains(response, supplier.pk)
        self.assertContains(response, "Supplier")
        self.assertContains(response, "Name")
        self.assertContains(response, "Phone")
        self.assertContains(response, "Email")
        self.assertContains(response, "Notes")

    def test_post_method(self):
        supplier = models.Supplier.objects.get(id=1)
        response = self.client.post(
            self.get_URL(),
            {
                "supplier": supplier.pk,
                "name": self.name,
                "phone": self.phone,
                "email": self.email,
                "notes": self.notes,
            },
        )
        new_supplier_contact = models.SupplierContact.objects.get(name=self.name)
        self.assertRedirects(
            response,
            new_supplier_contact.get_absolute_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        self.assertEqual(new_supplier_contact.name, self.name)
        self.assertEqual(new_supplier_contact.phone, self.phone)
        self.assertEqual(new_supplier_contact.email, self.email)
        self.assertEqual(new_supplier_contact.notes, self.notes)

    def test_create_without_details(self):
        supplier = models.Supplier.objects.get(id=1)
        self.client.post(self.get_URL(), {"supplier": supplier.pk, "name": self.name})
        new_supplier_contact = models.SupplierContact.objects.get(name=self.name)
        self.assertEqual(new_supplier_contact.name, self.name)
        self.assertIsNone(new_supplier_contact.phone)
        self.assertIsNone(new_supplier_contact.email)
        self.assertEqual(new_supplier_contact.notes, "")


class TestUpdateSupplierContactView(InventoryViewTest, ViewTests):
    fixtures = ("inventory/supplier",)
    name = "Joe Bloggs"
    phone = "9584612455"
    email = "noeone@nowhere.com"
    notes = "Call in the morning"

    def get_URL(self, supplier_id=1):
        return f"/inventory/suppliers/update_contact/{supplier_id}/"

    def test_get_method(self):
        supplier = models.Supplier.objects.get(id=1)
        contact = supplier.suppliercontact_set.all()[0]
        response = self.make_get_request()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Supplier")
        self.assertContains(response, "Name")
        self.assertContains(response, "Phone")
        self.assertContains(response, "Email")
        self.assertContains(response, "Notes")
        self.assertContains(response, contact.name)
        self.assertContains(response, contact.phone)
        self.assertContains(response, contact.email)
        self.assertContains(response, contact.notes)

    def test_post_method(self):
        supplier = models.Supplier.objects.get(id=1)
        contact = supplier.suppliercontact_set.all()[0]
        response = self.client.post(
            self.get_URL(),
            {
                "supplier": supplier.pk,
                "name": self.name,
                "phone": self.phone,
                "email": self.email,
                "notes": self.notes,
            },
        )
        contact.refresh_from_db()
        self.assertRedirects(
            response,
            contact.get_absolute_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        self.assertEqual(contact.name, self.name)
        self.assertEqual(contact.phone, self.phone)
        self.assertEqual(contact.email, self.email)
        self.assertEqual(contact.notes, self.notes)


class TestDeleteSupplierContactView(InventoryViewTest, ViewTests):
    fixtures = ("inventory/supplier",)

    def get_URL(self, supplier_id=1):
        return f"/inventory/suppliers/delete_contact/{supplier_id}/"

    def test_get_method(self):
        supplier = models.Supplier.objects.get(id=1)
        contact = supplier.suppliercontact_set.all()[0]
        response = self.make_get_request()
        self.assertContains(response, "Are you sure you want to delete")
        self.assertContains(response, supplier.name)
        self.assertContains(response, contact.name)
        self.assertContains(response, "Confirm")

    def test_post_method(self):
        supplier = models.Supplier.objects.get(id=1)
        contact = supplier.suppliercontact_set.all()[0]
        response = self.make_post_request()
        self.assertFalse(models.SupplierContact.objects.filter(id=contact.id).exists())
        self.assertRedirects(
            response,
            supplier.get_absolute_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
