from unittest.mock import Mock, patch

from home.tests.test_views.view_test import ViewTest
from inventory import models
from inventory.cloud_commerce_updater import PartialRangeUpdater, RangeUpdater
from inventory.tests.test_models.test_products import SetupVariationProductRange


class RangeUpdaterTests:
    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_set_name(self, mock_CCAPI):
        mock_product_range = Mock()
        mock_CCAPI.get_range.return_value = mock_product_range
        original_name = self.product_range.name
        new_name = "New Product Range Name"
        self.updater.set_name(new_name)
        if self.update_DB:
            self.assertEqual(new_name, self.product_range.name)
        else:
            self.assertEqual(original_name, self.product_range.name)
        if self.update_CC:
            mock_CCAPI.get_range.assert_called_once_with(self.product_range.range_ID)
            mock_product_range.set_name.assert_called_once_with(new_name)
            mock_CCAPI.set_product_name.assert_called_once_with(
                name=new_name, product_ids=self.product_IDs
            )
        else:
            mock_CCAPI.get_range.assert_not_called()
            mock_CCAPI.set_product_name.assert_not_called()

    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_set_department(self, mock_CCAPI):
        original_department = self.product_range.department
        department = models.Department.objects.create(
            name="New Department", product_option_value_ID="385093"
        )
        self.updater.set_department(department)
        if self.update_DB:
            self.assertEqual(department, self.product_range.department)
        else:
            self.assertEqual(original_department, self.product_range.department)
        if self.update_CC:
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=self.product_IDs,
                option_id=models.Department.PRODUCT_OPTION_ID,
                option_value_id=department.product_option_value_ID,
            )
        else:
            mock_CCAPI.set_product_option_value.assert_not_called()

    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_set_description(self, mock_CCAPI):
        original_description = self.product_range.description
        new_description = "A description\nOf a product."
        self.updater.set_description(new_description)
        if self.update_DB:
            self.assertEqual(new_description, self.product_range.description)
        else:
            self.assertEqual(original_description, self.product_range.description)
        if self.update_CC:
            mock_CCAPI.set_product_description.assert_called_once_with(
                product_ids=self.product_IDs, description=new_description
            )
        else:
            mock_CCAPI.set_product_description.assert_not_called()

    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_set_amazon_search_terms(self, mock_CCAPI):
        original_search_terms = self.product_range.amazon_search_terms
        new_search_terms = "Mug|Cup|Drink Container"
        product_option_value_ID = "284938"
        mock_CCAPI.get_option_value_id.return_value = product_option_value_ID
        self.updater.set_amazon_search_terms(new_search_terms)
        if self.update_DB:
            self.assertEqual(new_search_terms, self.product_range.amazon_search_terms)
        else:
            self.assertEqual(
                original_search_terms, self.product_range.amazon_search_terms
            )
        if self.update_CC:
            mock_CCAPI.get_option_value_id.assert_called_once_with(
                self.updater.AMAZON_SEARCH_TERMS_OPTION_ID,
                value=new_search_terms,
                create=True,
            )
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=self.product_IDs,
                option_id=self.updater.AMAZON_SEARCH_TERMS_OPTION_ID,
                option_value_id=product_option_value_ID,
            )
        else:
            mock_CCAPI.get_option_value_id.assert_not_called()
            mock_CCAPI.set_product_option_value.assert_not_called()

    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_set_amazon_bullet_points(self, mock_CCAPI):
        original_bullet_points = self.product_range.amazon_bullet_points
        new_bullet_points = "Mug|Cup|Drink Container"
        product_option_value_ID = "9465161"
        mock_CCAPI.get_option_value_id.return_value = product_option_value_ID
        self.updater.set_amazon_bullet_points(new_bullet_points)
        if self.update_DB:
            self.assertEqual(new_bullet_points, self.product_range.amazon_bullet_points)
        else:
            self.assertEqual(
                original_bullet_points, self.product_range.amazon_bullet_points
            )
        if self.update_CC:
            mock_CCAPI.get_option_value_id.assert_called_once_with(
                self.updater.AMAZON_BULLET_POINTS_OPTION_ID,
                value=new_bullet_points,
                create=True,
            )
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=self.product_IDs,
                option_id=self.updater.AMAZON_BULLET_POINTS_OPTION_ID,
                option_value_id=product_option_value_ID,
            )
        else:
            mock_CCAPI.get_option_value_id.assert_not_called()
            mock_CCAPI.set_product_option_value.assert_not_called()

    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_set_end_of_line(self, mock_CCAPI):
        mock_product_range = Mock()
        mock_CCAPI.get_range.return_value = mock_product_range
        original_value = self.product_range.end_of_line
        new_value = not original_value
        self.updater.set_end_of_line(new_value)
        if self.update_DB:
            self.assertEqual(new_value, self.product_range.end_of_line)
        else:
            self.assertEqual(original_value, self.product_range.end_of_line)
        if self.update_CC:
            mock_CCAPI.get_range.assert_called_once_with(self.product_range.range_ID)
            mock_product_range.set_end_of_line.assert_called_once_with(new_value)
        else:
            mock_CCAPI.get_range.assert_not_called()
            mock_product_range.set_end_of_line.assert_not_called()

    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_add_variation_product_option(self, mock_CCAPI):
        product_option = models.ProductOption.objects.create(
            name="Shape", product_option_ID="299438"
        )
        self.updater.add_variation_product_option(product_option)
        queryset = self.updater.product_range_selected_option_model.objects.filter(
            product_range=self.product_range, product_option=product_option
        )
        if self.update_DB:
            self.assertEqual(queryset.count(), 1)
            self.assertTrue(queryset.all()[0].variation)
        else:
            self.assertFalse(queryset.exists())
        if self.update_CC:
            mock_CCAPI.add_option_to_product.assert_called_once_with(
                range_id=self.product_range.range_ID,
                option_id=product_option.product_option_ID,
            )
            mock_CCAPI.set_range_option_drop_down.assert_called_once_with(
                range_id=self.product_range.range_ID,
                option_id=product_option.product_option_ID,
                drop_down=True,
            )
        else:
            mock_CCAPI.add_option_to_product.assert_not_called()
            mock_CCAPI.set_range_option_drop_down.assert_not_called()

    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_add_variation_product_option_updates_listing_options(self, mock_CCAPI):
        product_option = models.ProductOption.objects.create(
            name="Design", product_option_ID="3840382"
        )
        self.updater.product_range_selected_option_model.objects.create(
            product_range=self.product_range,
            product_option=product_option,
            variation=False,
        )
        self.updater.add_variation_product_option(product_option)
        selected_option = self.updater.product_range_selected_option_model.objects.get(
            product_range=self.product_range, product_option=product_option
        )
        if self.update_DB:
            self.assertTrue(selected_option.variation)
        else:
            self.assertFalse(selected_option.variation)

    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_add_listing_product_option(self, mock_CCAPI):
        product_option = models.ProductOption.objects.create(
            name="Shape", product_option_ID="299438"
        )
        self.updater.add_listing_product_option(product_option)
        queryset = self.updater.product_range_selected_option_model.objects.filter(
            product_range=self.product_range, product_option=product_option
        )
        if self.update_DB:
            self.assertEqual(queryset.count(), 1)
            self.assertFalse(queryset.all()[0].variation)
        else:
            self.assertFalse(queryset.exists())
        if self.update_CC:
            mock_CCAPI.add_option_to_product.assert_called_once_with(
                range_id=self.product_range.range_ID,
                option_id=product_option.product_option_ID,
            )
            mock_CCAPI.set_range_option_drop_down.assert_called_once_with(
                range_id=self.product_range.range_ID,
                option_id=product_option.product_option_ID,
                drop_down=False,
            )
        else:
            mock_CCAPI.add_option_to_product.assert_not_called()
            mock_CCAPI.set_range_option_drop_down.assert_not_called()

    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_add_listing_product_option_updates_variation_options(self, mock_CCAPI):
        product_option = self.size_product_option
        self.updater.add_listing_product_option(product_option)
        selected_option = self.updater.product_range_selected_option_model.objects.get(
            product_range=self.product_range, product_option=product_option
        )
        if self.update_DB:
            self.assertFalse(selected_option.variation)
        else:
            self.assertTrue(selected_option.variation)

    @patch("inventory.cloud_commerce_updater.range_updater.CCAPI")
    def test_remove_product_option(self, mock_CCAPI):
        mock_product_range = Mock()
        mock_CCAPI.get_range.return_value = mock_product_range
        product_option = self.colour_product_option
        self.updater.remove_product_option(product_option)
        if self.update_DB:
            self.assertFalse(
                self.updater.product_option_value_link_model.objects.filter(
                    product__product_ID__in=self.product_IDs,
                    product_option_value__product_option=product_option,
                ).exists()
            )
            self.assertFalse(
                self.updater.product_range_selected_option_model.objects.filter(
                    product_range=self.product_range, product_option=product_option
                ).exists()
            )
        else:
            self.assertTrue(
                self.updater.product_option_value_link_model.objects.filter(
                    product__product_ID__in=self.product_IDs,
                    product_option_value__product_option=product_option,
                ).exists()
            )
            self.assertTrue(
                self.updater.product_range_selected_option_model.objects.filter(
                    product_range=self.product_range, product_option=product_option
                ).exists()
            )
        if self.update_CC:
            mock_CCAPI.remove_option_from_product.assert_called_once_with(
                range_id=self.product_range.range_ID,
                option_id=product_option.product_option_ID,
            )
        else:
            mock_CCAPI.remove_option_from_product.assert_not_called()


class TestRangeUpdater(SetupVariationProductRange, RangeUpdaterTests, ViewTest):
    updater_class = RangeUpdater
    update_DB = True
    update_CC = True

    def setUp(self):
        super(SetupVariationProductRange, self).setUp()
        self.product_edit = models.ProductEdit.create_product_edit(
            self.user, self.product_range
        )
        self.updater = self.updater_class(self.product_range, self.user)
        self.product_IDs = [_.product_ID for _ in self.product_range.products()]


class TestPartialRangeUpdater(SetupVariationProductRange, RangeUpdaterTests, ViewTest):
    updater_class = PartialRangeUpdater
    update_DB = True
    update_CC = False

    def setUp(self):
        super(SetupVariationProductRange, self).setUp()
        self.product_edit = models.ProductEdit.create_product_edit(
            self.user, self.product_range
        )
        self.original_range = self.product_edit.product_range
        self.product_range = self.product_edit.partial_product_range
        self.product = self.product_range.products()[0]
        self.updater = self.updater_class(self.product_range, self.user)
        self.product_IDs = [_.product_ID for _ in self.product_range.products()]


class TestRangeUpdaterWithoutDB(
    SetupVariationProductRange, RangeUpdaterTests, ViewTest
):
    updater_class = RangeUpdater
    update_DB = False
    update_CC = False

    def setUp(self):
        super(SetupVariationProductRange, self).setUp()
        self.product_edit = models.ProductEdit.create_product_edit(
            self.user, self.product_range
        )
        self.updater = self.updater_class(self.product_range, self.user)
        self.updater.update_DB = False
        self.updater.update_CC = False
        self.product_IDs = [_.product_ID for _ in self.product_range.products()]
