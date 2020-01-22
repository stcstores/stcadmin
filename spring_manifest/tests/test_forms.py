from spring_manifest import forms, models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestUpdateOrderForm(STCAdminTest):
    fixtures = (
        "spring_manifest/secured_mail_destination",
        "spring_manifest/cloud_commerce_country_id",
        "spring_manifest/cloud_commerce_shipping_rule",
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/secured_mail_service",
        "spring_manifest/manifest",
        "spring_manifest/manifest_order",
        "spring_manifest/manifest_package",
        "spring_manifest/manifest_item",
    )

    def test_update_order_form(self):
        order = models.ManifestOrder.objects.get(id=1)
        country = order.country
        service = order.service
        manifest = models.get_manifest_by_service(service)
        form = forms.UpdateOrderForm(
            {"country": country, "service": service.id}, instance=order
        )
        self.assertTrue(form.is_valid())
        form.save()
        order.refresh_from_db()
        self.assertEqual(country, order.country)
        self.assertEqual(service, order.service)
        self.assertFalse(order.canceled)
        self.assertEqual(manifest, order.manifest)

    def test_delay_order(self):
        order = models.ManifestOrder.objects.get(id=1)
        country = order.country
        service = order.service
        self.assertIsNotNone(order.manifest)
        form = forms.UpdateOrderForm(
            {"country": country, "service": service.id, "delay": True}, instance=order
        )
        self.assertTrue(form.is_valid())
        form.save()
        order.refresh_from_db()
        self.assertEqual(country, order.country)
        self.assertEqual(service, order.service)
        self.assertFalse(order.canceled)
        self.assertIsNone(order.manifest)

    def test_cancel_order(self):
        order = models.ManifestOrder.objects.get(id=1)
        country = order.country
        service = order.service
        self.assertIsNotNone(order.manifest)
        form = forms.UpdateOrderForm(
            {"country": country, "service": service.id, "cancel": True}, instance=order
        )
        self.assertTrue(form.is_valid())
        form.save()
        order.refresh_from_db()
        self.assertEqual(country, order.country)
        self.assertEqual(service, order.service)
        self.assertTrue(order.canceled)
        self.assertIsNone(order.manifest)

    def test_uncancel(self):
        order = models.ManifestOrder.objects.get(id=1)
        country = order.country
        service = order.service
        manifest = models.get_manifest_by_service(service)
        order.mannifest = None
        order.canceled = True
        order.save()
        form = forms.UpdateOrderForm(
            {"country": country, "service": service.id, "uncancel": True},
            instance=order,
        )
        self.assertTrue(form.is_valid())
        form.save()
        order.refresh_from_db()
        self.assertEqual(country, order.country)
        self.assertEqual(service, order.service)
        self.assertFalse(order.canceled)
        self.assertEqual(manifest, order.manifest)

    def test_undelay(self):
        order = models.ManifestOrder.objects.get(id=1)
        country = order.country
        service = order.service
        manifest = models.get_manifest_by_service(service)
        order.canceled = True
        order.save()
        form = forms.UpdateOrderForm(
            {"country": country, "service": service.id, "undelay": True}, instance=order
        )
        self.assertTrue(form.is_valid())
        form.save()
        order.refresh_from_db()
        self.assertEqual(country, order.country)
        self.assertEqual(service, order.service)
        self.assertFalse(order.canceled)
        self.assertEqual(manifest, order.manifest)
