import pytest
from django.urls import reverse


@pytest.fixture
def url():
    return reverse("inventory:sku_generator")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/sku_generator.html" in [t.name for t in get_response.templates]
