import pytest
from django.urls import reverse

from inventory import models


@pytest.fixture
def url():
    return reverse("inventory:create_supplier")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_data():
    return {"name": "New Supplier"}


@pytest.fixture
def post_response(group_logged_in_client, url, post_data):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/supplier_form.html" in (t.name for t in get_response.templates)


@pytest.mark.django_db
def test_form_in_context(get_response):
    assert "form" in get_response.context


@pytest.mark.django_db
def test_form_is_saved(post_response):
    assert post_response.status_code == 302
    assert models.Supplier.objects.filter(name="New Supplier").exists()


@pytest.mark.django_db
def test_success_redirect(post_data, group_logged_in_client, url):
    response = group_logged_in_client.post(url, post_data)
    object = models.Supplier.objects.get(name="New Supplier")
    assert response.status_code == 302
    assert response["location"] == object.get_absolute_url()
