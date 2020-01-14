from price_calculator import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestShippingRegion(STCAdminTest):
    fixtures = ("price_calculator/shipping_region",)

    def test_create_object(self):
        name = "Test Region"
        region = models.ShippingRegion.objects.create(name=name)
        self.assertEqual(name, region.name)

    def test_str_method(self):
        region = models.ShippingRegion.objects.get(id=1)
        self.assertEqual(str(region), region.name)


class TestDestinationCountry(STCAdminTest):
    fixtures = (
        "price_calculator/shipping_region",
        "price_calculator/destination_country",
    )

    def test_create_object(self):
        name = "New Land"
        min_channel_fee = 9
        shipping_region = models.ShippingRegion.objects.get(id=1)
        exchange_rate = 1.3
        country = models.DestinationCountry.objects.create(
            name=name,
            min_channel_fee=min_channel_fee,
            shipping_region=shipping_region,
            exchange_rate=exchange_rate,
        )
        self.assertEqual(name, country.name)
        self.assertEqual("GBP", country.currency_code)
        self.assertEqual("£", country.currency_symbol)
        self.assertEqual(min_channel_fee, country.min_channel_fee)
        self.assertEqual(shipping_region, country.shipping_region)
        self.assertEqual(exchange_rate, country.exchange_rate)
        self.assertEqual(0, country.sort_order)

    def test_str_method(self):
        country = models.DestinationCountry.objects.get(id=1)
        self.assertEqual(str(country), country.name)


class TestPackageType(STCAdminTest):
    fixtures = ("price_calculator/package_type",)

    def test_create_object(self):
        name = "New Package Type"
        package_type = models.PackageType.objects.create(name=name)
        self.assertEqual(name, package_type.name)

    def test_str_method(self):
        package_type = models.PackageType.objects.get(id=1)
        self.assertEqual(package_type.name, str(package_type))


class TestVATRate(STCAdminTest):
    fixtures = ("price_calculator/vat_rate",)

    def test_create_object(self):
        name = "New VAT Rate"
        cc_id = 7
        percentage = 37
        vat_rate = models.VATRate.objects.create(
            name=name, cc_id=cc_id, percentage=percentage
        )
        self.assertEqual(name, vat_rate.name)
        self.assertEqual(cc_id, vat_rate.cc_id)
        self.assertEqual(percentage, vat_rate.percentage)

    def test_str_method(self):
        vat_rate = models.VATRate.objects.get(id=1)
        self.assertEqual(vat_rate.name, str(vat_rate))


class TestChannelFee(STCAdminTest):
    fixtures = ("price_calculator/channel_fee",)

    def test_create_object(self):
        name = "New Channel Fee"
        fee_percentage = 14
        channel_fee = models.ChannelFee.objects.create(
            name=name, fee_percentage=fee_percentage
        )
        self.assertEqual(name, channel_fee.name)
        self.assertEqual(fee_percentage, channel_fee.fee_percentage)
        self.assertEqual(100, channel_fee.ordering)

    def test_str_method(self):
        channel_fee = models.ChannelFee.objects.get(id=1)
        self.assertEqual(channel_fee.name, str(channel_fee))


class TestShippingPrice(STCAdminTest):
    fixtures = (
        "price_calculator/shipping_region",
        "price_calculator/destination_country",
        "price_calculator/package_type",
        "price_calculator/vat_rate",
        "price_calculator/shipping_price",
    )

    def test_create_object(self):
        name = "New Shipping Price"
        country = models.DestinationCountry.objects.get(id=1)
        package_types = [models.PackageType.objects.get(id=1)]
        min_weight = 50
        max_weight = 1500
        min_price = 200
        max_price = 500
        item_price = 600
        kilo_price = 24
        vat_rates = [models.VATRate.objects.get(id=1)]
        disabled = True
        shipping_price = models.ShippingPrice.objects.create(
            name=name,
            country=country,
            min_weight=min_weight,
            max_weight=max_weight,
            min_price=min_price,
            max_price=max_price,
            item_price=item_price,
            kilo_price=kilo_price,
            disabled=disabled,
        )
        shipping_price.package_type.set(package_types)
        shipping_price.vat_rates.set(vat_rates)
        shipping_price.refresh_from_db()
        self.assertEqual(name, shipping_price.name)
        self.assertEqual(country, shipping_price.country)
        self.assertEqual(package_types, list(shipping_price.package_type.all()))
        self.assertEqual(min_weight, shipping_price.min_weight)
        self.assertEqual(max_weight, shipping_price.max_weight)
        self.assertEqual(min_price, shipping_price.min_price)
        self.assertEqual(max_price, shipping_price.max_price)
        self.assertEqual(item_price, shipping_price.item_price)
        self.assertEqual(kilo_price, shipping_price.kilo_price)
        self.assertEqual(vat_rates, list(shipping_price.vat_rates.all()))
        self.assertEqual(disabled, shipping_price.disabled)

    def test_str_method(self):
        shipping_price = models.ShippingPrice.objects.get(id=1)
        self.assertEqual(shipping_price.name, str(shipping_price))

    def test_calculate_kilos_method(self):
        shipping_price = models.ShippingPrice.objects.get(id=1)
        shipping_price.kilo_price = 500
        self.assertEqual(1000, shipping_price.calculate_kilos(2000))
        self.assertEqual(25, shipping_price.calculate_kilos(50))
        self.assertEqual(5, shipping_price.calculate_kilos(10))
        shipping_price.kilo_price = 140
        self.assertEqual(280, shipping_price.calculate_kilos(2000))
        self.assertEqual(7, shipping_price.calculate_kilos(50))
        self.assertEqual(1, shipping_price.calculate_kilos(10))
        shipping_price.kilo_price = None
        self.assertEqual(0, shipping_price.calculate_kilos(2000))
        self.assertEqual(0, shipping_price.calculate_kilos(50))
        self.assertEqual(0, shipping_price.calculate_kilos(10))

    def test_calculcate_method(self):
        shipping_price = models.ShippingPrice.objects.get(id=1)
        shipping_price.kilo_price = 500
        shipping_price.item_price = 25
        self.assertEqual(1025, shipping_price.calculate(2000))
        self.assertEqual(50, shipping_price.calculate(50))
        self.assertEqual(30, shipping_price.calculate(10))
        shipping_price.kilo_price = 140
        self.assertEqual(305, shipping_price.calculate(2000))
        self.assertEqual(32, shipping_price.calculate(50))
        self.assertEqual(26, shipping_price.calculate(10))
        shipping_price.kilo_price = None
        self.assertEqual(25, shipping_price.calculate(2000))
        self.assertEqual(25, shipping_price.calculate(50))
        self.assertEqual(25, shipping_price.calculate(10))

    def test_package_type_string_method(self):
        package_types = [
            models.PackageType.objects.create(name="Foo"),
            models.PackageType.objects.create(name="Bar"),
            models.PackageType.objects.create(name="Baz"),
        ]
        shipping_price = models.ShippingPrice.objects.get(id=1)
        shipping_price.package_type.set(package_types)
        self.assertEqual("Foo, Bar, Baz", shipping_price.package_type_string())

    def test_get_price(self):
        country = models.DestinationCountry.objects.get(id=1)
        package_type = models.PackageType.objects.get(id=1)
        price_id = models.ShippingPrice.get_price(
            country_name=country.name,
            package_type_name=package_type.name,
            weight=500,
            price=2250,
        )
        self.assertIsInstance(price_id, models.ShippingPrice)


class TestShippingPriceGetPriceMethod(STCAdminTest):
    fixtures = (
        "price_calculator/shipping_region",
        "price_calculator/destination_country",
        "price_calculator/package_type",
        "price_calculator/vat_rate",
    )

    def setUp(self):
        self.country = models.DestinationCountry.objects.get(id=1)
        self.package_type = models.PackageType.objects.get(id=1)
        package_types = [self.package_type]
        vat_rates = [models.VATRate.objects.get(id=1)]
        shipping_price = models.ShippingPrice.objects.create(
            name="New Shipping Price",
            country=self.country,
            min_weight=50,
            max_weight=1500,
            min_price=200,
            max_price=500,
            item_price=600,
            kilo_price=24,
        )
        shipping_price.package_type.set(package_types)
        shipping_price.vat_rates.set(vat_rates)
        self.shipping_price = shipping_price

    def test_matching_filter(self):
        returned_shipping_price = models.ShippingPrice.get_price(
            country_name=self.country.name,
            package_type_name=self.package_type.name,
            weight=500,
            price=300,
        )
        self.assertEqual(self.shipping_price, returned_shipping_price)

    def test_filter_min_weight(self):
        with self.assertRaises(models.DestinationCountry.NoShippingService):
            models.ShippingPrice.get_price(
                country_name=self.country.name,
                package_type_name=self.package_type.name,
                weight=49,
                price=300,
            )

    def test_filter_max_weight(self):
        with self.assertRaises(models.DestinationCountry.NoShippingService):
            models.ShippingPrice.get_price(
                country_name=self.country.name,
                package_type_name=self.package_type.name,
                weight=1501,
                price=300,
            )

    def test_get_price_filter_min_price(self):
        with self.assertRaises(models.DestinationCountry.NoShippingService):
            models.ShippingPrice.get_price(
                country_name=self.country.name,
                package_type_name=self.package_type.name,
                weight=100,
                price=199,
            )

    def test_get_price_filter_max_price(self):
        with self.assertRaises(models.DestinationCountry.NoShippingService):
            models.ShippingPrice.get_price(
                country_name=self.country.name,
                package_type_name=self.package_type.name,
                weight=100,
                price=601,
            )

    def test_filter_country(self):
        with self.assertRaises(models.DestinationCountry.NoShippingService):
            models.ShippingPrice.get_price(
                country_name=models.DestinationCountry.objects.get(id=2).name,
                package_type_name=self.package_type.name,
                weight=100,
                price=300,
            )

    def test_filter_package_type(self):
        with self.assertRaises(models.DestinationCountry.NoShippingService):
            models.ShippingPrice.get_price(
                country_name=self.country.name,
                package_type_name=models.PackageType.objects.get(id=2).name,
                weight=100,
                price=300,
            )

    def test_filter_disabled(self):
        self.shipping_price.disabled = True
        self.shipping_price.save()
        with self.assertRaises(models.DestinationCountry.NoShippingService):
            models.ShippingPrice.get_price(
                country_name=self.country.name,
                package_type_name=self.package_type.name,
                weight=500,
                price=300,
            )

    def test_returns_null_max_weight(self):
        self.shipping_price.max_weight = None
        self.shipping_price.save()
        shipping_price = models.ShippingPrice.get_price(
            country_name=self.country.name,
            package_type_name=self.package_type.name,
            weight=500000,
            price=300,
        )
        self.assertEqual(self.shipping_price, shipping_price)

    def test_returns_null_min_weight(self):
        self.shipping_price.min_weight = None
        self.shipping_price.save()
        shipping_price = models.ShippingPrice.get_price(
            country_name=self.country.name,
            package_type_name=self.package_type.name,
            weight=0,
            price=300,
        )
        self.assertEqual(self.shipping_price, shipping_price)

    def test_returns_null_max_price(self):
        self.shipping_price.max_price = None
        self.shipping_price.save()
        shipping_price = models.ShippingPrice.get_price(
            country_name=self.country.name,
            package_type_name=self.package_type.name,
            weight=500,
            price=30000000,
        )
        self.assertEqual(self.shipping_price, shipping_price)

    def test_returns_null_min_price(self):
        self.shipping_price.min_price = None
        self.shipping_price.save()
        shipping_price = models.ShippingPrice.get_price(
            country_name=self.country.name,
            package_type_name=self.package_type.name,
            weight=500,
            price=0,
        )
        self.assertEqual(self.shipping_price, shipping_price)
