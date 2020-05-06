import pytest
from pytest_django.asserts import assertTemplateUsed

from fnac import models


class TestUpdateOffersView:
    URL = "/fnac/update_offers/"

    @pytest.fixture
    def comment_text(self):
        return "Shipping Information\nShips in 5 days"

    @pytest.fixture
    def comment(self, comment_text):
        return models.Comment.objects.set_comment_text(comment_text)

    @pytest.fixture
    def post_data(self, comment_text):
        return {"comment": comment_text}

    @pytest.fixture
    def valid_post_response(self, comment_factory, valid_post_request, post_data):
        comment_factory.create()
        return valid_post_request(self.URL, post_data)

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

    def test_logged_in_group_post(self, valid_post_response):
        assert valid_post_response.status_code == 302

    def test_response_test(self, valid_get_response):
        assertTemplateUsed("fnac/update_offers.html")
        assertTemplateUsed("fnac/status_boxes/inventory_update.html")
        assertTemplateUsed("fnac/status_boxes/offer_update.html")

    @pytest.mark.django_db
    def test_current_comment_is_displayed(
        self, comment, comment_text, valid_get_response_content
    ):
        assert comment_text in valid_get_response_content

    @pytest.mark.django_db
    def test_comment_is_updated(self, comment, comment_text, valid_post_response):
        assert models.Comment.objects.get_comment_text() == comment_text
