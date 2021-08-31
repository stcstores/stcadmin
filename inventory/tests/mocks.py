"""Mocks for CCAPI objects."""
import random
from string import ascii_uppercase


def get_id():
    return random.randint(100000, 999999)


def get_sku():
    def get_block():
        return "".join([random.choice(ascii_uppercase) for i in range(3)])

    return "_".join([get_block() for _ in range(3)])


class MockCCAPIProductRangeOptions:
    def __init__(self, options=None):
        self.options = options or [MockProductOption()]

    def __iter__(self):
        for option in self.options:
            yield option


class MockCCAPIProductRange:
    def __init__(
        self,
        id=None,
        sku=None,
        name=None,
        products=None,
        end_of_line=False,
        range_id=None,
        options=None,
    ):
        self.id = id or get_id()
        self.sku = sku or get_sku()
        self.name = name or "Mock Product Range"
        self.range_id = range_id or get_id()
        self.products = products or [MockCCAPIProduct()]
        self.end_of_line = end_of_line
        self.options = options or MockCCAPIProductRangeOptions()


class MockCCAPIProductProductOption:
    def __init__(self, option_name=None, value=None):
        self.option_name = option_name or "Mock Product Option"
        self.value = value or MockProductOptionValue()


class MockCCPAPIProductLocation:
    def __init__(self, name="Bay 1"):
        self.name = name


class MockCCAPIProduct:
    def __init__(
        self,
        id=None,
        sku=None,
        name=None,
        full_name=None,
        options=None,
        stock_level=5,
        locations=None,
    ):
        self.id = id or get_id()
        self.sku = sku or get_sku()
        self.name = name or "Mock Product"
        self.full_name = full_name or "Mock Product - Red"
        self.options = options or [MockCCAPIProductProductOption()]
        self.stock_level = stock_level
        self.locations = locations or [MockCCPAPIProductLocation()]

    def get_images(self):
        return []


class MockProductOption:
    def __init__(self, id=None, option_name=None, values=None, is_web_shop_select=True):
        self.id = id or get_id()
        self.option_name = option_name or "Mock Product Option"
        self.values = values or [MockProductOptionValue(option_name=self.option_name)]
        self.is_web_shop_select = is_web_shop_select

    def __iter__(self):
        for value in self.values:
            yield value


class MockProductOptions:
    def __init__(self, options=None):
        self.options = options or [MockProductOption()]
        self.option_lookup = {option.option_name: option for option in self.options}

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.options[key]
        return self.option_lookup[key]

    def __iter_(self):
        for option in self.options:
            yield option


class MockProductOptionValue:
    def __init__(self, id=None, value=None, option_name=None):
        self.id = id or get_id()
        self.value = value or "Mock Product Option Value"
        self.option_name = option_name or "Mock Product Option"


class MockCCProductsRangeOptions:
    def __init__(self, selected_options=None):
        self.selected_options = selected_options or []


class MockCCProductsRangeSelectedOption:
    def __init__(self, id=None, name=None):
        self.id = id or get_id()
        self.name = name or "Mock Selected Option"


class MockCCProductsProductRange:
    def __init__(
        self,
        id=None,
        name=None,
        products=None,
        end_of_line=False,
        options=None,
        department=None,
        description=None,
    ):
        self.id = id or get_id()
        self.name = name or "Mock Product Range"
        self.products = products or [MockCCProductsProduct(product_range=self)]
        self.end_of_line = end_of_line
        self.options = options or MockCCProductsRangeOptions()
        self.department = department or self.products[0].department
        self.description = description or "Mock Product Range\nA good thing."


class MockCCProductsSupplier:
    def __init__(self, factory_name="Reseller Inc"):
        self.factory_name = factory_name


class MockCCProductProductOptions:
    def __init__(self, options=None):
        options = options or [MockProductOptionValue()]
        self.options = {option.option_name: option for option in options}

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.options.values())[key]
        return self.options[key]

    def __setitem__(self, key, value):
        self.options[key] = value

    def __iter__(self):
        for option in list(self.options.values()):
            yield option.option_name, option.value


class MockCCProductsProduct:
    def __init__(
        self,
        id=None,
        name="Mock Product",
        full_name="Mock Product - Red - Green",
        product_range=None,
        barcode="153487314813",
        brand="Test Brand",
        manufacturer="Test Manufacturer",
        stock_level=5,
        vat_rate=5,
        retail_price=24.95,
        price=12.50,
        purcahse_price=5.75,
        bays=None,
        width=50,
        length=150,
        height=335,
        weight=100,
        package_type="Large Letter",
        supplier=None,
        supplier_sku="TY84938",
        department="Sports",
        options=None,
        amazon_bullets=None,
        amazon_search_terms=None,
        gender="mens",
        hs_code="28490389",
    ):
        self.id = id or get_id()
        self.name = name
        self.full_name = full_name
        self.product_range = product_range or MockCCProductsProductRange()
        self.range_id = self.product_range.id
        self.barcode = barcode
        self.brand = brand
        self.manufacturer = manufacturer
        self.stock_level = stock_level
        self.vat_rate = vat_rate
        self.price = price
        self.bays = bays or [get_id()]
        self.width = width
        self.length = length
        self.height = height
        self.weight = weight
        self.purchase_price = purcahse_price
        self.retail_price = retail_price
        self.package_type = package_type
        self.supplier = supplier or MockCCProductsSupplier()
        self.supplier_sku = supplier_sku
        self.department = department
        self.hs_code = hs_code
        self.options = (
            MockCCProductProductOptions(options) or MockCCProductProductOptions()
        )
        self.amazon_bullets = amazon_bullets or [
            "Green",
            "Large",
            "Round",
            "Heavy",
            "Good Clearence",
        ]
        self.amazon_search_terms = amazon_search_terms or [
            "Red",
            "Square",
            "Light",
            "Well rounded",
        ]
        self.gender = gender
