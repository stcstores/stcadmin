import tempfile
from unittest.mock import patch

import pytest
from django.test import override_settings
from pytest_django.asserts import assertTemplateUsed

from fnac.models import OfferUpdate


class TestCreateOfferUpdate:
    URL = "/fnac/offer_update/create/"

    @pytest.fixture
    def valid_get_response(self, valid_get_request):
        return valid_get_request(self.URL)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    @pytest.fixture(autouse=True)
    def mock_create_offer_update_task(self):
        with patch("fnac.views.create_offer_update_export") as mock_task:
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
        self, mock_create_offer_update_task, valid_get_response
    ):
        mock_create_offer_update_task.delay.assert_called_once()


@pytest.mark.django_db
class TestOfferUpdateStatusView:
    URL = "/fnac/offer_update/status/"

    @pytest.fixture
    def valid_get_response(self, valid_get_request):
        return valid_get_request(self.URL)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def existing_export(self, offer_update_factory):
        return offer_update_factory.create(status=OfferUpdate.COMPLETE)

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def in_progress_export(self, offer_update_factory):
        return offer_update_factory.create(status=OfferUpdate.IN_PROGRESS)

    @pytest.fixture
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def errored_export(self, offer_update_factory):
        return offer_update_factory.create(status=OfferUpdate.ERROR)

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
        assertTemplateUsed(valid_get_response, "fnac/offer_update_status.html")

    def test_content_with_no_existing_export(self, valid_get_response_content):
        assert (
            "No offer update file has yet been generated" in valid_get_response_content
        )
        assert "Generate New Offer Update File" in valid_get_response_content

    def test_content_with_existing_export(
        self, existing_export, valid_get_response_content
    ):
        assert "Last offer update file created at" in valid_get_response_content
        assert "Generate New Offer Update File" in valid_get_response_content

    def test_content_with_export_in_progress(
        self, in_progress_export, valid_get_response_content
    ):
        assert "An offer update file is being generated" in valid_get_response_content

    def test_content_with_export_error(
        self, errored_export, valid_get_response_content
    ):
        assert (
            "There was an error creating the offer update file"
            in valid_get_response_content
        )
        assert "Generate New Offer Update File" in valid_get_response_content
