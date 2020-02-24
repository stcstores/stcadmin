"""Mocks for CCAPI objects."""
import random


def get_id():
    return random.randint(100000, 999999)


def attach_property(instance, prop_name, propr):
    class_name = instance.__class__.__name__ + "Child"
    child_class = type(class_name, (instance.__class__,), {prop_name: propr})

    instance.__class__ = child_class


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
        name=None,
        products=None,
        end_of_line=False,
        range_id=None,
        options=None,
    ):
        self.id = id or get_id()
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
        name=None,
        full_name=None,
        options=None,
        stock_level=5,
        locations=None,
    ):
        self.id = id or get_id()
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
        options = options or [MockProductOption()]
        self.options = {option.option_name: option for option in options}

    def __getitem__(self, key):
        return self.options[key]

    def __setitem__(self, key, value):
        self.options[key] = value


class MockCCProductsProduct:
    def __init__(
        self,
        id=None,
        name=None,
        full_name=None,
        product_range=None,
        stock_level=5,
        vat_rate=None,
        retail_price=24.95,
        price=12.50,
        purcahse_price=5.75,
        bays=None,
        width=50,
        length=150,
        height=335,
        weight=100,
        package_type=None,
        supplier=None,
        supplier_sku=None,
        department=None,
        options=None,
        amazon_bullets=None,
        amazon_search_terms=None,
    ):
        self.id = id or get_id()
        self.name = name or "Mock Product"
        self.full_name = full_name or "Mock Product - Red - Green"
        self.product_range = product_range or MockCCProductsProductRange()
        self.range_id = self.product_range.id
        self.stock_level = stock_level
        self.vat_rate = vat_rate or 5
        self.price = price
        self.bays = bays or [get_id()]
        self.width = width
        self.length = length
        self.height = height
        self.weight = weight
        self.purchase_price = purcahse_price
        self.retail_price = retail_price
        self.package_type = package_type or "Large Letter"
        self.supplier = supplier or MockCCProductsSupplier()
        self.supplier_sku = supplier_sku or "TY84938"
        self.department = department or "Sports"
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
