import pytest
from django.db.utils import IntegrityError

from fnac import models


@pytest.fixture
def test_image_url():
    return "92849.jpg"


@pytest.mark.django_db
def test_FnacProduct_has_name(make_fnac_product):
    name = "Test Name"
    fnac_product = make_fnac_product(name=name)
    assert fnac_product.name == name


@pytest.mark.django_db
def test_FnacProduct_has_sku(make_fnac_product):
    sku = "RNG_ABC-DEF-123"
    fnac_product = make_fnac_product(sku=sku)
    assert fnac_product.sku == sku


@pytest.mark.django_db
def test_FnacProduct_sku_field_is_unique(make_fnac_product):
    sku = "RNG_ABC-DEF-123"
    make_fnac_product(sku=sku)
    with pytest.raises(IntegrityError):
        make_fnac_product(sku=sku)


@pytest.mark.django_db
def test_FnacProduct_product_range_field(make_fnac_range, make_fnac_product):
    fnac_range = make_fnac_range()
    product = make_fnac_product(fnac_range=fnac_range)
    assert product.fnac_range == fnac_range


@pytest.mark.django_db
def test_FnacProduct_barcode_field(make_fnac_product):
    barcode = "9308493484"
    product = make_fnac_product(barcode=barcode)
    assert product.barcode == barcode


@pytest.mark.django_db
def test_FnacProduct_description_field(make_fnac_product):
    description = "A desciption\nOf a product"
    product = make_fnac_product(description=description)
    assert product.description == description


@pytest.mark.django_db
def test_FnacProduct_colour_field(make_fnac_product):
    colour = "Green"
    product = make_fnac_product(colour=colour)
    assert product.colour == colour


@pytest.mark.django_db
def test_FnacProduct_colour_field_can_be_null(make_fnac_product):
    product = make_fnac_product(colour=None)
    assert product.colour is None


@pytest.mark.django_db
def test_FnacProduct_price_field(make_fnac_product):
    price = 5511
    product = make_fnac_product(price=price)
    assert product.price == price


@pytest.mark.django_db
def test_FnacProduct_price_field_can_be_null(make_fnac_product):
    product = make_fnac_product(price=None)
    assert product.price is None


@pytest.mark.django_db
def test_FnacProduct_brand_field(make_fnac_product):
    brand = "Stockist"
    product = make_fnac_product(brand=brand)
    assert product.brand == brand


@pytest.mark.django_db
def test_FnacProduct_english_size_field(make_fnac_product):
    english_size = "Medium"
    product = make_fnac_product(english_size=english_size)
    assert product.english_size == english_size


@pytest.mark.django_db
def test_FnacProduct_english_size_field_can_be_null(make_fnac_product):
    product = make_fnac_product(english_size=None)
    assert product.english_size is None


@pytest.mark.django_db
def test_FnacProduct_french_size_field(make_fnac_product, make_size):
    french_size = make_size()
    product = make_fnac_product(french_size=french_size)
    assert product.french_size == french_size


@pytest.mark.django_db
def test_FnacProduct_french_size_field_can_be_null(make_fnac_product):
    product = make_fnac_product(french_size=None)
    assert product.french_size is None


@pytest.mark.django_db
def test_FnacProduct_stock_level_field(make_fnac_product):
    stock_level = 63
    product = make_fnac_product(stock_level=stock_level)
    assert product.stock_level == stock_level


@pytest.mark.django_db
def test_FnacProduct_image_1_field(make_fnac_product, test_image_url):
    product = make_fnac_product(image_1=test_image_url)
    assert product.image_1 == test_image_url


@pytest.mark.django_db
def test_FnacProduct_image_1_field_can_be_empty(make_fnac_product):
    product = make_fnac_product(image_1="")
    assert product.image_1 == ""


@pytest.mark.django_db
def test_FnacProduct_image_2_field(make_fnac_product, test_image_url):
    product = make_fnac_product(image_2=test_image_url)
    assert product.image_2 == test_image_url


@pytest.mark.django_db
def test_FnacProduct_image_2_field_can_be_empty(make_fnac_product):
    product = make_fnac_product(image_2="")
    assert product.image_2 == ""


@pytest.mark.django_db
def test_FnacProduct_image_3_field(make_fnac_product, test_image_url):
    product = make_fnac_product(image_3=test_image_url)
    assert product.image_3 == test_image_url


@pytest.mark.django_db
def test_FnacProduct_image_3_field_can_be_empty(make_fnac_product):
    product = make_fnac_product(image_3="")
    assert product.image_3 == ""


@pytest.mark.django_db
def test_FnacProduct_image_4_field(make_fnac_product, test_image_url):
    product = make_fnac_product(image_4=test_image_url)
    assert product.image_4 == test_image_url


@pytest.mark.django_db
def test_FnacProduct_image_4_field_can_be_empty(make_fnac_product):
    product = make_fnac_product(image_4="")
    assert product.image_4 == ""


@pytest.mark.django_db
def test_FnacProduct_do_not_create_field(make_fnac_product):
    product = make_fnac_product(do_not_create=True)
    assert product.do_not_create is True


@pytest.mark.django_db
def test_FnacProduct_created_field(make_fnac_product):
    product = make_fnac_product(created=True)
    assert product.created is True


@pytest.mark.django_db
def test_FnacProduct_str(make_fnac_product):
    fnac_product = make_fnac_product(sku="ABC-DEF-123", name="Test Name")
    assert str(fnac_product) == "ABC-DEF-123 - Test Name"


@pytest.mark.django_db
def test_out_of_stock_method(make_fnac_range, make_fnac_product):
    fnac_range = make_fnac_range()
    make_fnac_product(sku="493-HNF-339", stock_level=5, fnac_range=fnac_range)
    out_of_stock = make_fnac_product(
        sku="AKE-833-DKE", stock_level=0, fnac_range=fnac_range
    )
    assert list(models.FnacProduct.out_of_stock()) == [out_of_stock]


@pytest.mark.django_db
def test_in_stock_method(make_fnac_range, make_fnac_product):
    fnac_range = make_fnac_range()
    in_stock = make_fnac_product(
        sku="493-HNF-339", stock_level=5, fnac_range=fnac_range
    )
    make_fnac_product(sku="AKE-833-DKE", stock_level=0, fnac_range=fnac_range)
    assert list(models.FnacProduct.in_stock()) == [in_stock]
