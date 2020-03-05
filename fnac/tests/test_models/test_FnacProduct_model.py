import pytest
from django.db.utils import IntegrityError

from fnac import models


@pytest.fixture
def test_image_url():
    return "92849.jpg"


@pytest.mark.django_db
def test_FnacProduct_has_name(fnac_product_factory):
    name = "Test Name"
    fnac_product = fnac_product_factory.create(name=name)
    assert fnac_product.name == name


@pytest.mark.django_db
def test_FnacProduct_has_sku(fnac_product_factory):
    sku = "RNG_ABC-DEF-123"
    fnac_product = fnac_product_factory.create(sku=sku)
    assert fnac_product.sku == sku


@pytest.mark.django_db
def test_FnacProduct_sku_field_is_unique(fnac_product_factory):
    sku = "RNG_ABC-DEF-123"
    fnac_product_factory.create(sku=sku)
    with pytest.raises(IntegrityError):
        fnac_product_factory.create(sku=sku)


@pytest.mark.django_db
def test_FnacProduct_product_range_field(fnac_range_factory, fnac_product_factory):
    fnac_range = fnac_range_factory.create()
    product = fnac_product_factory.create(fnac_range=fnac_range)
    assert product.fnac_range == fnac_range


@pytest.mark.django_db
def test_FnacProduct_barcode_field(fnac_product_factory):
    barcode = "9308493484"
    product = fnac_product_factory.create(barcode=barcode)
    assert product.barcode == barcode


@pytest.mark.django_db
def test_FnacProduct_description_field(fnac_product_factory):
    description = "A desciption\nOf a product"
    product = fnac_product_factory.create(description=description)
    assert product.description == description


@pytest.mark.django_db
def test_FnacProduct_colour_field(fnac_product_factory):
    colour = "Green"
    product = fnac_product_factory.create(colour=colour)
    assert product.colour == colour


@pytest.mark.django_db
def test_FnacProduct_colour_field_can_be_null(fnac_product_factory):
    product = fnac_product_factory.create(colour=None)
    assert product.colour is None


@pytest.mark.django_db
def test_FnacProduct_price_field(fnac_product_factory):
    price = 5511
    product = fnac_product_factory.create(price=price)
    assert product.price == price


@pytest.mark.django_db
def test_FnacProduct_price_field_can_be_null(fnac_product_factory):
    product = fnac_product_factory.create(price=None)
    assert product.price is None


@pytest.mark.django_db
def test_FnacProduct_brand_field(fnac_product_factory):
    brand = "Stockist"
    product = fnac_product_factory.create(brand=brand)
    assert product.brand == brand


@pytest.mark.django_db
def test_FnacProduct_english_size_field(fnac_product_factory):
    english_size = "Medium"
    product = fnac_product_factory.create(english_size=english_size)
    assert product.english_size == english_size


@pytest.mark.django_db
def test_FnacProduct_english_size_field_can_be_null(fnac_product_factory):
    product = fnac_product_factory.create()
    assert product.english_size is None


@pytest.mark.django_db
def test_FnacProduct_french_size_field(fnac_product_factory, size_factory):
    french_size = size_factory.create()
    product = fnac_product_factory.create(french_size=french_size)
    assert product.french_size == french_size


@pytest.mark.django_db
def test_FnacProduct_french_size_field_can_be_null(fnac_product_factory):
    product = fnac_product_factory.create()
    assert product.french_size is None


@pytest.mark.django_db
def test_FnacProduct_stock_level_field(fnac_product_factory):
    stock_level = 63
    product = fnac_product_factory.create(stock_level=stock_level)
    assert product.stock_level == stock_level


@pytest.mark.django_db
def test_FnacProduct_image_1_field(fnac_product_factory, test_image_url):
    product = fnac_product_factory.create(image_1=test_image_url)
    assert product.image_1 == test_image_url


@pytest.mark.django_db
def test_FnacProduct_image_1_field_can_be_empty(fnac_product_factory):
    product = fnac_product_factory.create(image_1="")
    assert product.image_1 == ""


@pytest.mark.django_db
def test_FnacProduct_image_2_field(fnac_product_factory, test_image_url):
    product = fnac_product_factory.create(image_2=test_image_url)
    assert product.image_2 == test_image_url


@pytest.mark.django_db
def test_FnacProduct_image_2_field_can_be_empty(fnac_product_factory):
    product = fnac_product_factory.create(image_2="")
    assert product.image_2 == ""


@pytest.mark.django_db
def test_FnacProduct_image_3_field(fnac_product_factory, test_image_url):
    product = fnac_product_factory.create(image_3=test_image_url)
    assert product.image_3 == test_image_url


@pytest.mark.django_db
def test_FnacProduct_image_3_field_can_be_empty(fnac_product_factory):
    product = fnac_product_factory.create(image_3="")
    assert product.image_3 == ""


@pytest.mark.django_db
def test_FnacProduct_image_4_field(fnac_product_factory, test_image_url):
    product = fnac_product_factory.create(image_4=test_image_url)
    assert product.image_4 == test_image_url


@pytest.mark.django_db
def test_FnacProduct_image_4_field_can_be_empty(fnac_product_factory):
    product = fnac_product_factory.create(image_4="")
    assert product.image_4 == ""


@pytest.mark.django_db
def test_FnacProduct_do_not_create_field(fnac_product_factory):
    product = fnac_product_factory.create(do_not_create=True)
    assert product.do_not_create is True


@pytest.mark.django_db
def test_FnacProduct_created_field(fnac_product_factory):
    product = fnac_product_factory.create(created=True)
    assert product.created is True


@pytest.mark.django_db
def test_FnacProduct_str(fnac_product_factory):
    fnac_product = fnac_product_factory.create(sku="ABC-DEF-123", name="Test Name")
    assert str(fnac_product) == "ABC-DEF-123 - Test Name"


@pytest.mark.django_db
def test_out_of_stock_method(fnac_product_factory):
    fnac_product_factory.create(stock_level=5)
    out_of_stock = fnac_product_factory.create(stock_level=0)
    assert list(models.FnacProduct.out_of_stock()) == [out_of_stock]


@pytest.mark.django_db
def test_in_stock_method(fnac_product_factory):
    in_stock = fnac_product_factory.create(stock_level=5)
    fnac_product_factory.create(stock_level=0)
    assert list(models.FnacProduct.in_stock()) == [in_stock]


@pytest.mark.django_db
def test_translated_method(fnac_product_factory, translation_factory):
    translated = fnac_product_factory.create()
    fnac_product_factory.create()
    translation_factory.create(product=translated)
    assert list(models.FnacProduct.translated()) == [translated]


@pytest.mark.django_db
def test_translated_does_not_return_when_name_missing(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, name="")
    assert product not in models.FnacProduct.translated()


@pytest.mark.django_db
def test_translated_does_not_return_when_description_missing(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, description="")
    assert product not in models.FnacProduct.translated()


@pytest.mark.django_db
def test_translated_does_not_return_when_product_has_colour_but_translation_does_not(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="red")
    translation_factory.create(product=product, colour="")
    assert product not in models.FnacProduct.translated()


@pytest.mark.django_db
def test_translated_does_return_when_product_and_translation_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="red")
    translation_factory.create(product=product, colour="rouge")
    assert product in models.FnacProduct.translated()


@pytest.mark.django_db
def test_translated_returns_when_nether_product_not_translation_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="")
    translation_factory.create(product=product, colour="")
    assert product in models.FnacProduct.translated()


@pytest.mark.django_db
def test_not_translated_method(fnac_product_factory, translation_factory):
    translated = fnac_product_factory.create()
    not_translated = fnac_product_factory.create()
    translation_factory.create(product=translated)
    assert list(models.FnacProduct.not_translated()) == [not_translated]


@pytest.mark.django_db
def test_not_translated_returns_when_translation_exists_without_name(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, name="")
    assert product in models.FnacProduct.not_translated()


@pytest.mark.django_db
def test_not_translated_returns_when_translation_exists_without_description(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create()
    translation_factory.create(product=product, description="")
    assert product in models.FnacProduct.not_translated()


@pytest.mark.django_db
def test_not_translated_returns_when_translation_and_product_has_colour_bud_description_does_not(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="Red")
    translation_factory.create(product=product, colour="")
    assert product in models.FnacProduct.not_translated()


@pytest.mark.django_db
def test_not_translated_does_not_return_when_translation_and_product_both_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="Red")
    translation_factory.create(product=product, colour="Rouge")
    assert product not in models.FnacProduct.not_translated()


@pytest.mark.django_db
def test_not_translated_does_not_return_when_neither_translation_or_product_have_colour(
    fnac_product_factory, translation_factory
):
    product = fnac_product_factory.create(colour="")
    translation_factory.create(product=product, colour="")
    assert product not in models.FnacProduct.not_translated()
