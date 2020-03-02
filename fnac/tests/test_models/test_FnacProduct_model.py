import pytest
from django.db.utils import IntegrityError


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
def test_FnacProduct_name_field_is_unique(make_fnac_product):
    name = "Test Name"
    make_fnac_product(name=name)
    with pytest.raises(IntegrityError):
        make_fnac_product(name=name)


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
def test_FnacProduct_size_field(make_fnac_product, make_size):
    size = make_size()
    product = make_fnac_product(size=size)
    assert product.size == size


@pytest.mark.django_db
def test_FnacProduct_size_field_can_be_null(make_fnac_product):
    product = make_fnac_product(size=None)
    assert product.size is None


@pytest.mark.django_db
def test_FnacProduct_stock_level_field(make_fnac_product):
    stock_level = 63
    product = make_fnac_product(stock_level=stock_level)
    assert product.stock_level == stock_level


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
