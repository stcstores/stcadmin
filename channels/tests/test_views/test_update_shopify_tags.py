from unittest import mock

import pytest
from django.urls import reverse

from channels.forms import ShopifyTagsForm
from channels.models.shopify_models import ShopifyListing
from channels.views import UpdateShopifyTags


@pytest.fixture
def template():
    return "channels/shopify/shopify_tags_form.html"


def test_template_name_attribute(template):
    assert UpdateShopifyTags.template_name == template


def test_form_class_attribute():
    assert UpdateShopifyTags.form_class == ShopifyTagsForm


def test_model_attribute():
    assert UpdateShopifyTags.model == ShopifyListing


@pytest.fixture
def tag(shopify_tag_factory):
    return shopify_tag_factory.create()


@pytest.fixture
def shopify_listing(shopify_listing_factory, tag):
    shopify_listing = shopify_listing_factory.create()
    shopify_listing.tags.set([tag])
    return shopify_listing


@pytest.fixture
def tags(shopify_tag_factory):
    return shopify_tag_factory.create_batch(3)


@pytest.fixture
def mock_shopify_tag():
    with mock.patch("channels.views.models.shopify_models.ShopifyTag") as m:
        yield m


@pytest.fixture
def url(mock_shopify_tag, shopify_listing):
    return reverse("channels:update_shopify_tags", args=[shopify_listing.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(template, get_response):
    assert template in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], ShopifyTagsForm)


@pytest.mark.django_db
def test_listing_in_context(shopify_listing, get_response):
    assert get_response.context["listing"] == shopify_listing


@pytest.mark.django_db
def test_listing_tags_in_context(tag, get_response):
    value = get_response.context["listing_tags"]
    assert list(value) == [tag]


@mock.patch("channels.views.UpdateShopifyTags.get_tag_groups")
def test_tag_groups_in_context(mock_get_tag_groups, group_logged_in_client, url):
    get_response = group_logged_in_client.get(url)
    mock_get_tag_groups.assert_called_once_with()
    assert get_response.context["tag_groups"] == mock_get_tag_groups.return_value


def test_get_tag_groups(mock_shopify_tag, shopify_tag_factory):
    tag_names = ["Aardvark", "Apple", "anchovie", "capital"]
    tags = [shopify_tag_factory.build(name=name) for name in tag_names]
    mock_shopify_tag.objects.all.return_value = tags
    value = UpdateShopifyTags().get_tag_groups()
    mock_shopify_tag.objects.all.assert_called_once_with()
    assert value == {"A": [tags[0], tags[1], tags[2]], "C": [tags[3]]}


@pytest.fixture
def form_data(tags):
    return {"tags": [tag.id for tag in tags]}


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_redirect(post_response, shopify_listing):
    assert post_response.status_code == 302
    assert post_response["Location"] == shopify_listing.get_absolute_url()


@pytest.mark.django_db
def test_redirect_with_create_tag(
    form_data, group_logged_in_client, url, shopify_listing
):
    form_data["create_tag"] = True
    post_response = group_logged_in_client.post(url, form_data)
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse(
        "channels:create_shopify_tag", args=[shopify_listing.pk]
    )


@pytest.mark.django_db
def test_sets_tags(tags, shopify_listing, post_response):
    for tag in tags:
        assert shopify_listing.tags.all().contains(tag)
