from unittest.mock import Mock, patch

from django.shortcuts import reverse

from inventory import models

from .inventory_view_test import InventoryViewTest


class TestSuppliersViews:
    def setUp(self):
        super().setUp()
        self.supplier = models.Supplier.objects.create(
            name="Stock Inc", product_option_value_ID="165415", factory_ID="84135"
        )
        self.supplier_contact = models.SupplierContact.objects.create(
            supplier=self.supplier,
            name="Jeff",
            email="jeff@stockinc.com",
            phone="0742156456",
            notes="A note about the supplier",
        )

    def factories_response(self, factories):
        response = []
        for name, id in factories:
            mock = Mock(name=name, id=id)
            mock.name = name
            response.append(mock)
        return response


class TestSuppliersView(TestSuppliersViews, InventoryViewTest):
    def test_suppliers_view(self):
        response = self.client.get(reverse("inventory:suppliers"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.supplier.name)
        self.assertQuerysetEqual(
            response.context["suppliers"], map(repr, models.Supplier.objects.all())
        )


class TestSupplierView(TestSuppliersViews, InventoryViewTest):
    def test_supplier_view(self):
        response = self.client.get(
            reverse("inventory:supplier", kwargs={"pk": self.supplier.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.supplier.name)
        self.assertEqual(response.context["supplier"], self.supplier)
        self.assertQuerysetEqual(
            response.context["contacts"],
            map(repr, models.SupplierContact.objects.filter(supplier=self.supplier)),
        )
        self.assertContains(response, self.supplier_contact.name)


class TestCreateSupplierView(TestSuppliersViews, InventoryViewTest):
    @patch("inventory.models.suppliers.CCAPI")
    def test_create_supplier_get(self, mock_CCAPI):
        response = self.client.get(reverse("inventory:create_supplier"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Name")

    @patch("inventory.models.suppliers.CCAPI.get_factories")
    @patch("inventory.models.suppliers.CCAPI.create_factory")
    @patch("inventory.models.product_options.CCAPI.create_option_value")
    def test_create_supplier_post(
        self, mock_create_option_value, mock_create_factory, mock_get_factories
    ):
        name = "New Supplier"
        factories = (("Socks R Us", "86166"), ("shoeseller", "843135"))
        mock_get_factories.return_value = self.factories_response(factories)
        mock_create_factory.return_value = Mock(name=name, id="513478")
        mock_create_option_value.return_value = "943154"
        self.assertFalse(models.Supplier.objects.filter(name=name).exists())
        response = self.client.post(
            reverse("inventory:create_supplier"), {"name": name}
        )
        mock_get_factories.assert_called_once()
        mock_create_factory.assert_called_once_with(name)
        mock_create_option_value.assert_called_once_with(
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

    @patch("inventory.models.suppliers.CCAPI.get_factories")
    @patch("inventory.models.product_options.CCAPI.create_option_value")
    def test_create_supplier_with_existing_factory(
        self, mock_create_option_value, mock_get_factories
    ):
        name = "Another Supplier"
        factories = (
            ("Socks R Us", "86166"),
            ("shoeseller", "843135"),
            (name, "781546"),
        )
        mock_get_factories.return_value = self.factories_response(factories)
        mock_create_option_value.return_value = "245578"
        self.client.post(reverse("inventory:create_supplier"), {"name": name})
        mock_create_option_value.assert_called_once_with(
            models.Supplier.PRODUCT_OPTION_ID, name
        )
        mock_get_factories.assert_called_once()
        new_supplier = models.Supplier.objects.get(name=name)
        self.assertEqual(new_supplier.factory_ID, "781546")
        self.assertEqual(new_supplier.product_option_value_ID, "245578")


class TestToggleSupplierActiveView(TestSuppliersViews, InventoryViewTest):
    def test_set_inactive(self):
        supplier = models.Supplier.objects.get(id=self.supplier.id)
        self.assertFalse(supplier.inactive)
        response = self.client.get(
            reverse("inventory:toggle_supplier_active", kwargs={"pk": self.supplier.pk})
        )
        supplier = models.Supplier.objects.get(id=self.supplier.id)
        self.assertRedirects(
            response,
            supplier.get_absolute_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        self.assertTrue(supplier.inactive)

    def test_set_active(self):
        models.Supplier.objects.filter(id=self.supplier.id).update(inactive=True)
        response = self.client.get(
            reverse("inventory:toggle_supplier_active", kwargs={"pk": self.supplier.pk})
        )
        supplier = models.Supplier.objects.get(id=self.supplier.id)
        self.assertRedirects(
            response,
            supplier.get_absolute_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        self.assertFalse(supplier.inactive)


class TestCreateSupplierContactView(TestSuppliersViews, InventoryViewTest):
    name = "Joe Bloggs"
    phone = "9584612455"
    email = "noeone@nowhere.com"
    notes = "Call in the morning"

    def test_get_method(self):
        response = self.client.get(
            reverse(
                "inventory:create_supplier_contact",
                kwargs={"supplier_pk": self.supplier.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.supplier.name)
        self.assertContains(response, self.supplier.pk)
        self.assertContains(response, "Supplier")
        self.assertContains(response, "Name")
        self.assertContains(response, "Phone")
        self.assertContains(response, "Email")
        self.assertContains(response, "Notes")

    def test_post_method(self):
        response = self.client.post(
            reverse(
                "inventory:create_supplier_contact",
                kwargs={"supplier_pk": self.supplier.pk},
            ),
            {
                "supplier": self.supplier.pk,
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
        self.client.post(
            reverse(
                "inventory:create_supplier_contact",
                kwargs={"supplier_pk": self.supplier.pk},
            ),
            {"supplier": self.supplier.pk, "name": self.name},
        )
        new_supplier_contact = models.SupplierContact.objects.get(name=self.name)
        self.assertEqual(new_supplier_contact.name, self.name)
        self.assertIsNone(new_supplier_contact.phone)
        self.assertIsNone(new_supplier_contact.email)
        self.assertEqual(new_supplier_contact.notes, "")


class TestUpdateSupplierContactView(TestSuppliersViews, InventoryViewTest):
    name = "Joe Bloggs"
    phone = "9584612455"
    email = "noeone@nowhere.com"
    notes = "Call in the morning"

    def test_get_method(self):
        response = self.client.get(
            reverse(
                "inventory:update_supplier_contact",
                kwargs={"pk": self.supplier_contact.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Supplier")
        self.assertContains(response, "Name")
        self.assertContains(response, "Phone")
        self.assertContains(response, "Email")
        self.assertContains(response, "Notes")
        self.assertContains(response, self.supplier_contact.name)
        self.assertContains(response, self.supplier_contact.phone)
        self.assertContains(response, self.supplier_contact.email)
        self.assertContains(response, self.supplier_contact.notes)

    def test_post_method(self):
        response = self.client.post(
            reverse(
                "inventory:update_supplier_contact",
                kwargs={"pk": self.supplier_contact.pk},
            ),
            {
                "supplier": self.supplier.pk,
                "name": self.name,
                "phone": self.phone,
                "email": self.email,
                "notes": self.notes,
            },
        )
        supplier_contact = models.SupplierContact.objects.get(
            pk=self.supplier_contact.pk
        )
        self.assertRedirects(
            response,
            supplier_contact.get_absolute_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        self.assertEqual(supplier_contact.name, self.name)
        self.assertEqual(supplier_contact.phone, self.phone)
        self.assertEqual(supplier_contact.email, self.email)
        self.assertEqual(supplier_contact.notes, self.notes)


class TestDeleteSupplierContactView(TestSuppliersViews, InventoryViewTest):
    def test_get_method(self):
        response = self.client.get(
            reverse(
                "inventory:delete_supplier_contact",
                kwargs={"pk": self.supplier_contact.pk},
            )
        )
        self.assertContains(response, "Are you sure you want to delete")
        self.assertContains(response, self.supplier.name)
        self.assertContains(response, self.supplier_contact.name)
        self.assertContains(response, "Confirm")

    def test_post_method(self):
        response = self.client.post(
            reverse(
                "inventory:delete_supplier_contact",
                kwargs={"pk": self.supplier_contact.pk},
            )
        )
        self.assertFalse(
            models.SupplierContact.objects.filter(pk=self.supplier_contact.pk).exists()
        )
        self.assertRedirects(
            response,
            self.supplier.get_absolute_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
