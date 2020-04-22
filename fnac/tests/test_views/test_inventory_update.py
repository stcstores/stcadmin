from unittest.mock import patch

import pytest
from pytest_django.asserts import assertTemplateUsed

from fnac.models import InventoryImport


class TestStartInventoryUpdate:
    URL = "/fnac/inventory_update/start/"

    @pytest.fixture
    def valid_get_response(self, valid_get_request):
        return valid_get_request(self.URL)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    @pytest.fixture(autouse=True)
    def mock_update_inventory(self):
        with patch("fnac.views.update_inventory") as mock_task:
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

    def test_response_test(self, valid_get_response_content):
        assert valid_get_response_content == "done"

    def test_inventory_update_triggered(
        self, mock_update_inventory, valid_get_response
    ):
        mock_update_inventory.delay.assert_called_once()


@pytest.mark.django_db
class TestInventoryUpdateStatusView:
    URL = "/fnac/inventory_update/status/"

    @pytest.fixture
    def valid_get_response(self, valid_get_request):
        return valid_get_request(self.URL)

    @pytest.fixture
    def valid_get_response_content(self, valid_get_response):
        return valid_get_response.content.decode("utf8")

    @pytest.fixture
    def existing_import(self, inventory_import_factory):
        return inventory_import_factory.create(status=InventoryImport.COMPLETE)

    @pytest.fixture
    def in_progress_import(self, inventory_import_factory):
        return inventory_import_factory.create(status=InventoryImport.IN_PROGRESS)

    @pytest.fixture
    def errored_import(self, inventory_import_factory):
        return inventory_import_factory.create(status=InventoryImport.ERROR)

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
        assertTemplateUsed("fnac/inventory_import_status.html")

    def test_content_with_no_existing_import(self, valid_get_response_content):
        assert "Inventory not yet imported" in valid_get_response_content
        assert "Update Inventory Information" in valid_get_response_content

    def test_content_with_existing_import(
        self, existing_import, valid_get_response_content
    ):
        assert "Inventory last updated at" in valid_get_response_content
        assert "Update Inventory Information" in valid_get_response_content

    def test_content_with_update_in_progress(
        self, in_progress_import, valid_get_response_content
    ):
        assert "An import is in progress" in valid_get_response_content

    def test_content_with_import_error(
        self, errored_import, valid_get_response_content
    ):
        assert (
            "There was an error updating the inventory information"
            in valid_get_response_content
        )
        assert "Update Inventory Information" in valid_get_response_content
