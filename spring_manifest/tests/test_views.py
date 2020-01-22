from unittest.mock import Mock, patch

from django.contrib.auth.models import Group
from django.core import mail
from django.urls import reverse_lazy

from spring_manifest import models, views
from stcadmin import settings
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class ManifestViewTest(STCAdminTest):
    group_name = "manifests"

    def setUp(self):
        self.create_user()
        group, _ = Group.objects.get_or_create(name=self.group_name)
        group.user_set.add(self.user)
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)


class TestManifestListView(ManifestViewTest, ViewTests):
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
    URL = "/spring_manifest/manifest_list/"
    template = "spring_manifest/manifest_list.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("current_manifests", response.context)
        self.assertEqual(
            list(models.Manifest.unfiled.all()),
            list(response.context["current_manifests"]),
        )
        self.assertIn("previous_manifests", response.context)
        self.assertEqual(
            list(models.Manifest.filed.all()[:50]),
            list(response.context["previous_manifests"]),
        )
        self.assertIn("unmanifested_orders", response.context)
        self.assertEqual(
            list(models.ManifestOrder.unmanifested.all()),
            list(response.context["unmanifested_orders"]),
        )
        self.assertIn("update", response.context)
        self.assertEqual(models.get_manifest_update(), response.context["update"])


class TestManifestView(ManifestViewTest, ViewTests):
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
    template = "spring_manifest/manifest.html"

    def get_URL(self, manifest_ID=None):
        if manifest_ID is None:
            manifest_ID = 1
        return f"/spring_manifest/manifest/{manifest_ID}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("manifest", response.context)
        manifest = models.Manifest.objects.get(id=1)
        self.assertEqual(manifest, response.context["manifest"])
        self.assertIn("orders", response.context)
        orders = manifest.manifestorder_set.all().order_by("dispatch_date")
        self.assertEqual(list(orders), list(response.context["orders"]))
        self.assertIn("services", response.context)
        services = {
            service.name: len([order for order in orders if order.service == service])
            for service in models.ManifestService.enabled_services.all()
        }
        self.assertDictEqual(services, response.context["services"])
        self.assertIn("update", response.context)
        self.assertEqual(models.get_manifest_update(), response.context["update"])

    def test_returns_404_for_invalid_manifest_id(self):
        response = self.client.get(self.get_URL(manifest_ID="999999"))
        self.assertEqual(404, response.status_code)


class TestCanceledOrdersView(ManifestViewTest, ViewTests):
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
    template = "spring_manifest/canceled_orders.html"
    URL = "/spring_manifest/canceled_orders/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("unmanifested_orders", response.context)
        unmanifested_orders = models.ManifestOrder.objects.filter(
            manifest__isnull=True, canceled=False
        )
        self.assertEqual(
            list(unmanifested_orders), list(response.context["unmanifested_orders"]),
        )
        self.assertIn("canceled_orders", response.context)
        canceled_orders = models.ManifestOrder.canceled_orders.filter(
            manifest__isnull=True, canceled=True
        )
        self.assertEqual(
            list(canceled_orders), list(response.context["canceled_orders"]),
        )


class TestOrderExistsView(ManifestViewTest):
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
    URL = "/spring_manifest/order_exists/"

    def test_post_method(self):
        order = models.ManifestOrder.objects.get(id=1)
        response = self.client.post(self.URL, {"order_id": order.order_id})
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            reverse_lazy("spring_manifest:update_order", kwargs={"order_pk": order.id}),
            response.content.decode("utf8"),
        )

    def test_non_existant_order(self):
        response = self.client.post(self.URL, {"order_id": "9999999"})
        self.assertEqual(200, response.status_code)
        self.assertEqual("0", response.content.decode("utf8"))


class TestUpdateManifestView(ManifestViewTest, ViewTests):
    URL = "/spring_manifest/update_manifest/"

    @patch("spring_manifest.views.views.time")
    @patch("spring_manifest.views.views.threading")
    def test_get_method(self, mock_threading, mock_time):
        mock_thread = Mock()
        mock_threading.Thread.return_value = mock_thread
        response = self.client.get(
            self.URL, {"return": "/spring_manifest/manifest_list/"}
        )
        mock_time.sleep.assert_called_once_with(1)
        mock_threading.Thread.assert_called_once_with(
            target=models.update_manifest_orders
        )
        mock_thread.setDaemon.assert_called_once_with(True)
        mock_thread.start.assert_called_once()
        self.assertRedirects(response, "/spring_manifest/manifest_list/")


class TestSendSecuredMailManifestView(ManifestViewTest, ViewTests):
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
    URL = "/spring_manifest/send_secured_mail_manifest_files/"

    @patch("spring_manifest.views.views.SecuredMailManifestFile")
    @patch("spring_manifest.views.views.models")
    def test_post_method(self, mock_models, mock_SecuredMailManifestFile):
        manifest_file = Mock(
            open=Mock(return_value=Mock(read=Mock(return_value=b"file contents"))),
        )
        manifest_file.name = "manifest_file.xlsx"
        docket_file = Mock(
            name="docket_file.xlsx",
            open=Mock(return_value=Mock(read=Mock(return_value=b"file contents"))),
        )
        docket_file.name = "docket_file.xlsx"
        mock_manifest = Mock(
            status=models.Manifest.UNFILED,
            manifest_file=manifest_file,
            docket_file=docket_file,
            id="4",
            files_sent=False,
        )
        mock_models.Manifest.objects = Mock(get=Mock(return_value=mock_manifest))
        self.assertEqual(len(mail.outbox), 0)
        number_of_bags = "37"
        response = self.client.post(
            self.URL,
            {"number_of_bags": number_of_bags, "manifest_id": mock_manifest.id},
        )
        self.assertRedirects(
            response,
            reverse_lazy(
                "spring_manifest:manifest", kwargs={"manifest_id": mock_manifest.id}
            ),
            fetch_redirect_response=False,
        )
        mock_SecuredMailManifestFile.add_bag_number.assert_called_once_with(
            mock_manifest, number_of_bags
        )
        self.assertEqual(len(mail.outbox), 2)
        manifest_email, docket_email = mail.outbox
        self.check_manifest_email(mock_manifest, manifest_email)
        self.check_docket_email(mock_manifest, docket_email)

    def check_manifest_email(self, mock_manifest, manifest_email):
        self.assertEqual(
            f"Seaton Trading Company Manifest {mock_manifest}", manifest_email.subject
        )
        self.assertEqual(
            [settings.SECURED_MAIL_MANIFEST_EMAIL_ADDRESS], manifest_email.to
        )
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, manifest_email.from_email)
        self.assertEqual([settings.DEFAULT_FROM_EMAIL], manifest_email.reply_to)
        self.assertEqual(
            [
                (
                    "manifest_file.xlsx",
                    b"file contents",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            ],
            manifest_email.attachments,
        )

    def check_docket_email(self, mock_manifest, docket_email):
        self.assertEqual(
            f"Seaton Trading Company Docket {mock_manifest}", docket_email.subject
        )
        self.assertEqual([settings.SECURED_MAIL_DOCKET_EMAIL_ADDRESS], docket_email.to)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, docket_email.from_email)
        self.assertEqual([], docket_email.reply_to)
        self.assertEqual(
            [
                (
                    "docket_file.xlsx",
                    b"file contents",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            ],
            docket_email.attachments,
        )


class TestFileManifestView(ManifestViewTest, ViewTests):
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

    def get_URL(self, manifest_ID=None):
        if manifest_ID is None:
            manifest_ID = models.Manifest.objects.get(status=models.Manifest.UNFILED).id
        return f"/spring_manifest/file_manifest/{manifest_ID}/"

    @patch("spring_manifest.views.views.time")
    @patch("spring_manifest.views.views.threading")
    def test_get_method(self, mock_threading, mock_time):
        manifest = models.Manifest.objects.get(status=models.Manifest.UNFILED)
        mock_thread = Mock()
        mock_threading.Thread.return_value = mock_thread
        response = self.make_get_request()
        mock_time.sleep.assert_called_once_with(3)
        mock_threading.Thread.assert_called_once_with(
            target=views.FileManifestView.file_manifest, args=[manifest]
        )
        mock_thread.setDaemon.assert_called_once_with(True)
        mock_thread.start.assert_called_once()
        self.assertRedirects(
            response,
            reverse_lazy(
                "spring_manifest:manifest", kwargs={"manifest_id": manifest.id},
            ),
        )

    @patch("spring_manifest.views.views.time")
    @patch("spring_manifest.views.views.threading")
    def test_invalid_manifest_ID(self, mock_threading, mock_time):
        response = self.client.get(self.get_URL(manifest_ID=9999))
        self.assertEqual(404, response.status_code)
        mock_threading.Thread.assert_not_called()
        mock_time.sleep.assert_not_called()

    @patch("spring_manifest.views.views.time")
    @patch("spring_manifest.views.views.threading")
    def test_filed_manifest(self, mock_threading, mock_time):
        response = self.client.get(self.get_URL(manifest_ID=1), follow=True)
        self.assertEqual(200, response.status_code)
        mock_threading.Thread.assert_not_called()
        mock_time.sleep.assert_not_called()
        self.assertIn("messages", response.context)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Manifest already filed.")

    @patch("spring_manifest.views.views.FileSecuredMailManifest")
    def test_file_manifest(self, mockFileSecuredMailManifest):
        manifest = Mock(manifest_type=Mock())
        manifest.manifest_type.name = "Secured Mail"
        views.FileManifestView.file_manifest(manifest)
        mockFileSecuredMailManifest.assert_called_once_with(manifest)

    @patch("spring_manifest.views.views.FileSecuredMailManifest")
    def test_file_manifest_with_invalid_manifest_type(
        self, mockFileSecuredMailManifest
    ):
        manifest = Mock(manifest_type=Mock())
        manifest.manifest_type.name = "Invalid Manifest Type"
        with self.assertRaises(Exception):
            views.FileManifestView.file_manifest(manifest)
        mockFileSecuredMailManifest.assert_not_called()


class TestUpdateOrderView(ManifestViewTest, ViewTests):
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
    template = "spring_manifest/update_order.html"

    def get_URL(self, order_id=None):
        if order_id is None:
            order_id = 1
        return f"/spring_manifest/update_order/{order_id}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("order", response.context)
        self.assertEqual(
            response.context["order"], models.ManifestOrder.objects.get(id=1)
        )

    def test_post_method(self):
        order = models.ManifestOrder.objects.get(id=1)
        country = order.country
        service = order.service
        manifest = models.get_manifest_by_service(service)
        response = self.client.post(
            self.get_URL(), {"country": country.id, "service": service.id}
        )
        self.assertRedirects(
            response,
            reverse_lazy("spring_manifest:update_order", kwargs={"order_pk": order.id}),
            fetch_redirect_response=False,
        )
        order.refresh_from_db()
        self.assertEqual(country, order.country)
        self.assertEqual(service, order.service)
        self.assertFalse(order.canceled)
        self.assertEqual(manifest, order.manifest)

    def test_return_redirect_with_manifest(self):
        order = models.ManifestOrder.objects.get(id=1)
        order.save()
        response = self.client.post(
            self.get_URL(),
            {"country": order.country.id, "service": order.service.id, "return": True},
        )
        order.refresh_from_db()
        self.assertRedirects(
            response,
            reverse_lazy(
                "spring_manifest:manifest", kwargs={"manifest_id": order.manifest_id},
            ),
            fetch_redirect_response=False,
        )

    def test_return_redirect_without_manifest(self):
        order = models.ManifestOrder.objects.get(id=1)
        order.save()
        response = self.client.post(
            self.get_URL(),
            {
                "country": order.country.id,
                "service": order.service.id,
                "return": True,
                "delay": True,
            },
        )
        self.assertRedirects(
            response,
            reverse_lazy("spring_manifest:canceled_orders"),
            fetch_redirect_response=False,
        )

    def test_split(self):
        order = models.ManifestOrder.objects.get(id=1)
        order.save()
        response = self.client.post(
            self.get_URL(),
            {"country": order.country.id, "service": order.service.id, "split": True},
        )
        self.assertRedirects(
            response,
            reverse_lazy("spring_manifest:split_order", kwargs={"order_pk": order.id}),
            fetch_redirect_response=False,
        )
