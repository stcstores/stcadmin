import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from inventory import models
from inventory.tests import mocks


@pytest.fixture
def range_id():
    return "8946165"


@pytest.fixture
def get_URL(range_id):
    def _get_url(range_id=range_id):
        return f"/inventory/images/{range_id}/"

    return _get_url


@pytest.fixture
def range_options():
    return mocks.MockCCAPIProductRangeOptions(
        options=[
            mocks.MockProductOption(option_name="Size", is_web_shop_select=True),
            mocks.MockProductOption(option_name="Colour", is_web_shop_select=True),
        ]
    )


@pytest.fixture
def small_red_product():
    return mocks.MockCCAPIProduct(
        options=[
            mocks.MockCCAPIProductProductOption(
                option_name="Size",
                value=mocks.MockProductOptionValue(value="Small", option_name="Size"),
            ),
            mocks.MockCCAPIProductProductOption(
                option_name="Colour",
                value=mocks.MockProductOptionValue(value="Red", option_name="Colour"),
            ),
        ]
    )


@pytest.fixture
def large_green_product():
    return mocks.MockCCAPIProduct(
        options=[
            mocks.MockCCAPIProductProductOption(
                option_name="Size",
                value=mocks.MockProductOptionValue(value="Large", option_name="Size"),
            ),
            mocks.MockCCAPIProductProductOption(
                option_name="Colour",
                value=mocks.MockProductOptionValue(value="Green", option_name="Colour"),
            ),
        ]
    )


@pytest.fixture
def products(small_red_product, large_green_product):
    return [small_red_product, large_green_product]


@pytest.fixture
def product_range(range_id, products, range_options):
    return mocks.MockCCAPIProductRange(
        id=range_id, products=products, options=range_options
    )


@pytest.fixture
def mock_CCAPI(product_range):
    with patch("inventory.views.images.CCAPI") as mock_CCAPI:
        mock_CCAPI.get_range.return_value = product_range
        yield mock_CCAPI


@pytest.fixture
def valid_get_response(valid_get_request, get_URL):
    return valid_get_request(get_URL())


@pytest.fixture
def image():
    with open(Path(__file__).parent / "test_image.jpg", "rb") as f:
        return SimpleUploadedFile("test_image.jpg", f.read(), content_type="image/jpg")


@pytest.fixture
def post_request_data(products, image):
    return {
        "product_ids": json.dumps([product.id for product in products]),
        "cloud_commerce_images": [image],
    }


@pytest.fixture
def post_request_response(mock_CCAPI, valid_post_request, get_URL, post_request_data):
    return valid_post_request(get_URL(), data=post_request_data)


def test_logged_in_get(get_URL, mock_CCAPI, logged_in_client):
    response = logged_in_client.get(get_URL())
    assert response.status_code == 403


def test_logged_out_get(mock_CCAPI, client, get_URL):
    response = client.get(get_URL())
    assert response.status_code == 302


def test_logged_in_group_get(mock_CCAPI, group_logged_in_client, get_URL):
    response = group_logged_in_client.get(get_URL())
    assert response.status_code == 200


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_logged_in_post(mock_CCAPI, get_URL, logged_in_client, post_request_data):
    response = logged_in_client.post(get_URL(), post_request_data)
    assert response.status_code == 403


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_logged_out_post(mock_CCAPI, client, get_URL, post_request_data):
    response = client.post(get_URL(), post_request_data)
    assert response.status_code == 302


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_logged_in_group_post(
    mock_CCAPI, group_logged_in_client, get_URL, post_request_data
):
    response = group_logged_in_client.post(get_URL(), post_request_data)
    assert response.status_code == 302


def test_uses_template(mock_CCAPI, valid_get_response):
    assertTemplateUsed(valid_get_response, "inventory/images.html")


def test_context_contains_options(
    mock_CCAPI,
    valid_get_response,
    small_red_product,
    large_green_product,
):
    assert valid_get_response.context["options"] == {
        "Size": {"Small": [small_red_product.id], "Large": [large_green_product.id]},
        "Colour": {"Green": [large_green_product.id], "Red": [small_red_product.id]},
    }


def test_context_contains_product_range(
    mock_CCAPI,
    valid_get_response,
    product_range,
):
    assert valid_get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_context(mock_CCAPI, valid_get_response, products):
    assert valid_get_response.context["products"] == products


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_post_calls_add_images(mock_CCAPI, post_request_response):
    mock_CCAPI.upload_image.assert_called_once()


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_post_creates_images_in_database(
    product_range,
    products,
    post_request_response,
):
    for product in products:
        assert models.ProductImage.objects.filter(
            product_id=product.id,
            range_sku=product_range.sku,
            sku=product.sku,
            image_file__isnull=False,
        ).exists()


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_post_request_returns_redirect(
    get_URL,
    post_request_response,
):
    assertRedirects(post_request_response, get_URL())


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_content(mock_CCAPI, valid_get_response, products):
    content = valid_get_response.content.decode("utf8")
    for product in products:
        assert product.name in content
    assert "Large" in content
    assert "Small" in content
    assert "Red" in content
    assert "Green" in content
