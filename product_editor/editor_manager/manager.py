"""
ProductManager subclasses.

Product Managers are used to manage session stored product information and
page progression for Product Creator forms.
"""

import json

from django.shortcuts import redirect, reverse

from . import form_pages
from .productbase import ProductEditorBase
from .productcreator import ProductCreator, ProductEditor
from .productloader import ProductLoader


class BaseProductManager(ProductEditorBase):
    """
    Base class for Product Managers.

    Product Managers are used to manage session stored product information and
    page progression for Product Creator forms.
    """

    def __init__(self, request):
        """Set object properties."""
        self.request = request
        self.session = self.request.session
        self.get_data_from_session()
        self.set_pages()

    def set_pages(self):
        """Create pages."""
        raise NotImplementedError()

    def clear_session(self):
        """Clear all new product data from session."""
        self.session[self.SESSION_KEY] = {}

    @property
    def product_data(self):
        """Return all new product data."""
        return self.session[self.SESSION_KEY]

    @property
    def current_pages(self):
        """Return pages relevent to current product."""
        return [page for page in self.pages if page.visible()]

    @property
    def page_names(self):
        """Return dict of pages by page name."""
        return {page.name: page for page in self.pages}

    @property
    def page_identifiers(self):
        """Return dict of pages by page name."""
        return {page.identifier: page for page in self.pages}

    @property
    def pages(self):
        """Return all pages for this manager."""
        return [
            self.basic_info, self.product_info, self.listing_options,
            self.variation_options, self.unused_variations,
            self.variation_info, self.variation_listing_options, self.finish]

    @property
    def single_product_pages(self):
        """Return pages used for single products."""
        return [
            self.basic_info, self.product_info, self.listing_options,
            self.finish]

    @property
    def variation_product_pages(self):
        """Return pages used for variation products."""
        return [
            self.basic_info, self.product_info, self.variation_options,
            self.unused_variations, self.variation_info,
            self.variation_listing_options, self.finish]

    @property
    def landing_page(self):
        """Return URL of the first page to be displaid."""
        raise NotImplementedError()

    @property
    def product_type(self):
        """Return the type of the product, Single or Variation."""
        product_data = self.session.get(self.SESSION_KEY, None)
        if product_data is not None:
            return product_data.get(self.TYPE, None)
        else:
            return None

    @product_type.setter
    def product_type(self, product_type):
        product_data = self.session.get(self.SESSION_KEY, None)
        product_data[self.TYPE] = product_type
        self.session.modified = True

    @property
    def variations(self):
        """Return variation combinations for product."""
        combinations = [
            {k: v for k, v in d.items() if k not in
                (self.USED, self.PRODUCT_ID)}
            for d in self.unused_variations.data if d[self.USED]]
        return combinations

    def get_page(self, page_identifier):
        """Return page by identifier."""
        return self.page_identifiers[page_identifier]

    def get_url(self, page_identifier):
        """Return URL identifier for page by identifier."""
        try:
            return self.get_page(page_identifier).url
        except KeyError:
            print('Page not found: "{}"'.format(page_identifier))
            return self.current_pages[0].url

    def get_redirect(self, page, post_data):
        """Return HTTP redirect for the appropriate page."""
        if 'goto' in post_data and post_data['goto']:
            return redirect(self.get_url(self.request.POST['goto']))
        page_index = self.current_pages.index(page)
        if 'back' in post_data:
            return redirect(self.current_pages[page_index - 1].url)
        return redirect(self.current_pages[page_index + 1].url)

    def redirect_start(self):
        """Return HTTP Redirect to the first page of the forms."""
        return redirect(self.pages[0].url)

    def save_json(self, outfile):
        """Output new product data as JSON to outfile."""
        data = self.product_data
        return json.dump(data, outfile, indent=4, sort_keys=True)

    def save_product(self):
        """Complete product creation or editing."""
        raise NotImplementedError()


class NewProductManager(BaseProductManager):
    """Product manager for creating new products."""

    SESSION_KEY = 'new_product'

    def get_data_from_session(self):
        """Retrive data from session."""
        if self.SESSION_KEY not in self.session:
            self.session[self.SESSION_KEY] = {}
        self.session.modified = True
        self.data = self.session.get(self.SESSION_KEY, None)

    def set_pages(self):
        """Create pages."""
        self.basic_info = form_pages.NewBasicInfo(self)
        self.product_info = form_pages.NewProductInfo(self)
        self.listing_options = form_pages.NewListingOptions(self)
        self.variation_options = form_pages.NewVariationOptions(self)
        self.unused_variations = form_pages.NewUnusedVariations(self)
        self.variation_info = form_pages.NewVariationInfo(self)
        self.variation_listing_options = form_pages.NewVariationListingOptions(
            self)
        self.clear_product = form_pages.ClearNewProduct(self)
        self.finish = form_pages.NewFinish(self)

    def get_redirect(self, page, post_data):
        """Return HTTP redirect for the appropriate page."""
        if page == self.basic_info:
            if 'variations' in post_data:
                self.product_type = self.VARIATION
            elif 'single' in post_data:
                self.product_type = self.SINGLE
        return super().get_redirect(page, post_data)

    @classmethod
    def landing_page(cls):
        """Return URL of the first page to be displaid."""
        return reverse('product_editor:{}'.format(cls.BASIC))

    def save_product(self):
        """Save new product."""
        return ProductCreator(self.product_data)


class EditProductManager(BaseProductManager):
    """Product Manager for editing existing products."""

    SESSION_KEY = 'edit_product'

    def __init__(self, request, range_id):
        """Get Range ID for product range being edited."""
        self.range_id = range_id
        super().__init__(request)

    def get_data_from_session(self):
        """Retrive data from session."""
        if self.SESSION_KEY not in self.session:
            self.session[self.SESSION_KEY] = {}
        self.session.modified = True
        self.data = self.session.get(self.SESSION_KEY, None)
        if not self.data or not self.range_id == self.data.get(self.RANGE_ID):
            self.load_product_data()
        else:
            return
            self.load_product_data()  # TEMP

    def set_pages(self):
        """Create pages."""
        self.basic_info = form_pages.EditBasicInfo(self)
        self.product_info = form_pages.EditProductInfo(self)
        self.listing_options = form_pages.EditListingOptions(self)
        self.variation_options = form_pages.EditVariationOptions(self)
        self.unused_variations = form_pages.EditUnusedVariations(self)
        self.variation_info = form_pages.EditVariationInfo(self)
        self.variation_listing_options = (
            form_pages.EditVariationListingOptions(self))
        self.clear_product = form_pages.ClearEditedProduct(self)
        self.finish = form_pages.EditFinish(self)

    def load_product_data(self):
        """Replace data in session with current product data."""
        self.session[self.SESSION_KEY] = ProductLoader(self.range_id)

    @classmethod
    def landing_page(cls, range_id):
        """Return URL of the first page to be displaid."""
        return reverse('product_editor:{}'.format(
            cls.BASIC), kwargs={'range_id': range_id})

    def save_product(self):
        """Update product."""
        data = self.product_data
        self.clear_session()
        return ProductEditor(data)
