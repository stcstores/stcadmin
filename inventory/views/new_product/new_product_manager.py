import json

import cc_products


class NewProductBase:
    VARIATION = 'variation'
    SINGLE = 'single'
    NEW_PRODUCT = 'new_product_data'
    BASIC = 'basic_info'
    TYPE = 'type'
    VARIATION_OPTIONS = 'variation_options'
    UNUSED_VARIATIONS = 'unused_variations'
    LISTING_OPTIONS = 'listing_options'
    VARIATION_INFO = 'variation_info'
    VARIATION_LISTING_OPTIONS = 'variation_listing_options'
    FINISH = 'finish'


class Page:
    def __init__(self, name, identifier, manager, url=None):
        self.name = name
        self.identifier = identifier
        if url is None:
            self.url = 'inventory:new_product_{}'.format(self.identifier)
        else:
            self.url = 'inventory:{}'.format(url)
        self.manager = manager

    @property
    def data(self):
        data = self.manager.session[self.manager.NEW_PRODUCT].get(
            self.identifier, None)
        return data

    @data.setter
    def data(self, data):
        self.manager.session[self.manager.NEW_PRODUCT][self.identifier] = data
        self.manager.session.modified = True


class NewProductManager(NewProductBase):
    """Access new product data stored in session."""

    def __init__(self, request):
        self.request = request
        self.session = request.session
        if self.NEW_PRODUCT not in self.session:
            self.session[self.NEW_PRODUCT] = {}
        self.session.modified = True
        self.basic_info = Page('Basic Info', self.BASIC, self)
        self.listing_options = Page(
            'Listing Options', self.LISTING_OPTIONS, self)
        self.variation_options = Page(
            'Variation Options', self.VARIATION_OPTIONS, self)
        self.unused_variations = Page(
            'Unused Variations', self.UNUSED_VARIATIONS, self)
        self.variation_info = Page('Variation Info', self.VARIATION_INFO, self)
        self.variation_listing_options = Page(
            'Variation Listing Options', self.VARIATION_LISTING_OPTIONS, self)
        self.finish = Page('Finish', self.FINISH, self)
        self.data = self.session.get(self.NEW_PRODUCT, None)
        self.pages = (
            self.basic_info, self.listing_options, self.variation_options,
            self.variation_info, self.variation_listing_options, self.finish)
        self.single_product_pages = (
            self.basic_info, self.listing_options, self.finish)
        self.variation_product_pages = (
            self.basic_info, self.variation_options, self.unused_variations,
            self.variation_info, self.variation_listing_options, self.finish)
        if self.product_type == self.VARIATION:
            self.current_pages = self.variation_product_pages
        elif self.product_type == self.SINGLE:
            self.current_pages = self.single_product_pages
        else:
            self.current_pages = (self.basic_info, )

    @property
    def product_type(self):
        product_data = self.session.get(self.NEW_PRODUCT, None)
        if product_data is not None:
            return product_data.get(self.TYPE, None)
        else:
            return None

    @product_type.setter
    def product_type(self, product_type):
        product_data = self.session.get(self.NEW_PRODUCT, None)
        product_data[self.TYPE] = product_type
        self.session.modified = True

    def delete_product(self):
        self.session[self.NEW_PRODUCT] = {}

    def save_json(self, outfile):
        data = self.product_data
        return json.dump(data, outfile, indent=4, sort_keys=True)

    @property
    def product_data(self):
        return self.session[self.NEW_PRODUCT]

    @staticmethod
    def create_product(product_data):
        return NewProduct(product_data)


class NewProduct(NewProductBase):

    def __new__(self, product_data):
        self.product_data = product_data
        title = self.product_data[self.BASIC]['title']
        self.product_range = cc_products.create_range(title)
        if self.product_data[self.TYPE] == self.SINGLE:
            self.create_single_product(self.product_range)
        elif self.product_data[self.TYPE] == self.VARIATION:
            self.create_variation_product(self.product_range)
