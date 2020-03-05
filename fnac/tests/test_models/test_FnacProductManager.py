import pytest

from fnac import models


@pytest.mark.django_db
def test_out_of_stock_method(fnac_product_factory):
    fnac_product_factory.create(stock_level=5)
    out_of_stock = fnac_product_factory.create(stock_level=0)
    assert list(models.FnacProduct.objects.out_of_stock()) == [out_of_stock]


@pytest.mark.django_db
def test_in_stock_method(fnac_product_factory):
    in_stock = fnac_product_factory.create(stock_level=5)
    fnac_product_factory.create(stock_level=0)
    assert list(models.FnacProduct.objects.in_stock()) == [in_stock]


@pytest.mark.django_db
def test_translated_method(fnac_product_factory, translation_factory):
    translated = fnac_product_factory.create()
    fnac_product_factory.create()
    translation_factory.create(product=translated)
    assert list(models.FnacProduct.objects.translated()) == [translated]


@pytest.mark.django_db
def test_translated_does_not_return_when_name_missing(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, name="")
    assert product not in models.FnacProduct.objects.translated()


@pytest.mark.django_db
def test_translated_does_not_return_when_description_missing(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, description="")
    assert product not in models.FnacProduct.objects.translated()


@pytest.mark.django_db
def test_translated_does_not_return_when_product_has_colour_but_translation_does_not(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="red")
    translation_factory.create(product=product, colour="")
    assert product not in models.FnacProduct.objects.translated()


@pytest.mark.django_db
def test_translated_does_return_when_product_and_translation_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="red")
    translation_factory.create(product=product, colour="rouge")
    assert product in models.FnacProduct.objects.translated()


@pytest.mark.django_db
def test_translated_returns_when_nether_product_not_translation_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="")
    translation_factory.create(product=product, colour="")
    assert product in models.FnacProduct.objects.translated()


@pytest.mark.django_db
def test_not_translated_method(fnac_product_factory, translation_factory):
    translated = fnac_product_factory.create()
    not_translated = fnac_product_factory.create()
    translation_factory.create(product=translated)
    assert list(models.FnacProduct.objects.not_translated()) == [not_translated]


@pytest.mark.django_db
def test_not_translated_returns_when_translation_exists_without_name(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, name="")
    assert product in models.FnacProduct.objects.not_translated()


@pytest.mark.django_db
def test_not_translated_returns_when_translation_exists_without_description(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, description="")
    assert product in models.FnacProduct.objects.not_translated()


@pytest.mark.django_db
def test_not_translated_returns_when_translation_and_product_has_colour_bud_description_does_not(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="Red")
    translation_factory.create(product=product, colour="")
    assert product in models.FnacProduct.objects.not_translated()


@pytest.mark.django_db
def test_not_translated_does_not_return_when_translation_and_product_both_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="Red")
    translation_factory.create(product=product, colour="Rouge")
    assert product not in models.FnacProduct.objects.not_translated()


@pytest.mark.django_db
def test_not_translated_does_not_return_when_neither_translation_or_product_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="")
    translation_factory.create(product=product, colour="")
    assert product not in models.FnacProduct.objects.not_translated()
