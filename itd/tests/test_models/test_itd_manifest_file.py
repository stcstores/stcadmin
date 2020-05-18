import csv
from unittest.mock import Mock

import pytest

from itd.models import _ITDManifestFile


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def mock_order_product():
    def _mock_order_product(
        name="A Product", sku="ABC-DEF-GHI", weight=250, quantity=1
    ):
        return Mock(
            product_name=name, sku=sku, per_item_weight=weight, quantity=quantity
        )

    return _mock_order_product


@pytest.fixture
def delivery_address_string(
    address_1="1 Fake Street",
    address_2="Notown",
    city="Nowhere",
    region="Nullshire",
    postcode="NW1 0NW",
):
    def _delivery_address_string(address_1, address_2, city, region, postcode):
        address = "\t".join((address_1, address_2))
        return ",".join((address, city, region, postcode))

    return _delivery_address_string


@pytest.fixture
def mock_order(delivery_address_string, mock_order_product):
    def _mock_order(
        delivery_address=None,
        products=None,
        order_id="489161486",
        customer_id="849384943",
        country_code=1,
        delivery_name="Joe Bloggs",
        address_1="1 Fake Street",
        address_2="Notown",
        city="Nowhere",
        region="Nullshire",
        postcode="NW1 0NW",
        price="25.20",
    ):
        mock_order = Mock(
            order_id=order_id,
            customer_id=customer_id,
            delivery_country_code=country_code,
            delivery_name=delivery_name,
            total_gross_gbp=price,
        )
        mock_order.delilvery_address = delivery_address or delivery_address_string(
            address_1=address_1,
            address_2=address_2,
            city=city,
            region=region,
            postcode=postcode,
        )
        mock_order.products = products or [mock_order_product()]
        return mock_order

    return _mock_order


@pytest.fixture
def manifest_file_contents():
    def _manifest_file_contents(orders):
        manifest = _ITDManifestFile.create(orders)
        manifest.seek(0)
        reader = csv.reader(manifest)
        return list(reader)

    return _manifest_file_contents


@pytest.mark.django_db
def test_manifest_row(country, mock_order, mock_order_product, manifest_file_contents):
    product_name = "A Product"
    sku = "ABC-DEF-GHI"
    weight = 250
    order_id = "489161486"
    country_code = country.country_ID
    delivery_name = "Joe Bloggs"
    price = "25.20"
    address_1 = "1 Fake Street"
    address_2 = "Notown"
    city = "Nowhere"
    region = "Nullshire"
    postcode = "NW1 0NW"
    product = mock_order_product(sku=sku, name=product_name, weight=weight, quantity=1)
    order = mock_order(
        order_id=order_id,
        country_code=country_code,
        delivery_name=delivery_name,
        price=price,
        address_1=address_1,
        address_2=address_2,
        city=city,
        region=region,
        postcode=postcode,
        products=[product],
    )
    assert manifest_file_contents([order])[0] == [
        "Joe",
        "Bloggs",
        address_1,
        address_2,
        city,
        region,
        country.name,
        postcode,
        f"CCPpackord({order_id})",
        product_name,
        sku,
        f"{(weight/1000):.2f}",
        price,
    ]


@pytest.mark.django_db
def test_first_name_in_manifest(country, mock_order, manifest_file_contents):
    order = mock_order(delivery_name="Bill Johnson")
    manifest_contents = manifest_file_contents([order])
    assert manifest_contents[0][0] == "Bill"


@pytest.mark.django_db
def test_second_name_in_manifest(country, mock_order, manifest_file_contents):
    order = mock_order(delivery_name="Bill Johnson")
    manifest_contents = manifest_file_contents([order])
    assert manifest_contents[0][1] == "Johnson"


@pytest.mark.django_db
def test_single_name_in_manifest(country, mock_order, manifest_file_contents):
    order = mock_order(delivery_name="Johnson")
    manifest_contents = manifest_file_contents([order])
    assert manifest_contents[0][0] == "First name"
    assert manifest_contents[0][1] == "Johnson"


@pytest.mark.django_db
def test_tracking_number_in_address_is_ignored(
    country, mock_order, manifest_file_contents
):
    order = mock_order(postcode="NW38 H85 (3189161648161)")
    manifest_contents = manifest_file_contents([order])
    assert manifest_contents[0][7] == "NW38 H85"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "address_string,line_1,line_2",
    [
        ("123 Fake Street\tNowhere", "123 Fake Street", "Nowhere"),
        ("123 Fake Street, Nowhere", "123 Fake Street Nowhere", ""),
        (" 123 Fake Street \t Nowhere ", "123 Fake Street", "Nowhere"),
        ("123 Fake, Street\tNow, here", "123 Fake Street", "Now here"),
        ("123 Fake Street\tNowhere#61614686", "123 Fake Street", "Nowhere"),
        (
            "54675489 Fake Street 12345679 156486161351",
            "54675489 Fake Street 12345679",
            "156486161351",
        ),
        (
            "54675489 Fake Street 12345679 156486161351\tNowhere",
            "54675489 Fake Street 12345679",
            "156486161351 Nowhere",
        ),
        (
            "54675489 Fake Street 12345679 156486161351 \t Nowhere",
            "54675489 Fake Street 12345679",
            "156486161351 Nowhere",
        ),
        (
            "54675489FakeStreet12345679156486161351",
            "54675489FakeStreet12345679156486161",
            "351",
        ),
    ],
)
def test_address_string_split(
    country, mock_order, manifest_file_contents, address_string, line_1, line_2
):
    rest_of_address_string = ",Notown,Nullshire,NW20 5NW"
    delivery_address = address_string + rest_of_address_string
    order = mock_order(delivery_address=delivery_address)
    manifest_contents = manifest_file_contents([order])
    assert manifest_contents[0][2] == line_1
    assert manifest_contents[0][3] == line_2
