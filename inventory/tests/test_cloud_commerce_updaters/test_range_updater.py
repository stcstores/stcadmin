from unittest.mock import Mock

from inventory import models
from inventory.cloud_commerce_updater import PartialRangeUpdater, RangeUpdater
from inventory.tests import fixtures

from .test_updater_base import BaseUpdaterMethodTest, BaseUpdaterTest


class BaseRangeUpdaterTest(BaseUpdaterTest):
    patch_path = "inventory.cloud_commerce_updater.range_updater.CCAPI"

    def setUp(self):
        super().setUp()
        self.product_IDs = [_.product_ID for _ in self.product_range.products()]

    def updater_object(self):
        return self.product_range


class RangeUpdaterTest(BaseRangeUpdaterTest, fixtures.VariationProductRangeFixture):

    updater_class = RangeUpdater

    def test_update_DB(self):
        self.update_DB_test()

    def test_update_CC(self):
        self.update_CC_test()


class PartialRangeUpdaterTest(BaseRangeUpdaterTest, fixtures.EditingProductFixture):
    updater_class = PartialRangeUpdater

    def test_update_DB(self):
        print(self.product_range)
        self.update_DB_test()

    def test_update_CC(self):
        self.no_CC_update_test()


class NoChangeRangeUpdaterTest(
    BaseRangeUpdaterTest, fixtures.VariationProductRangeFixture
):
    updater_class = RangeUpdater

    def update_updater(self):
        self.updater.update_DB = False
        self.updater.update_CC = False

    def test_update_DB(self):
        self.no_DB_update_test()

    def test_update_CC(self):
        self.no_CC_update_test()


class TestSetName(BaseUpdaterMethodTest):
    def setup_test(self):
        self.mock_product_range = Mock()
        self.mock_CCAPI.get_range.return_value = self.mock_product_range
        self.original_name = self.product_range.name
        self.new_name = "New Product Range Name"
        self.updater.set_name(self.new_name)

    def update_DB_test(self):
        self.assertEqual(self.new_name, self.product_range.name)

    def no_DB_update_test(self):
        self.assertEqual(self.original_name, self.product_range.name)

    def update_CC_test(self):
        self.mock_CCAPI.get_range.assert_called_once_with(self.product_range.range_ID)
        self.mock_product_range.set_name.assert_called_once_with(self.new_name)
        self.mock_CCAPI.set_product_name.assert_called_once_with(
            name=self.new_name, product_ids=self.product_IDs
        )
        self.assertEqual(3, len(self.mock_CCAPI.mock_calls))

    def no_CC_update_test(self):
        self.assertEqual(0, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetName(RangeUpdaterTest, TestSetName):
    pass


class TestPartialRangeUpdaterSetName(PartialRangeUpdaterTest, TestSetName):
    pass


class TestNoUpdateRangeUpdaterSetName(NoChangeRangeUpdaterTest, TestSetName):
    pass


class TestSetDeparment(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_department = self.product_range.department
        self.new_department = models.Department.objects.create(
            name="New Department", product_option_value_ID="385093"
        )
        self.updater.set_department(self.new_department)

    def update_DB_test(self):
        self.assertEqual(self.new_department, self.product_range.department)

    def no_DB_update_test(self):
        self.assertEqual(self.original_department, self.product_range.department)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=self.product_IDs,
            option_id=models.Department.PRODUCT_OPTION_ID,
            option_value_id=self.new_department.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetDeparment(RangeUpdaterTest, TestSetDeparment):
    pass


class TestPartialRangeUpdaterSetDeparment(PartialRangeUpdaterTest, TestSetDeparment):
    pass


class TestNoUpdateRangeUpdaterSetDepartment(NoChangeRangeUpdaterTest, TestSetDeparment):
    pass


class TestSetDescription(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_description = self.product_range.description
        self.new_description = "A description\nOf a product."
        self.updater.set_description(self.new_description)

    def update_DB_test(self):
        self.assertEqual(self.new_description, self.product_range.description)

    def no_DB_update_test(self):
        self.assertEqual(self.original_description, self.product_range.description)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_description.assert_called_once_with(
            product_ids=self.product_IDs, description=self.new_description
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetDescription(RangeUpdaterTest, TestSetDescription):
    pass


class TestPartialRangeUpdaterSetDescription(
    PartialRangeUpdaterTest, TestSetDescription
):
    pass


class TestNoUpdateRangeUpdaterSetDescription(
    NoChangeRangeUpdaterTest, TestSetDescription
):
    pass


class TestSetSearchTerms(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_search_terms = self.product_range.amazon_search_terms
        self.new_search_terms = ["Mug", "Cup", "Drink Container"]
        self.search_tem_text = "|".join(self.new_search_terms)
        self.product_option_value_ID = "284938"
        self.mock_CCAPI.get_option_value_id.return_value = self.product_option_value_ID
        self.updater.set_amazon_search_terms(self.new_search_terms)

    def update_DB_test(self):
        self.assertEqual(self.search_tem_text, self.product_range.amazon_search_terms)

    def no_DB_update_test(self):
        self.assertEqual(
            self.original_search_terms, self.product_range.amazon_search_terms
        )

    def update_CC_test(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            self.updater.AMAZON_SEARCH_TERMS_OPTION_ID,
            value=self.search_tem_text,
            create=True,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=self.product_IDs,
            option_id=self.updater.AMAZON_SEARCH_TERMS_OPTION_ID,
            option_value_id=self.product_option_value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetSearchTerms(RangeUpdaterTest, TestSetSearchTerms):
    pass


class TestPartialRangeUpdaterSetSearchTerms(
    PartialRangeUpdaterTest, TestSetSearchTerms
):
    pass


class TestNoUpdateRangeUpdaterSetSearchTerms(
    NoChangeRangeUpdaterTest, TestSetSearchTerms
):
    pass


class TestSetBullets(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_bullet_points = self.product_range.amazon_bullet_points
        self.new_bullet_points = ["Mug", "Cup", "Drink Container"]
        self.bulllet_points_text = "|".join(self.new_bullet_points)
        self.product_option_value_ID = "9465161"
        self.mock_CCAPI.get_option_value_id.return_value = self.product_option_value_ID
        self.updater.set_amazon_bullet_points(self.new_bullet_points)

    def update_DB_test(self):
        self.assertEqual(
            self.bulllet_points_text, self.product_range.amazon_bullet_points
        )

    def no_DB_update_test(self):
        self.assertEqual(
            self.original_bullet_points, self.product_range.amazon_bullet_points
        )

    def update_CC_test(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            self.updater.AMAZON_BULLET_POINTS_OPTION_ID,
            value=self.bulllet_points_text,
            create=True,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=self.product_IDs,
            option_id=self.updater.AMAZON_BULLET_POINTS_OPTION_ID,
            option_value_id=self.product_option_value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetBullets(RangeUpdaterTest, TestSetBullets):
    pass


class TestPartialRangeUpdaterSetBullets(PartialRangeUpdaterTest, TestSetBullets):
    pass


class TestNoUpdateRangeUpdaterSetBullets(NoChangeRangeUpdaterTest, TestSetBullets):
    pass


class TestSetEndOfLine(BaseUpdaterMethodTest):
    def setup_test(self):
        self.mock_product_range = Mock()
        self.mock_CCAPI.get_range.return_value = self.mock_product_range
        self.original_value = self.product_range.end_of_line
        self.new_value = not self.original_value
        self.updater.set_end_of_line(self.new_value)

    def update_DB_test(self):
        self.assertEqual(self.new_value, self.product_range.end_of_line)

    def no_DB_update_test(self):
        self.assertEqual(self.original_value, self.product_range.end_of_line)

    def update_CC_test(self):
        self.mock_CCAPI.get_range.assert_called_once_with(self.product_range.range_ID)
        self.mock_product_range.set_end_of_line.assert_called_once_with(self.new_value)
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetEndOfLine(RangeUpdaterTest, TestSetEndOfLine):
    pass


class TestPartialRangeUpdaterSetEndOfLine(PartialRangeUpdaterTest, TestSetEndOfLine):
    pass


class TestNoUpdateRangeUpdaterSetEndOfLine(NoChangeRangeUpdaterTest, TestSetEndOfLine):
    pass


class TestSetAddVariationOption(BaseUpdaterMethodTest):
    def setup_test(self):
        self.product_option = models.ProductOption.objects.create(
            name="Shape", product_option_ID="299438"
        )
        self.updater.add_variation_product_option(self.product_option)
        self.queryset = self.updater.product_range_selected_option_model.objects.filter(
            product_range=self.product_range, product_option=self.product_option
        )

    def update_DB_test(self):
        self.assertEqual(self.queryset.count(), 1)
        self.assertTrue(self.queryset.all()[0].variation)

    def no_DB_update_test(self):
        self.assertFalse(self.queryset.exists())

    def update_CC_test(self):
        self.mock_CCAPI.add_option_to_product.assert_called_once_with(
            range_id=self.product_range.range_ID,
            option_id=self.product_option.product_option_ID,
        )
        self.mock_CCAPI.set_range_option_drop_down.assert_called_once_with(
            range_id=self.product_range.range_ID,
            option_id=self.product_option.product_option_ID,
            drop_down=True,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterAddVariationOption(RangeUpdaterTest, TestSetAddVariationOption):
    pass


class TestPartialRangeUpdaterAddVariationOption(
    PartialRangeUpdaterTest, TestSetAddVariationOption
):
    pass


class TestNoUpdateRangeUpdaterAddVariationOption(
    NoChangeRangeUpdaterTest, TestSetAddVariationOption
):
    pass


class TestAddVariationOptionUpdatesListingOption(BaseUpdaterMethodTest):
    def setup_test(self):
        self.product_option = models.ProductOption.objects.create(
            name="Design", product_option_ID="3840382"
        )
        self.updater.product_range_selected_option_model.objects.create(
            product_range=self.product_range,
            product_option=self.product_option,
            variation=False,
        )
        self.updater.add_variation_product_option(self.product_option)
        self.selected_option = self.updater.product_range_selected_option_model.objects.get(
            product_range=self.product_range, product_option=self.product_option
        )

    def update_DB_test(self):
        self.assertTrue(self.selected_option.variation)

    def no_DB_update_test(self):
        self.assertFalse(self.selected_option.variation)

    def update_CC_test(self):
        self.mock_CCAPI.add_option_to_product.assert_called_once_with(
            range_id=self.product_range.range_ID,
            option_id=self.product_option.product_option_ID,
        )
        self.mock_CCAPI.set_range_option_drop_down.assert_called_once_with(
            range_id=self.product_range.range_ID,
            option_id=self.product_option.product_option_ID,
            drop_down=True,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterAddVariationOptionUpdatesListingOption(
    RangeUpdaterTest, TestAddVariationOptionUpdatesListingOption
):
    pass


class TestPartialRangeUpdaterAddVariationOptionUpdatesListingOption(
    PartialRangeUpdaterTest, TestAddVariationOptionUpdatesListingOption
):
    pass


class TestNoUpdateRangeUpdaterAddVariationOptionUpdatesListingOption(
    NoChangeRangeUpdaterTest, TestAddVariationOptionUpdatesListingOption
):
    pass


class TestAddListingOption(BaseUpdaterMethodTest):
    def setup_test(self):
        self.product_option = models.ProductOption.objects.create(
            name="Shape", product_option_ID="299438"
        )
        self.updater.add_listing_product_option(self.product_option)
        self.queryset = self.updater.product_range_selected_option_model.objects.filter(
            product_range=self.product_range, product_option=self.product_option
        )

    def update_DB_test(self):
        self.assertEqual(self.queryset.count(), 1)
        self.assertFalse(self.queryset.all()[0].variation)

    def no_DB_update_test(self):
        self.assertFalse(self.queryset.exists())

    def update_CC_test(self):
        self.mock_CCAPI.add_option_to_product.assert_called_once_with(
            range_id=self.product_range.range_ID,
            option_id=self.product_option.product_option_ID,
        )
        self.mock_CCAPI.set_range_option_drop_down.assert_called_once_with(
            range_id=self.product_range.range_ID,
            option_id=self.product_option.product_option_ID,
            drop_down=False,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterAddListingOption(RangeUpdaterTest, TestAddListingOption):
    pass


class TestPartialRangeUpdaterAddListingOption(
    PartialRangeUpdaterTest, TestAddListingOption
):
    pass


class TestNoUpdateRangeUpdaterAddListingOption(
    NoChangeRangeUpdaterTest, TestAddListingOption
):
    pass


class TestAddListingOptionUpdatesVariationOption(BaseUpdaterMethodTest):
    def setup_test(self):
        self.product_option = self.size_product_option
        self.updater.add_listing_product_option(self.product_option)
        self.selected_option = self.updater.product_range_selected_option_model.objects.get(
            product_range=self.product_range, product_option=self.product_option
        )

    def update_DB_test(self):
        self.assertFalse(self.selected_option.variation)

    def no_DB_update_test(self):
        self.assertTrue(self.selected_option.variation)

    def update_CC_test(self):
        self.mock_CCAPI.add_option_to_product.assert_called_once_with(
            range_id=self.product_range.range_ID,
            option_id=self.product_option.product_option_ID,
        )
        self.mock_CCAPI.set_range_option_drop_down.assert_called_once_with(
            range_id=self.product_range.range_ID,
            option_id=self.product_option.product_option_ID,
            drop_down=False,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterAddListingOptionUpdatesVariationOption(
    RangeUpdaterTest, TestAddListingOptionUpdatesVariationOption
):
    pass


class TestPartialRangeUpdaterAddListingOptionUpdatesVariationOption(
    PartialRangeUpdaterTest, TestAddListingOptionUpdatesVariationOption
):
    pass


class TestNoUpdateRangeUpdaterAddListingOptionUpdatesVariationOption(
    NoChangeRangeUpdaterTest, TestAddListingOptionUpdatesVariationOption
):
    pass


class TestRemoveProductOption(BaseUpdaterMethodTest):
    def setup_test(self):
        self.mock_CCAPI.get_range.return_value = Mock()
        self.product_option = self.colour_product_option
        self.updater.remove_product_option(self.product_option)

    def update_DB_test(self):
        self.assertFalse(
            self.updater.product_option_value_link_model.objects.filter(
                product__product_ID__in=self.product_IDs,
                product_option_value__product_option=self.product_option,
            ).exists()
        )
        self.assertFalse(
            self.updater.product_range_selected_option_model.objects.filter(
                product_range=self.product_range, product_option=self.product_option
            ).exists()
        )

    def no_DB_update_test(self):
        self.assertTrue(
            self.updater.product_option_value_link_model.objects.filter(
                product__product_ID__in=self.product_IDs,
                product_option_value__product_option=self.product_option,
            ).exists()
        )
        self.assertTrue(
            self.updater.product_range_selected_option_model.objects.filter(
                product_range=self.product_range, product_option=self.product_option
            ).exists()
        )

    def update_CC_test(self):
        self.mock_CCAPI.remove_option_from_product.assert_called_once_with(
            range_id=self.product_range.range_ID,
            option_id=self.product_option.product_option_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterTestRemoveProductOption(
    RangeUpdaterTest, TestRemoveProductOption
):
    pass


class TestPartialRangeUpdaterTestRemoveProductOption(
    PartialRangeUpdaterTest, TestRemoveProductOption
):
    pass


class TestNoUpdateRangeUpdaterTestRemoveProductOption(
    NoChangeRangeUpdaterTest, TestRemoveProductOption
):
    pass
