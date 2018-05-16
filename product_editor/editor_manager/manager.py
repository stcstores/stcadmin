"""
ProductManager subclasses.

Product Managers are used to manage session stored product information and
page progression for Product Creator forms.
"""

import json

from django.shortcuts import redirect

from .page import EditProductPage, NewProductPage
from .productbase import ProductEditorBase
from .productcreator import ProductCreator
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
        self.basic_info = self.page_class('Basic Info', self.BASIC, self)
        self.product_info = self.page_class(
            'Product Info', self.PRODUCT_INFO, self)
        self.listing_options = self.page_class(
            'Listing Options', self.LISTING_OPTIONS, self)
        self.variation_options = self.page_class(
            'Variation Options', self.VARIATION_OPTIONS, self)
        self.unused_variations = self.page_class(
            'Unused Variations', self.UNUSED_VARIATIONS, self)
        self.variation_info = self.page_class(
            'Variation Info', self.VARIATION_INFO, self)
        self.variation_listing_options = self.page_class(
            'Variation Listing Options', self.VARIATION_LISTING_OPTIONS, self)
        self.finish = self.page_class('Finish', self.FINISH, self)

    @property
    def product_data(self):
        """Return all new product data."""
        return self.session[self.SESSION_KEY]

    @property
    def current_pages(self):
        """Return pages relevent to current product."""
        if self.product_type == self.VARIATION:
            if self.unused_variations.data:
                return [
                    page for page in self.variation_product_pages
                    if page != self.product_info]
            return self.variation_product_pages
        elif self.product_type == self.SINGLE:
            return self.single_product_pages
        else:
            return (self.basic_info, self.product_info)

    @property
    def page_names(self):
        """Return dict of pages by page name."""
        return {page.name: page for page in self.current_pages}

    @property
    def page_identifiers(self):
        """Return dict of pages by page name."""
        return {page.identifier: page for page in self.current_pages}

    @property
    def pages(self):
        """Return all pages for this manager."""
        return [
            self.basic_info, self.product_info, self.listing_options,
            self.variation_options, self.variation_info,
            self.variation_listing_options, self.finish]

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
        if page == self.basic_info:
            if 'variations' in post_data:
                self.product_type = self.VARIATION
            elif 'single' in post_data:
                self.product_type = self.SINGLE
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


class NewProductManager(BaseProductManager):
    """Product manager for creating new products."""

    page_class = NewProductPage
    SESSION_KEY = 'new_product'

    def get_data_from_session(self):
        """Retrive data from session."""
        if self.SESSION_KEY not in self.session:
            self.session[self.SESSION_KEY] = {}
        self.session.modified = True
        self.data = self.session.get(self.SESSION_KEY, None)

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
            {k: v for k, v in d.items() if k != 'used'}
            for d in self.unused_variations.data if d['used']]
        return combinations

    def delete_product(self):
        """Clear all new product data from session."""
        self.session[self.SESSION_KEY] = {}

    def create_product(self):
        """Create new Cloud Commerce Product from data in session."""
        return ProductCreator(self.product_data)


class EditProductManager(BaseProductManager):
    """Product Manager for editing existing products."""

    page_class = EditProductPage
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
            self.load_product_data()  # TEMP

    def load_product_data(self):
        """Replace data in session with current product data."""
        self.session[self.SESSION_KEY] = ProductLoader(self.range_id)

    @property
    def product_type(self):
        """Return the type of the product, Single or Variation."""
        return self.SINGLE  # TEMP
