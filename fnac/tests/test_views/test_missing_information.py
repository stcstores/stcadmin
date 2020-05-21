import json
import tempfile
from io import BytesIO
from unittest.mock import patch

import pytest
from django.test import override_settings
from pytest_django.asserts import assertTemplateUsed

from fnac.models import MissingInformationExport, MissingInformationImport


class TestMissingInformationView:
    URL = "/fnac/missing_information/"

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

    def test_response_templates(self, valid_get_response):
        assertTemplateUsed(valid_get_response, "fnac/missing_information.html")


class TestCreateMissingInformationExport:
    URL = "/fnac/missing_information/create_export/"

    @pytest.fixture
    def valid_get_response(self, valid_get_request):
        return valid_get_request(self.URL)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    @pytest.fixture(autouse=True)
    def mock_create_missing_information_export_task(self):
        with patch("fnac.views.create_missing_information_export") as mock_task:
            yield mock_task

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

    def test_response_templates(self, valid_get_response_content):
        assert valid_get_response_content == "done"

    def test_export_creation_triggered(
        self, mock_create_missing_information_export_task, valid_get_response
    ):
        mock_create_missing_information_export_task.delay.assert_called_once()


@pytest.mark.django_db
class TestMissingInformationExportStatusView:
    URL = "/fnac/missing_information/export_status/"

    @pytest.fixture
    def valid_get_response(self, valid_get_request):
        return valid_get_request(self.URL)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def existing_export(self, missing_information_export_factory):
        return missing_information_export_factory.create(
            status=MissingInformationExport.COMPLETE
        )

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def in_progress_export(self, missing_information_export_factory):
        return missing_information_export_factory.create(
            status=MissingInformationExport.IN_PROGRESS
        )

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def errored_export(self, missing_information_export_factory):
        return missing_information_export_factory.create(
            status=MissingInformationExport.ERROR
        )

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

    def test_response_templates(self, valid_get_response):
        assertTemplateUsed(
            valid_get_response, "fnac/missing_information_export_status.html"
        )

    def test_content_with_no_existing_export(self, valid_get_response_content):
        assert (
            "No Missing Information file has yet been generated"
            in valid_get_response_content
        )
        assert "Generate New Missing Information File" in valid_get_response_content

    def test_content_with_existing_export(
        self, existing_export, valid_get_response_content
    ):
        assert "Last Missing Information file created at " in valid_get_response_content
        assert "Generate New Missing Information File" in valid_get_response_content

    def test_content_with_export_in_progress(
        self, in_progress_export, valid_get_response_content
    ):
        assert (
            "A Missing Information file is being generated"
            in valid_get_response_content
        )

    def test_content_with_export_error(
        self, errored_export, valid_get_response_content
    ):
        assert "There was an error creating the file" in valid_get_response_content
        assert "Generate New Missing Information File" in valid_get_response_content


class TestStartMissingInformationImport:
    URL = "/fnac/missing_information/start_import/"

    @pytest.fixture
    def upload_file(self):
        upload_file = BytesIO(b"content")
        upload_file.name = "missing_information.xlsx"
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
            "fnac.forms.models.MissingInformationImport.objects.create_import"
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

    def test_response_templates(self, valid_post_response_content):
        assert valid_post_response_content == "done"

    def test_import_triggered(self, mock_create_import, valid_post_response):
        mock_create_import.assert_called_once()

    def test_invalid_post(self, group_logged_in_client):
        response = group_logged_in_client.post(self.URL)
        assert response.status_code == 500


@pytest.mark.django_db
class TestMissingInformationImportStatusView:
    URL = "/fnac/missing_information/import_status/"

    @pytest.fixture
    def valid_get_response(self, valid_get_request):
        return valid_get_request(self.URL)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def existing_import(self, missing_information_import_factory):
        return missing_information_import_factory.create(
            status=MissingInformationImport.COMPLETE
        )

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def in_progress_import(self, missing_information_import_factory):
        return missing_information_import_factory.create(
            status=MissingInformationImport.IN_PROGRESS
        )

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def errored_import(self, missing_information_import_factory):
        return missing_information_import_factory.create(
            status=MissingInformationImport.ERROR
        )

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

    def test_content_with_no_existing_import(self, valid_get_response_content):
        assert valid_get_response_content == json.dumps(
            {"status": None, "latest": None}
        )

    def test_content_with_existing_import(
        self, existing_import, valid_get_response_content
    ):
        assert valid_get_response_content == json.dumps(
            {
                "status": MissingInformationImport.COMPLETE,
                "latest": existing_import.timestamp.strftime("%H:%M on %d %b %Y"),
            }
        )

    def test_content_with_import_in_progress(
        self, in_progress_import, valid_get_response_content
    ):
        assert valid_get_response_content == json.dumps(
            {"status": MissingInformationImport.IN_PROGRESS, "latest": None}
        )

    def test_content_with_import_error(
        self, errored_import, valid_get_response_content
    ):
        assert valid_get_response_content == json.dumps(
            {
                "status": MissingInformationImport.ERROR,
                "latest": errored_import.timestamp.strftime("%H:%M on %d %b %Y"),
            }
        )
