import pytest
from django.urls import reverse

from restock import models


@pytest.fixture
def url():
    return reverse("restock:create_blacklisted_brand")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_data():
    return {"name": "Blacklisted Brand", "comment": "With Comment"}


@pytest.fixture
def post_response(group_logged_in_client, url, post_data):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "restock/blacklistedbrand_form.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_form_in_context(get_response):
    assert "form" in get_response.context


@pytest.mark.django_db
def test_form_is_saved(post_response):
    assert post_response.status_code == 302
    object = models.BlacklistedBrand.objects.get(name="Blacklisted Brand")
    assert object.comment == "With Comment"


@pytest.mark.django_db
def test_success_redirect(post_data, group_logged_in_client, url):
    response = group_logged_in_client.post(url, post_data)
    assert response.status_code == 302
    assert response["location"] == reverse("restock:brand_blacklist")
