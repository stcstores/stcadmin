import pytest

from channels import models


@pytest.fixture
def shopify_tag(shopify_tag_factory):
    return shopify_tag_factory.create()


@pytest.mark.django_db
def test_full_clean(shopify_tag):
    assert shopify_tag.full_clean() is None


@pytest.mark.django_db
def test_has_name_attribute(shopify_tag):
    assert isinstance(shopify_tag.name, str)


# Test Methods


@pytest.mark.django_db
def test_str_method(shopify_tag):
    assert str(shopify_tag) == shopify_tag.name


@pytest.mark.django_db
def test_replace_method_creates_new_tags(shopify_tag):
    new_tags = ("A", "B")
    shopify_tag.replace(*new_tags)
    for tag in new_tags:
        assert models.shopify_models.ShopifyTag.objects.filter(name=tag).exists()


@pytest.mark.django_db
def test_replace_method_deletes_self(shopify_tag):
    shopify_tag.replace("A")
    assert (
        models.shopify_models.ShopifyTag.objects.filter(id=shopify_tag.id).exists()
        is False
    )


@pytest.mark.django_db
def test_tags_are_replaced(shopify_listing_factory, shopify_tag):
    listing = shopify_listing_factory.create()
    listing.tags.add(shopify_tag)
    shopify_tag.replace("A")
    assert listing.tags.count() == 1
    assert listing.tags.all()[0].name == "A"
