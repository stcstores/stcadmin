import json
import tempfile
from io import BytesIO
from unittest.mock import patch

import pytest
from django.test import override_settings
from pytest_django.asserts import assertTemplateUsed

from fnac.forms import MiraklProductImportForm
from fnac.models import MiraklProductImport


class TestMissingInformationView:
    URL = "/fnac/add_created_products/"

    @pytest.fixture
    def valid_get_response(self, valid_get_request):
        return valid_get_request(self.URL)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    def test_logged_out_get_method(self, logged_in_client):
        response = logged_in_client.get(self.URL)
        assert response.status_code == 403

    def test_logged_out_get(self, client):
        response = client.get(self.URL)
        assert response.status_code == 302

    def test_logged_in_group_get(self, valid_get_response):
        assert valid_get_response.status_code == 200

    def test_logged_in_post(self, logged_in_client):
        response = logged_in_client.post(self.URL)
        assert response.status_code == 403

    def test_logged_out_post(self, client):
        response = client.post(self.URL)
        assert response.status_code == 302

    def test_logged_in_group_post(
        self, group_logged_in_client,
    ):
        response = group_logged_in_client.post(self.URL)
        assert response.status_code == 405

    def test_response_test(self, valid_get_response):
        assertTemplateUsed("fnac/add_created_products.html")
        assertTemplateUsed("fnac/status_boxes/mirakl_product_upload.html")

    def test_form_in_context(self, valid_get_response):
        assert isinstance(valid_get_response.context["form"], MiraklProductImportForm)

    def test_model_in_context(self, valid_get_response):
        assert valid_get_response.context["MiraklProductImport"] == MiraklProductImport


class TestStartMiraklProductFileImport:
    URL = "/fnac/add_created_products/start_mirakl_product_file_import/"

    @pytest.fixture
    def upload_file(self):
        upload_file = BytesIO(b"content")
        upload_file.name = "mirakl_products.xlsx"
        return upload_file

    @pytest.fixture
    def valid_post_response(self, valid_post_request, upload_file):
        return valid_post_request(self.URL, {"import_file": upload_file})

    @pytest.fixture
    def valid_post_response_content(self, valid_post_response):
        return valid_post_response.content.decode("utf8")

    @pytest.fixture(autouse=True)
    def mock_create_import(self):
        with patch(
            "fnac.forms.models.MiraklProductImport.objects.create_import"
        ) as mock_create_import:
            yield mock_create_import

    def test_logged_out_get_method(self, logged_in_client):
        response = logged_in_client.get(self.URL)
        assert response.status_code == 403

    def test_logged_out_get(self, client):
        response = client.get(self.URL)
        assert response.status_code == 302

    def test_logged_in_group_get(self, group_logged_in_client):
        response = group_logged_in_client.get(self.URL)
        assert response.status_code == 405

    def test_logged_in_post(self, logged_in_client):
        response = logged_in_client.post(self.URL)
        assert response.status_code == 403

    def test_logged_out_post(self, client):
        response = client.post(self.URL)
        assert response.status_code == 302

    def test_logged_in_group_post(self, group_logged_in_client, upload_file):
        response = group_logged_in_client.post(self.URL, {"import_file": upload_file})
        assert response.status_code == 200

    def test_response_test(self, valid_post_response_content):
        assert valid_post_response_content == "done"

    def test_import_triggered(self, mock_create_import, valid_post_response):
        mock_create_import.assert_called_once()

    def test_invalid_post(self, group_logged_in_client):
        response = group_logged_in_client.post(self.URL)
        assert response.status_code == 500


@pytest.mark.django_db
class TestMiraklProductFileImportStatus:
    URL = "/fnac/add_created_products/mirakl_product_file_status/"

    @pytest.fixture
    def valid_get_response(self, valid_get_request):
        return valid_get_request(self.URL)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def existing_import(self, mirakl_product_import_factory):
        return mirakl_product_import_factory.create(status=MiraklProductImport.COMPLETE)

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def in_progress_import(self, mirakl_product_import_factory):
        return mirakl_product_import_factory.create(
            status=MiraklProductImport.IN_PROGRESS
        )

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def errored_import(self, mirakl_product_import_factory):
        return mirakl_product_import_factory.create(status=MiraklProductImport.ERROR)

    def test_logged_out_get_method(self, logged_in_client):
        response = logged_in_client.get(self.URL)
        assert response.status_code == 403

    def test_logged_out_get(self, client):
        response = client.get(self.URL)
        assert response.status_code == 302

    def test_logged_in_group_get(self, valid_get_response):
        assert valid_get_response.status_code == 200

    def test_logged_in_post(self, logged_in_client):
        response = logged_in_client.post(self.URL)
        assert response.status_code == 403

    def test_logged_out_post(self, client):
        response = client.post(self.URL)
        assert response.status_code == 302

    def test_logged_in_group_post(
        self, group_logged_in_client,
    ):
        response = group_logged_in_client.post(self.URL)
        assert response.status_code == 405

    def test_response_test(self, valid_get_response):
        assertTemplateUsed("fnac/missing_information_import_status.html")

    def test_content_with_no_existing_import(self, valid_get_response_content):
        assert valid_get_response_content == json.dumps(
            {"status": None, "latest": None}
        )

    def test_content_with_existing_import(
        self, existing_import, valid_get_response_content
    ):
        assert valid_get_response_content == json.dumps(
            {
                "status": MiraklProductImport.COMPLETE,
                "latest": existing_import.timestamp.strftime("%H:%M on %d %b %Y"),
            }
        )

    def test_content_with_import_in_progress(
        self, in_progress_import, valid_get_response_content
    ):
        assert valid_get_response_content == json.dumps(
            {"status": MiraklProductImport.IN_PROGRESS, "latest": None}
        )

    def test_content_with_import_error(
        self, errored_import, valid_get_response_content
    ):
        assert valid_get_response_content == json.dumps(
            {
                "status": MiraklProductImport.ERROR,
                "latest": errored_import.timestamp.strftime("%H:%M on %d %b %Y"),
            }
        )
