import json
from unittest.mock import Mock, patch

from django.contrib.auth.models import Group

from price_calculator import models
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class PriceCalculatorViewTest(STCAdminTest):
    group_name = "inventory"

    def setUp(self):
        self.create_user()
        group = Group.objects.get(name=self.group_name)
        group.user_set.add(self.user)
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)


class TestPriceCalcualtorView(PriceCalculatorViewTest, ViewTests):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "price_calculator/destination_country",
        "price_calculator/package_type",
        "price_calculator/vat_rate",
        "price_calculator/shipping_price",
    )

    URL = "/price_calculator/price_calculator/"
    template = "price_calculator/price_calculator.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        context = response.context
        self.assertIn("countries", context)
        self.assertEqual(
            set(models.DestinationCountry.objects.all()), set(context["countries"])
        )
        self.assertIn("package_types", context)
        self.assertEqual(
            set(models.PackageType.objects.all()), set(context["package_types"])
        )
        self.assertIn("channel_fees", context)
        self.assertEqual(
            set(models.ChannelFee.objects.all()), set(context["channel_fees"])
        )


class TestRangePriceCalcualtorView(PriceCalculatorViewTest, ViewTests):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "price_calculator/destination_country",
        "price_calculator/package_type",
        "price_calculator/vat_rate",
        "price_calculator/shipping_price",
    )

    template = "price_calculator/range_price_calculator.html"
    range_ID = "3849383"

    def setUp(self):
        super().setUp()
        cc_products_patcher = patch("price_calculator.views.cc_products")
        self.mock_cc_products = cc_products_patcher.start()
        self.addCleanup(cc_products_patcher.stop)

    def get_URL(self, range_ID=None):
        if range_ID is None:
            range_ID = self.range_ID
        return f"/price_calculator/price_calculator/{range_ID}/"

    def test_get_method(self):
        mock_product_range = Mock(id=self.range_ID, products=[Mock(), Mock()])
        self.mock_cc_products.get_range.return_value = mock_product_range
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.mock_cc_products.get_range.assert_called_once()
        self.assertEqual(1, len(self.mock_cc_products.mock_calls))

    def test_context(self):
        mock_product_range = Mock(id=self.range_ID, products=[Mock(), Mock()])
        self.mock_cc_products.get_range.return_value = mock_product_range
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        context = response.context
        self.assertIn("product_range", context)
        self.assertEqual(mock_product_range, context["product_range"])
        self.assertIn("countries", context)
        self.assertEqual(
            set(models.DestinationCountry.objects.all()), set(context["countries"])
        )
        self.assertIn("channel_fees", context)
        self.assertEqual(
            set(models.ChannelFee.objects.all()), set(context["channel_fees"])
        )


class TestGetShippingPriceView(PriceCalculatorViewTest, ViewTests):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "price_calculator/destination_country",
        "price_calculator/package_type",
        "price_calculator/vat_rate",
        "price_calculator/shipping_price",
    )

    URL = "/price_calculator/get_shipping_price/"
    template = "price_calculator/range_price_calculator.html"

    def get_form_data(self):
        package_type = models.PackageType.objects.get(id=1)
        country = models.DestinationCountry.objects.get(id=1)
        return {
            "package_type": package_type.name,
            "international_shipping": "Domestic",
            "country": country.name,
            "weight": "500",
            "price": "300",
        }

    def test_post_method(self):
        form_data = self.get_form_data()
        response = self.client.post(self.URL, form_data)
        self.assertEqual(200, response.status_code)

    def test_content(self):
        form_data = self.get_form_data()
        response = self.client.post(self.URL, form_data)
        content = response.content.decode("utf8")
        data = json.loads(content)
        self.assertDictEqual(
            data,
            {
                "success": True,
                "price": 226,
                "price_name": "UK Packet",
                "vat_rates": [
                    {"cc_id": 5, "id": 1, "name": "20% VAT", "percentage": 20},
                    {"cc_id": 0, "id": 2, "name": "VAT Free", "percentage": 0},
                ],
                "exchange_rate": 0,
                "currency_code": "GBP",
                "currency_symbol": "£",
                "min_channel_fee": 0,
            },
        )

    def test_no_valid_shipping_service(self):
        form_data = self.get_form_data()
        form_data["price"] = 70000
        form_data["weight"] = 80000
        response = self.client.post(self.URL, form_data)
        content = response.content.decode("utf8")
        data = json.loads(content)
        self.assertDictEqual(
            data,
            {
                "success": False,
                "price": 0,
                "price_name": "No Shipping Service Found",
                "vat_rates": [],
                "exchange_rate": 0,
                "currency_code": "GBP",
                "currency_symbol": "£",
                "min_channel_fee": 0,
            },
        )

    def test_international(self):
        form_data = self.get_form_data()
        country = models.DestinationCountry.objects.get(id=3)
        form_data["country"] = country
        form_data["international_shipping"] = "Express"
        response = self.client.post(self.URL, form_data)
        content = response.content.decode("utf8")
        data = json.loads(content)
        self.assertDictEqual(
            data,
            {
                "success": True,
                "price": 900,
                "price_name": "Express Germany",
                "vat_rates": [
                    {"cc_id": 5, "id": 1, "name": "20% VAT", "percentage": 20},
                    {"cc_id": 0, "id": 2, "name": "VAT Free", "percentage": 0},
                ],
                "exchange_rate": country.exchange_rate,
                "currency_code": country.currency_code,
                "currency_symbol": country.currency_symbol,
                "min_channel_fee": 0,
            },
        )

    def test_min_channel_fee(self):
        form_data = self.get_form_data()
        country = models.DestinationCountry.objects.get(id=6)
        form_data["country"] = country
        response = self.client.post(self.URL, form_data)
        content = response.content.decode("utf8")
        data = json.loads(content)
        self.assertDictEqual(
            data,
            {
                "success": True,
                "price": 248,
                "price_name": "SMIU USA",
                "vat_rates": [],
                "exchange_rate": country.exchange_rate,
                "currency_code": country.currency_code,
                "currency_symbol": country.currency_symbol,
                "min_channel_fee": country.min_channel_fee * country.exchange_rate,
            },
        )
