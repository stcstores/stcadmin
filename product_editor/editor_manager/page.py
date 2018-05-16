"""Page classes containing information about form pages."""


class BasePage:
    """Base class for product editor form pages."""

    def __init__(self, name, identifier, manager, url=None):
        """Set page properties."""
        self.name = name
        self.identifier = identifier
        self.url = self.get_url(url)
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

    def get_url(self, url):
        """Return URL identifier for page."""
        if url is None:
            return 'product_editor:{}'.format(self.identifier)
        else:
            return 'product_editor:{}'.format(url)


class NewProductPage(BasePage):
    """Container for pages used for creating new products."""

    pass


class EditProductPage(BasePage):
    """Container for pages used for editing existing products."""

    pass
