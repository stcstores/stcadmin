"""Page classes containing information about form pages."""
from .productbase import ProductEditorBase


class Page(ProductEditorBase):
    """Base class for product editor form pages."""

    def __init__(self, manager):
        """Set page properties."""
        self.manager = manager

    def __repr__(self):
        return self.name

    @property
    def data(self):
        """Return data stored in the session for this page."""
        data = self.manager.product_data.get(
            self.identifier, None)
        return data

    @data.setter
    def data(self, data):
        """Store data in the session for this page."""
        self.manager.product_data[self.identifier] = data
        self.manager.session.modified = True

    def data_exists(self, page_identifier=None):
        """Return True if data exists for the indicated page."""
        if page_identifier is None:
            page_identifier = self.identifer
        if page_identifier in self.manager.product_data:
            if len(self.manager.product_data[page_identifier]) > 1:
                return True
        return False

    @property
    def url(self):
        """Return URL identifer for this page."""
        return 'product_editor:{}'.format(self.identifier)

    def visible(self):
        """Return True if page is currently visible in navigation."""
        return True

    def enabled(self):
        """Return True if page is available in navigation."""
        return True


class BasicInfo(Page):
    """Page for product attributes that stay the same between variations."""

    name = 'Basic Info'
    identifier = ProductEditorBase.BASIC


class ProductInfo(Page):
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
            if self.data_exists(self.UNUSED_VARIATIONS):
                return False
        return True


class ListingOptions(Page):
    """Page to set Product Options for listings for single items."""

    name = 'Listing Options'
    identifier = ProductEditorBase.LISTING_OPTIONS

    def enabled(self):
        """Return True if page is available in navigation."""
        if self.data_exists(self.BASIC):
            return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.SINGLE:
            return True
        return False


class VariationOptions(Page):
    """Page to select variations for new variation products."""

    name = 'Variation Options'
    identifier = ProductEditorBase.VARIATION_OPTIONS

    def enabled(self):
        """Return True if page is available in navigation."""
        if self.data_exists(self.BASIC):
            return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.VARIATION:
            return True
        return False


class UnusedVariations(Page):
    """Page to mark non existant variations as unused."""

    name = 'Unused Variations'
    identifier = ProductEditorBase.UNUSED_VARIATIONS

    def enabled(self):
        """Return True if page is available in navigation."""
        if self.data_exists(self.PRODUCT_INFO):
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
        if self.data_exists(self.VARIATION_OPTIONS):
            return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.VARIATION:
            return True
        return False


class VariationListingOptions(Page):
    """Page to set listing Product Options for variations."""

    name = 'Variation Listing Options'
    identifier = ProductEditorBase.VARIATION_LISTING_OPTIONS

    def enabled(self):
        """Return True if page is available in navigation."""
        if self.data_exists(self.UNUSED_VARIATIONS):
            return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.VARIATION:
            return True
        return False


class Finish(Page):
    """Final page to create the new product or edit the existing product."""

    name = 'Finish'
    identifier = ProductEditorBase.FINISH

    def enabled(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type == self.VARIATION:
            if self.data_exists(self.VARIATION_INFO):
                return True
        if self.manager.product_type == self.SINGLE:
            if self.data_exists(self.PRODUCT_INFO):
                return True
        return False

    def visible(self):
        """Return True if page is currently visible in navigation."""
        if self.manager.product_type is not None:
            return True
        return False
