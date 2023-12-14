import pytest
from django.urls import reverse

from restock.models import BlacklistedBrand


@pytest.fixture
def blacklisted_brand(blacklisted_brand_factory):
    return blacklisted_brand_factory.create()


@pytest.fixture
def url(blacklisted_brand):
    return reverse(
        "restock:delete_blacklisted_brand",
        kwargs={"pk": blacklisted_brand.pk},
    )


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_data(blacklisted_brand):
    return {}


@pytest.fixture
def post_response(group_logged_in_client, url, post_data):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "restock/blacklistedbrand_confirm_delete.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_form_in_context(get_response):
    assert "form" in get_response.context


@pytest.mark.django_db
def test_object_is_deleted(post_response, blacklisted_brand):
    assert BlacklistedBrand.objects.filter(pk=blacklisted_brand.pk).exists() is False


@pytest.mark.django_db
def test_success_redirect(blacklisted_brand, post_response):
    assert post_response.status_code == 302
    assert post_response["location"] == reverse("restock:brand_blacklist")
