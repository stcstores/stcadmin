from unittest import mock

import pytest
from django.urls import reverse


@pytest.fixture
def blacklisted_brands(blacklisted_brand_factory):
    return blacklisted_brand_factory.create_batch(3)


@pytest.fixture
def url():
    return reverse("restock:brand_blacklist")


@pytest.fixture
def search_text():
    return "Search Text"


@pytest.fixture
def get_response(url, group_logged_in_client):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "restock/blacklistedbrand_list.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_object_list_in_context(blacklisted_brands, get_response):
    for brand in blacklisted_brands:
        assert get_response.context["object_list"].contains(brand)


@pytest.mark.django_db
@mock.patch("restock.views.BrandBlacklist.model.objects.fuzzy_search")
def test_search(mock_fuzzy_search, url, group_logged_in_client, search_text):
    response = group_logged_in_client.get(url, {"search_text": search_text})
    mock_fuzzy_search.assert_called_once_with(search_text)
    assert response.context["object_list"] == mock_fuzzy_search.return_value
