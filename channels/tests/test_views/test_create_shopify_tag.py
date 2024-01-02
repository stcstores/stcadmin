from unittest import mock

import pytest
from django.urls import reverse

from channels.forms import ShopifyTagForm
from channels.models.shopify_models import ShopifyListing, ShopifyTag
from channels.views import CreateShopifyTag


@pytest.fixture
def template():
    return "channels/shopify/create_shopify_tag.html"


def test_template_name_attribute(template):
    assert CreateShopifyTag.template_name == template


def test_form_class_attribute():
    assert CreateShopifyTag.form_class == ShopifyTagForm


def test_model_attribute():
    assert CreateShopifyTag.model == ShopifyTag


@pytest.fixture
def mock_get_object():
    with mock.patch("channels.views.get_object_or_404") as m:
        m.return_value.pk = 55
        yield m


@pytest.fixture
def form_data():
    return {"name": "Tag Name"}


@pytest.fixture
def listing_id():
    return 99


@pytest.fixture
def url():
    return reverse("channels:create_shopify_tag")


@pytest.fixture
def url_with_listing_id(listing_id):
    return reverse("channels:create_shopify_tag", kwargs={"listing_pk": listing_id})


@pytest.fixture
def get_response(mock_get_object, group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(template, get_response):
    assert template in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], ShopifyTagForm)


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_creates_tag(form_data, post_response):
    assert ShopifyTag.objects.filter(name=form_data["name"]).exists()


@pytest.mark.django_db
def test_redirect_without_listing_id(post_response):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse("channels:create_shopify_tag")


@pytest.mark.django_db
def test_redirect_with_listing_id(
    mock_get_object, form_data, listing_id, group_logged_in_client, url_with_listing_id
):
    response = group_logged_in_client.post(url_with_listing_id, form_data)
    obj = ShopifyTag.objects.get(name=form_data["name"])
    assert response.status_code == 302
    mock_get_object.assert_called_once_with(ShopifyListing, pk=listing_id)
    mock_get_object.return_value.tags.add.assert_called_once_with(obj)
    assert response["Location"] == reverse(
        "channels:update_shopify_tags", kwargs={"pk": mock_get_object.return_value.pk}
    )
