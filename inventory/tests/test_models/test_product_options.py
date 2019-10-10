from unittest.mock import Mock, patch

from inventory import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestProductOption(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.product_option = models.ProductOption.objects.create(
            name="Size", product_option_ID="38473"
        )

    def test_str_method(self):
        self.assertEqual(str(self.product_option), self.product_option.name)

    def test_active_property(self):
        self.assertTrue(self.product_option.active)
        self.product_option.inactive = True
        self.product_option.save()
        self.assertFalse(self.product_option.active)

    @patch("inventory.models.product_options.CCAPI")
    def test_cc_product_option_values_method(self, mock_CCAPI):
        value = Mock()
        mock_CCAPI.get_product_options.return_value = {"Size": value}
        return_value = self.product_option.cc_product_option_values()
        self.assertEqual(return_value, value)
        mock_CCAPI.get_product_options.assert_called_once()


class TestProductOptionValue(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.product_option = models.ProductOption.objects.create(
            name="Size", product_option_ID="38473"
        )
        cls.product_option_value = models.ProductOptionValue.objects.create(
            value="Small",
            product_option=cls.product_option,
            product_option_value_ID="65461",
        )

    @patch("inventory.models.product_options.CCAPI")
    def test_get_product_options_method(self, mock_CCAPI):
        with self.assertRaises(NotImplementedError):
            self.product_option_value.get_product_options()

    def test_str_method(self):
        self.assertEqual(str(self.product_option_value), "Size: Small")

    @patch("inventory.models.product_options.CCAPI")
    def test_save_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        value = models.ProductOptionValue.objects.create(
            value="Medium", product_option=self.product_option
        )
        self.assertEqual(value.product_option_value_ID, "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            self.product_option.product_option_ID, "Medium"
        )

    @patch("inventory.models.product_options.CCAPI")
    def test_create_CC_product_option_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        value = models.ProductOptionValue(
            value="Medium", product_option=self.product_option
        )
        self.assertEqual(value.create_CC_product_option("Medium"), "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            self.product_option.product_option_ID, "Medium"
        )


class TestDepartment(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.department = models.Department.objects.create(
            name="Test Department", product_option_value_ID="48292"
        )

    def test_active_property(self):
        self.assertTrue(self.department.active)
        self.department.inactive = True
        self.department.save()
        self.assertFalse(self.department.active)

    @patch("inventory.models.product_options.CCAPI")
    def test_get_product_options_method(self, mock_CCAPI):
        value = Mock()
        mock_CCAPI.get_product_options.return_value = {
            models.Department.PRODUCT_OPTION_NAME: value
        }
        return_value = self.department.get_product_options()
        self.assertEqual(return_value, value)
        mock_CCAPI.get_product_options.assert_called_once()

    def test_str_method(self):
        self.assertEqual(str(self.department), self.department.name)

    @patch("inventory.models.product_options.CCAPI")
    def test_save_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        value = models.Department.objects.create(name="Department 2")
        self.assertEqual(value.product_option_value_ID, "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.Department.PRODUCT_OPTION_ID, value.name
        )

    @patch("inventory.models.product_options.CCAPI")
    def test_create_CC_product_option_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        self.assertEqual(self.department.create_CC_product_option("Medium"), "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.Department.PRODUCT_OPTION_ID, "Medium"
        )

    def test_default_warehouse_method(self):
        self.assertIsNone(self.department.default_warehouse())
        warehouse = models.Warehouse.objects.create(
            name=self.department.name, warehouse_ID="294093"
        )
        self.assertEqual(self.department.default_warehouse(), warehouse)

    def test_default_bay_method(self):
        self.assertIsNone(self.department.default_bay())
        warehouse = models.Warehouse.objects.create(
            name=self.department.name, warehouse_ID="294093"
        )
        bay = models.Bay.objects.create(
            name=self.department.name,
            bay_ID="284923",
            warehouse=warehouse,
            is_default=True,
        )
        self.assertEqual(self.department.default_bay(), bay)


class TestPackageType(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.package_type = models.PackageType.objects.create(
            name="Standard Shipping",
            product_option_value_ID="48284",
            large_letter_compatible=True,
        )

    def test_active_property(self):
        self.assertTrue(self.package_type.active)
        self.package_type.inactive = True
        self.package_type.save()
        self.assertFalse(self.package_type.active)

    @patch("inventory.models.product_options.CCAPI")
    def test_get_product_options_method(self, mock_CCAPI):
        value = Mock()
        mock_CCAPI.get_product_options.return_value = {
            models.PackageType.PRODUCT_OPTION_NAME: value
        }
        return_value = self.package_type.get_product_options()
        self.assertEqual(return_value, value)
        mock_CCAPI.get_product_options.assert_called_once()

    def test_str_method(self):
        self.assertEqual(str(self.package_type), self.package_type.name)

    @patch("inventory.models.product_options.CCAPI")
    def test_save_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        value = models.PackageType.objects.create(
            name="Expedited Shipping", large_letter_compatible=False
        )
        self.assertEqual(value.product_option_value_ID, "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.PackageType.PRODUCT_OPTION_ID, value.name
        )

    @patch("inventory.models.product_options.CCAPI")
    def test_create_CC_product_option_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        self.assertEqual(self.package_type.create_CC_product_option("Medium"), "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.PackageType.PRODUCT_OPTION_ID, "Medium"
        )


class TestInternationalShipping(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.international_shipping = models.InternationalShipping.objects.create(
            name="Standard Shipping", product_option_value_ID="48284"
        )

    def test_active_property(self):
        self.assertTrue(self.international_shipping.active)
        self.international_shipping.inactive = True
        self.international_shipping.save()
        self.assertFalse(self.international_shipping.active)

    @patch("inventory.models.product_options.CCAPI")
    def test_get_product_options_method(self, mock_CCAPI):
        value = Mock()
        mock_CCAPI.get_product_options.return_value = {
            models.InternationalShipping.PRODUCT_OPTION_NAME: value
        }
        return_value = self.international_shipping.get_product_options()
        self.assertEqual(return_value, value)
        mock_CCAPI.get_product_options.assert_called_once()

    def test_str_method(self):
        self.assertEqual(
            str(self.international_shipping), self.international_shipping.name
        )

    @patch("inventory.models.product_options.CCAPI")
    def test_save_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        value = models.InternationalShipping.objects.create(name="Expedited Shipping")
        self.assertEqual(value.product_option_value_ID, "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.InternationalShipping.PRODUCT_OPTION_ID, value.name
        )

    @patch("inventory.models.product_options.CCAPI")
    def test_create_CC_product_option_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        self.assertEqual(
            self.international_shipping.create_CC_product_option("Medium"), "89461"
        )
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.InternationalShipping.PRODUCT_OPTION_ID, "Medium"
        )


class TestBrand(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.brand = models.Brand.objects.create(
            name="Stock Inc", product_option_value_ID="48284"
        )

    def test_active_property(self):
        self.assertTrue(self.brand.active)
        self.brand.inactive = True
        self.brand.save()
        self.assertFalse(self.brand.active)

    @patch("inventory.models.product_options.CCAPI")
    def test_get_product_options_method(self, mock_CCAPI):
        value = Mock()
        mock_CCAPI.get_product_options.return_value = {
            models.Brand.PRODUCT_OPTION_NAME: value
        }
        return_value = self.brand.get_product_options()
        self.assertEqual(return_value, value)
        mock_CCAPI.get_product_options.assert_called_once()

    def test_str_method(self):
        self.assertEqual(str(self.brand), self.brand.name)

    @patch("inventory.models.product_options.CCAPI")
    def test_save_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        value = models.Brand.objects.create(name="Expedited Shipping")
        self.assertEqual(value.product_option_value_ID, "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.Brand.PRODUCT_OPTION_ID, value.name
        )

    @patch("inventory.models.product_options.CCAPI")
    def test_create_CC_product_option_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        self.assertEqual(self.brand.create_CC_product_option("Medium"), "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.Brand.PRODUCT_OPTION_ID, "Medium"
        )


class TestManufacturer(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.manufacturer = models.Manufacturer.objects.create(
            name="Stock Inc", product_option_value_ID="48284"
        )

    def test_active_property(self):
        self.assertTrue(self.manufacturer.active)
        self.manufacturer.inactive = True
        self.manufacturer.save()
        self.assertFalse(self.manufacturer.active)

    @patch("inventory.models.product_options.CCAPI")
    def test_get_product_options_method(self, mock_CCAPI):
        value = Mock()
        mock_CCAPI.get_product_options.return_value = {
            models.Manufacturer.PRODUCT_OPTION_NAME: value
        }
        return_value = self.manufacturer.get_product_options()
        self.assertEqual(return_value, value)
        mock_CCAPI.get_product_options.assert_called_once()

    def test_str_method(self):
        self.assertEqual(str(self.manufacturer), self.manufacturer.name)

    @patch("inventory.models.product_options.CCAPI")
    def test_save_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        value = models.Manufacturer.objects.create(name="Expedited Shipping")
        self.assertEqual(value.product_option_value_ID, "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.Manufacturer.PRODUCT_OPTION_ID, value.name
        )

    @patch("inventory.models.product_options.CCAPI")
    def test_create_CC_product_option_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        self.assertEqual(self.manufacturer.create_CC_product_option("Medium"), "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.Manufacturer.PRODUCT_OPTION_ID, "Medium"
        )


class TestGender(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.gender = models.Gender.objects.create(
            name="mens", readable_name="Mens", product_option_value_ID="48284"
        )

    def test_active_property(self):
        self.assertTrue(self.gender.active)
        self.gender.inactive = True
        self.gender.save()
        self.assertFalse(self.gender.active)

    @patch("inventory.models.product_options.CCAPI")
    def test_get_product_options_method(self, mock_CCAPI):
        value = Mock()
        mock_CCAPI.get_product_options.return_value = {
            models.Gender.PRODUCT_OPTION_NAME: value
        }
        return_value = self.gender.get_product_options()
        self.assertEqual(return_value, value)
        mock_CCAPI.get_product_options.assert_called_once()

    def test_str_method(self):
        self.assertEqual(str(self.gender), self.gender.readable_name)

    @patch("inventory.models.product_options.CCAPI")
    def test_save_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        value = models.Gender.objects.create(name="womens", readable_name="Womens")
        self.assertEqual(value.product_option_value_ID, "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.Gender.PRODUCT_OPTION_ID, value.name
        )

    @patch("inventory.models.product_options.CCAPI")
    def test_create_CC_product_option_method(self, mock_CCAPI):
        mock_CCAPI.create_option_value.return_value = "89461"
        self.assertEqual(self.gender.create_CC_product_option("Medium"), "89461")
        mock_CCAPI.create_option_value.assert_called_once_with(
            models.Gender.PRODUCT_OPTION_ID, "Medium"
        )
