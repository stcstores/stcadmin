"""Page classes containing information about form pages."""
from django.urls import reverse

from .productbase import ProductEditorBase


class PageData:
    """Descriptor for page data."""

    def __get__(self, instance, owner):
        return instance.manager.product_data.get(instance.identifier, None)

    def __set__(self, instance, value):
        instance.manager.product_data[instance.identifier] = value
        instance.manager.session.modified = True


class Page(ProductEditorBase):
    """Base class for product editor form pages."""

    def __init__(self, manager):
        """Set page properties."""
        self.manager = manager

    def __repr__(self):
        return self.name

    data = PageData()

    @property
    def data_exists(self):
        """Return True if data exists for this page, else False."""
        if len(self.data) > 1:
            return True
        return False

    def data_exists_for_page(self, page_identifier):
        """Return True if data exists for the indicated page."""
        if page_identifier in self.manager.product_data:
            return self.manager.get_page(page_identifier).data_exists

    @property
    def url(self):
        """Return URL identifier for this page."""
        raise NotImplementedError()

    def visible(self):
        """Return True if page is currently visible in navigation."""
        return True

    def enabled(self):
        """Return True if page is available in navigation."""
        return True


class NewProductPage(Page):
    """Page class for the new product forms."""

    @property
    def url(self):
        """Return URL identifier for this page."""
        return reverse('product_editor:{}'.format(self.identifier))


class EditProductPage(Page):
    """Page class for the edit product forms."""

    @property
    def url(self):
        """Return URL identifier for this page."""
        return reverse(
            'product_editor:{}'.format(self.identifier),
            kwargs={'range_id': self.manager.range_id})


class BasicInfo:
    """Page for product attributes that stay the same between variations."""

    name = 'Basic Info'
    identifier = ProductEditorBase.BASIC


class ProductInfo:
    """Page for product attributes that vary between variations."""

    name = 'Product Info'
    identifier = ProductEditorBase.PRODUCT_INFO

    def enabled(self):
        """Return True if page is available in navigation."""
        if self.manager.product_type is not None:
            return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.VARIATION:
            if self.data_exists_for_page(self.UNUSED_VARIATIONS):
                return False
        return True


class ListingOptions:
    """Page to set Product Options for listings for single items."""

    name = 'Listing Options'
    identifier = ProductEditorBase.LISTING_OPTIONS

    def enabled(self):
        """Return True if page is available in navigation."""
        if self.data_exists_for_page(self.BASIC):
            return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.SINGLE:
            return True
        return False


class VariationOptions:
    """Page to select variations for new variation products."""

    name = 'Variation Options'
    identifier = ProductEditorBase.VARIATION_OPTIONS

    def enabled(self):
        """Return True if page is available in navigation."""
        if self.data_exists_for_page(self.BASIC):
            return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.VARIATION:
            return True
        return False

    @property
    def data_exists(self):
        """Return True if data exists for this page, else False."""
        if len(self.data) > 0:
            return True
        return False


class UnusedVariations:
    """Page to mark non existant variations as unused."""

    name = 'Unused Variations'
    identifier = ProductEditorBase.UNUSED_VARIATIONS

    def enabled(self):
        """Return True if page is available in navigation."""
        if self.data_exists_for_page(self.PRODUCT_INFO):
            return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.VARIATION:
            return True
        return False


class VariationInfo(Page):
    """Page to set required information for variation."""

    name = 'Variation Info'
    identifier = ProductEditorBase.VARIATION_INFO

    def enabled(self):
        """Return True if page is available in navigation."""
        if self.data_exists_for_page(self.VARIATION_OPTIONS):
            return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.VARIATION:
            return True
        return False


class VariationListingOptions:
    """Page to set listing Product Options for variations."""

    name = 'Variation Listing Options'
    identifier = ProductEditorBase.VARIATION_LISTING_OPTIONS

    def enabled(self):
        """Return True if page is available in navigation."""
        if self.data_exists_for_page(self.UNUSED_VARIATIONS):
            return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.VARIATION:
            return True
        return False


class Finish:
    """Final page to create the new product or edit the existing product."""

    name = 'Finish'
    identifier = ProductEditorBase.FINISH

    def enabled(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.VARIATION:
            if self.data_exists_for_page(self.VARIATION_INFO):
                return True
        if self.manager.product_type == self.SINGLE:
            if self.data_exists_for_page(self.PRODUCT_INFO):
                return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type is not None:
            return True
        return False


class ClearProduct(Page):
    """Clear session data."""

    identifier = ProductEditorBase.CLEAR_PRODUCT

    def visible(self):
        """Return True if page is currently visible in navigation."""
        return False

    def enabled(self):
        """Return True if page is available in navigation."""
        return False


class NewBasicInfo(BasicInfo, NewProductPage):
    """Page for product attributes that stay the same between variations."""

    pass


class EditBasicInfo(BasicInfo, EditProductPage):
    """Page for product attributes that stay the same between variations."""

    pass


class NewProductInfo(ProductInfo, NewProductPage):
    """Page for product attributes that vary between variations."""

    pass


class EditProductInfo(ProductInfo, EditProductPage):
    """Page for product attributes that vary between variations."""

    pass


class NewListingOptions(ListingOptions, NewProductPage):
    """Page to set Product Options for listings for single items."""

    pass


class EditListingOptions(ListingOptions, EditProductPage):
    """Page to set Product Options for listings for single items."""

    pass


class NewVariationOptions(VariationOptions, NewProductPage):
    """Page to select variations for new variation products."""

    pass


class EditVariationOptions(VariationOptions, EditProductPage):
    """Page to select variations for new variation products."""

    class PageDataWithExistingData(PageData):
        """Retain existing variation data when updating."""

        def __set__(self, instance, data):
            existing_data = instance.manager.product_data[
                instance.EXISTING_VARIATIONS]
            for option, value_list in existing_data.items():
                for value in value_list:
                    if value not in data[option]:
                        data[option].insert(0, value)
            super().__set__(instance, data)

    data = PageDataWithExistingData()


class NewUnusedVariations(UnusedVariations, NewProductPage):
    """Page to mark non existant variations as unused."""

    pass


class EditUnusedVariations(UnusedVariations, EditProductPage):
    """Page to mark non existant variations as unused."""

    pass


class NewVariationInfo(VariationInfo, NewProductPage):
    """Page to set required information for variation."""

    pass


class EditVariationInfo(VariationInfo, EditProductPage):
    """Page to set required information for variation."""

    pass


class NewVariationListingOptions(VariationListingOptions, NewProductPage):
    """Page to set listing Product Options for variations."""

    pass


class EditVariationListingOptions(VariationListingOptions, EditProductPage):
    """Page to set listing Product Options for variations."""

    pass


class NewFinish(Finish, NewProductPage):
    """Create new product."""

    pass


class EditFinish(Finish, EditProductPage):
    """Update edited product."""

    pass


class ClearNewProduct(ClearProduct, NewProductPage):
    """Clear new product data from session."""

    name = 'Clear New Product'
    warning_text = '\\n'.join([
        'This will delete the current prduct and start a new one.',
        'Any progress on the current product will be lost.',
        'Is this what you want to do?'])


class ClearEditedProduct(ClearProduct, EditProductPage):
    """Clear new product data from session."""

    name = 'Clear Changes'
    warning_text = '\\n'.join([
        'This will delete any current changes.',
        'Is this what you want to do?'])
