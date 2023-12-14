import pytest
from django.urls import reverse

from fba.forms import SelectFBAOrderProductForm
from fba.views.fba import SelectFBAOrderProduct


def test_template_name_attribute():
    assert SelectFBAOrderProduct.template_name == "fba/select_order_product.html"


def test_form_class_attribute():
    assert SelectFBAOrderProduct.form_class == SelectFBAOrderProductForm


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def url():
    return reverse("fba:select_product_for_order")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response):
    assert "fba/select_order_product.html" in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], SelectFBAOrderProductForm)


@pytest.fixture
def form_data(product):
    return {"product_SKU": product.sku}


@pytest.fixture
def form_data_with_invalid_sku(form_data):
    form_data["product_SKU"] = "999-999-999"
    return form_data


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


def test_redirect(post_response, product):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse("fba:create_order", args=[product.pk])


def test_invalid_sku(group_logged_in_client, url, form_data_with_invalid_sku):
    response = group_logged_in_client.post(url, form_data_with_invalid_sku)
    assert response.status_code == 200
