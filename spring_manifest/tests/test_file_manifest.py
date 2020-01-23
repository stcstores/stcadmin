import io
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import override_settings
from django.utils import timezone

from spring_manifest import models
from spring_manifest.views.file_manifest import securedmail
from spring_manifest.views.file_manifest.file_manifest import FileManifest
from spring_manifest.views.file_manifest.state_code import StateCode
from stcadmin.tests.stcadmin_test import STCAdminTest


def close_manifest(manifest):
    manifest.closed = True
    manifest.status = manifest.UNFILED
    manifest.save()


def mock_now():
    return timezone.make_aware(datetime(2019, 12, 21))


class TestStateCode(STCAdminTest):
    def test_state_code(self):
        self.assertEqual("AK", StateCode("alaska"))
        self.assertEqual("AK", StateCode("Alaska"))

    def test_invalid_state_code(self):
        self.assertIsNone(StateCode("non existant state"))


class TestFileManifest(STCAdminTest):
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

    @patch("spring_manifest.views.file_manifest.file_manifest.models.close_manifest")
    @patch(
        "spring_manifest.views.file_manifest.file_manifest.FileManifest.process_manifest"
    )
    def test_file_manifest(self, mock_process_manifest, mock_close_manifest):
        manifest = models.Manifest.objects.filter(closed=True)[0]
        FileManifest(manifest)
        self.assertEqual(manifest.IN_PROGRESS, manifest.status)
        self.assertEqual("", manifest.errors)
        mock_close_manifest.assert_called_once_with(manifest)
        mock_process_manifest.assert_called_once()

    @patch("spring_manifest.views.file_manifest.file_manifest.models.close_manifest")
    def test_error_closing_manifest(self, mock_close_manifest):
        manifest = models.Manifest.objects.filter(closed=True)[0]
        mock_close_manifest.side_effect = Exception
        with self.assertRaises(Exception):
            FileManifest(manifest)
        self.assertEqual("Manifest did not close.", manifest.errors)
        mock_close_manifest.assert_called_once_with(manifest)

    @patch("spring_manifest.views.file_manifest.file_manifest.models.close_manifest")
    def test_manifest_did_not_close(self, mock_close_manifest):
        manifest = models.Manifest.objects.filter(closed=False)[0]
        with self.assertRaises(Exception):
            FileManifest(manifest)
        self.assertEqual("Manifest did not close.", manifest.errors)
        mock_close_manifest.assert_called_once_with(manifest)

    @patch("spring_manifest.views.file_manifest.file_manifest.models.close_manifest")
    @patch(
        "spring_manifest.views.file_manifest.file_manifest.FileManifest.process_manifest"
    )
    def test_error_in_process_manifest(
        self, mock_process_manifest, mock_close_manifest
    ):
        manifest = models.Manifest.objects.filter(closed=True)[0]
        mock_process_manifest.side_effect = Exception
        FileManifest(manifest)
        self.assertEqual(manifest.FAILED, manifest.status)
        self.assertEqual("Error processing manifest.\n", manifest.errors)
        mock_close_manifest.assert_called_once_with(manifest)

    @patch("spring_manifest.views.file_manifest.file_manifest.models.close_manifest")
    def test_process_manifest(self, mock_close_manifest):
        manifest = models.Manifest.objects.filter(closed=True)[0]
        filer = FileManifest(manifest)
        with self.assertRaises(NotImplementedError):
            filer.process_manifest()

    @patch("spring_manifest.views.file_manifest.file_manifest.models.close_manifest")
    @patch(
        "spring_manifest.views.file_manifest.file_manifest.FileManifest.process_manifest"
    )
    def test_add_error(self, mock_process_manifest, mock_close_manifest):
        manifest = models.Manifest.objects.filter(closed=True, errors__isnull=True)[0]
        filer = FileManifest(manifest)
        self.assertNotEqual(manifest.FAILED, manifest.status)
        self.assertEqual("", manifest.errors)
        filer.add_error("Error 1")
        self.assertEqual(manifest.FAILED, manifest.status)
        self.assertEqual("Error 1\n", manifest.errors)
        filer.add_error("Error 2")
        self.assertEqual("Error 1\nError 2\n", manifest.errors)

    def test_get_order_weight(self):
        order = Mock(
            products=[
                Mock(per_item_weight=25, quantity=4),
                Mock(per_item_weight=200, quantity=2),
            ]
        )
        weight = FileManifest.get_order_weight(order)
        self.assertEqual(0.5, weight)

    @patch("spring_manifest.views.file_manifest.file_manifest.models.close_manifest")
    @patch(
        "spring_manifest.views.file_manifest.file_manifest.FileManifest.process_manifest"
    )
    def test_valid(self, mock_process_manifest, mock_close_manifest):
        manifest = models.Manifest.objects.filter(closed=True, errors__isnull=True)[0]
        filer = FileManifest(manifest)
        self.assertTrue(filer.valid())
        manifest.errors = "Error"
        self.assertFalse(filer.valid())
        manifest.status = manifest.FAILED
        self.assertFalse(filer.valid())
        manifest.errors = None
        self.assertFalse(filer.valid())


class TestFileSecuredMailManifest(STCAdminTest):
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
        "spring_manifest/counter",
    )

    def setUp(self):
        super().setUp()
        self.manifest_type = models.ManifestType.objects.get(name="Secured Mail")
        self.manifest = models.Manifest.objects.get(id=4)

    @patch("django.utils.timezone.now", mock_now)
    @patch(
        "spring_manifest.views.file_manifest.file_manifest.models.close_manifest",
        close_manifest,
    )
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_file_manifest(self):
        securedmail.FileSecuredMailManifest(self.manifest)
        self.manifest.refresh_from_db()
        self.assertEqual("", self.manifest.errors)
        self.assertEqual(self.manifest.FILED, self.manifest.status)
        self.assertTrue(self.manifest.closed)
        self.assertTrue(self.manifest.manifest_file)
        self.assertFalse(self.manifest.item_advice_file)
        self.assertFalse(self.manifest.files_sent)
        self.assertEqual(mock_now(), self.manifest.time_filed)

    @patch("django.utils.timezone.now", mock_now)
    @patch(
        "spring_manifest.views.file_manifest.file_manifest.models.close_manifest",
        close_manifest,
    )
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_docket_counter_updated(self):
        counter = models.Counter.objects.get(name="Secured Mail Docket Number")
        docket_number = counter.count
        securedmail.FileSecuredMailManifest(self.manifest)
        counter.refresh_from_db()
        self.assertEqual(docket_number + 1, counter.count)

    @patch("django.utils.timezone.now", mock_now)
    @patch(
        "spring_manifest.views.file_manifest.file_manifest.models.close_manifest",
        close_manifest,
    )
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    @patch("spring_manifest.views.file_manifest.securedmail.SecuredMailManifestFile")
    @patch("spring_manifest.views.file_manifest.securedmail.SecuredMailDocketFile")
    def test_manifest_file(
        self, mock_SecuredMailDocketFile, mock_SecuredMailManifestFile
    ):
        mock_manifest_file = io.BytesIO(b"manifest contents")
        mock_SecuredMailManifestFile.create_manifest = Mock(
            return_value=mock_manifest_file
        )
        mock_SecuredMailDocketFile.return_value = io.BytesIO(b"docket contents")
        securedmail.FileSecuredMailManifest(self.manifest)
        self.manifest.refresh_from_db()
        manifest_file_name = (
            f"manifests/{self.manifest.id}_Secured_Mail_Unfiled_manifest.xlsx"
        )
        self.assertEqual(manifest_file_name, self.manifest.manifest_file.name)
        manifest_path = Path(settings.MEDIA_ROOT) / manifest_file_name
        self.assertTrue(manifest_path.exists())
        with open(manifest_path, "rb") as f:
            self.assertEqual(f.read(), b"manifest contents")

    @patch("django.utils.timezone.now", mock_now)
    @patch(
        "spring_manifest.views.file_manifest.file_manifest.models.close_manifest",
        close_manifest,
    )
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    @patch("spring_manifest.views.file_manifest.securedmail.SecuredMailManifestFile")
    @patch("spring_manifest.views.file_manifest.securedmail.SecuredMailDocketFile")
    def test_docket_file(
        self, mock_SecuredMailDocketFile, mock_SecuredMailManifestFile
    ):
        mock_manifest_file = io.BytesIO(b"manifest contents")
        mock_SecuredMailManifestFile.create_manifest = Mock(
            return_value=mock_manifest_file
        )
        mock_SecuredMailDocketFile.return_value = io.BytesIO(b"docket contents")
        securedmail.FileSecuredMailManifest(self.manifest)
        docket_file_name = f"docket/{self.manifest.id}_Secured_Mail_Unfiled_docket.xlsx"
        self.assertTrue(self.manifest.docket_file)
        self.assertEqual(docket_file_name, self.manifest.docket_file.name)
        docket_path = Path(settings.MEDIA_ROOT) / docket_file_name
        self.assertTrue(docket_path.exists())
        with open(docket_path, "rb") as f:
            self.assertEqual(f.read(), b"docket contents")

    @patch("django.utils.timezone.now", mock_now)
    @patch(
        "spring_manifest.views.file_manifest.file_manifest.models.close_manifest",
        close_manifest,
    )
    @patch(
        "spring_manifest.views.file_manifest.securedmail.FileSecuredMailManifest.valid"
    )
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_invalid_manifest(self, mock_valid):
        mock_valid.return_value = False
        securedmail.FileSecuredMailManifest(self.manifest)
        self.manifest.refresh_from_db()
        self.assertEqual("", self.manifest.errors)
        self.assertEqual(self.manifest.FAILED, self.manifest.status)
        self.assertFalse(self.manifest.manifest_file)
        self.assertFalse(self.manifest.docket_file)
        self.assertFalse(self.manifest.item_advice_file)
        self.assertFalse(self.manifest.files_sent)
        self.assertIsNone(self.manifest.time_filed)

    def test_increment_docket_number(self):
        counter = models.Counter.objects.get(name="Secured Mail Docket Number")
        docket_number = counter.count
        securedmail.FileSecuredMailManifest.increment_docket_number()
        counter.refresh_from_db()
        self.assertEqual(docket_number + 1, counter.count)
