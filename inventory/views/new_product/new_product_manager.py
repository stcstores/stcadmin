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


class NewProductManager:
    """Access new product data stored in session."""

    VARIATION = 'variation'
    SINGLE = 'single'
    NEW_PRODUCT = 'new_product_data'
    BASIC = 'basic_info'
    TYPE = 'type'
    VARIATION_OPTIONS = 'variation_options'
    LISTING_OPTIONS = 'listing_options'
    VARIATION_DATA = 'variations'
    VARIATION_LISTING_OPTIONS = 'variation_listing_options'

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
        self.variation_info = Page('Variation Info', self.VARIATION_DATA, self)
        self.variation_listing_options = Page(
            'Variation Listing Options', self.VARIATION_LISTING_OPTIONS, self)
        self.data = self.session.get(self.NEW_PRODUCT, None)
        self.pages = (
            self.basic_info, self.listing_options, self.variation_options,
            self.variation_info, self.variation_listing_options)
        self.single_product_pages = (self.basic_info, self.listing_options)
        self.variation_product_pages = (
            self.basic_info, self.variation_options, self.variation_info,
            self.variation_listing_options)
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
