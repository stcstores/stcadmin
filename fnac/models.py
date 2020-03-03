"""Models for the fnac app."""

from django.db import models

from inventory.models import ProductExport


class Category(models.Model):
    """Model for FNAC categories."""

    name = models.CharField(max_length=255)
    english = models.TextField(unique=True)
    french = models.TextField(unique=True)

    def __str__(self):
        return self.name or self.english


class Size(models.Model):
    """Model for FNAC sizes."""

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class FnacRange(models.Model):
    """Model for FNAC product ranges."""

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return f"{self.sku} - {self.name}"


class FnacProduct(models.Model):
    """Model for FNAC products."""

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255, unique=True)
    fnac_range = models.ForeignKey(FnacRange, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=15)
    description = models.TextField()
    price = models.PositiveIntegerField(blank=True, null=True)
    brand = models.CharField(max_length=255)
    colour = models.CharField(max_length=255, blank=True, null=True)
    english_size = models.CharField(max_length=255, blank=True, null=True)
    french_size = models.ForeignKey(
        Size, on_delete=models.PROTECT, blank=True, null=True
    )
    stock_level = models.IntegerField()
    image_1 = models.CharField(max_length=20, blank=True)
    image_2 = models.CharField(max_length=20, blank=True)
    image_3 = models.CharField(max_length=20, blank=True)
    image_4 = models.CharField(max_length=20, blank=True)
    do_not_create = models.BooleanField(default=False)
    created = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @classmethod
    def out_of_stock(cls):
        """Return a queryset of out of stock products."""
        return cls.objects.filter(stock_level=0)

    @classmethod
    def in_stock(cls):
        """Return a quyerset of in stock products."""
        return cls.objects.filter(stock_level__gt=0)


class Translation(models.Model):
    """Model for FNAC product name, description and colour translations."""

    product = models.OneToOneField(FnacProduct, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    colour = models.CharField(max_length=255)

    def __repr__(self):
        return f"<Translations for {self.product}>"


def update_inventory(inventory_file=None):
    """Update FnacRange and FnacProduct from an inventory export."""
    _InventoryUpdate(inventory_file=inventory_file)


class _InventoryUpdate:
    RANGE_SKU_COLUMN = "RNG_SKU"
    RANGE_NAME_COLUMN = "RNG_Name"
    SKU_COLUMN = "VAR_SKU"
    NAME_COLUMN = "VAR_Name"
    BARCODE_COLUMN = "VAR_Barcode"
    DESCRIPTION_COLUMN = "VAR_Description"
    COLOUR_COLUMN = "OPT_Colour_DRD"
    BRAND_COLUMN = "OPT_Brand"
    SIZE_COLUMN = "OPT_Size_DRD"
    STOCK_COLUMN = "VAR_Stock"
    IMAGE_COLUMN = "VAR_IMG"

    def __init__(self, inventory_file=None):
        self.updated_range_skus = []
        self.inventory_file = inventory_file or self.get_inventory_file()
        self.update_products()

    @staticmethod
    def get_inventory_file():
        return ProductExport.latest_export().as_table()

    def update_products(self):
        for row in self.inventory_file:
            fnac_range = self.create_or_update_range_from_inventory_row(row)
            self.create_or_update_product_from_inventory_row(row, fnac_range)

    def create_or_update_range_from_inventory_row(self, row):
        range_sku = row[self.RANGE_SKU_COLUMN]
        kwargs = self.get_fnac_range_kwargs(row)
        try:
            fnac_range = FnacRange.objects.get(sku=range_sku)
        except FnacRange.DoesNotExist:
            fnac_range = FnacRange(**kwargs)
            fnac_range.save()
            return fnac_range
        else:
            range_queryset = FnacRange.objects.filter(sku=range_sku)
            if range_sku not in self.updated_range_skus:
                range_queryset.update(**kwargs)
                self.updated_range_skus.append(range_sku)
            return range_queryset[0]

    def create_or_update_product_from_inventory_row(self, row, fnac_range):
        sku = row[self.SKU_COLUMN]
        kwargs = self.get_fnac_product_kwargs(row)
        kwargs["fnac_range"] = fnac_range
        try:
            product = FnacProduct.objects.get(sku=sku)
        except FnacProduct.DoesNotExist:
            product = FnacProduct(**kwargs)
            product.save()
            return product
        else:
            queryset = FnacProduct.objects.filter(sku=sku)
            queryset.update(**kwargs)
            return queryset[0]

    def get_fnac_range_kwargs(self, row):
        return {"name": row[self.RANGE_NAME_COLUMN], "sku": row[self.RANGE_SKU_COLUMN]}

    def get_fnac_product_kwargs(self, row):
        images = self.clean_images(row[self.IMAGE_COLUMN])
        return {
            "name": row[self.NAME_COLUMN],
            "sku": row[self.SKU_COLUMN],
            "barcode": self.clean_barcode(row[self.BARCODE_COLUMN]),
            "description": row[self.DESCRIPTION_COLUMN] or "",
            "colour": row[self.COLOUR_COLUMN],
            "brand": self.clean_brand(row[self.BRAND_COLUMN]),
            "english_size": row[self.SIZE_COLUMN],
            "stock_level": row[self.STOCK_COLUMN],
            "image_1": images[0],
            "image_2": images[1],
            "image_3": images[2],
            "image_4": images[3],
        }

    @staticmethod
    def clean_barcode(raw_barcode):
        if raw_barcode is None:
            return ""
        barcodes = raw_barcode.split(",")
        for barcode in barcodes:
            barcode = barcode.strip()
            if len(barcode) == 13:
                return barcode
            if len(barcode) == 12:
                return f"0{barcode}"
        return ""

    @staticmethod
    def clean_brand(brand):
        if not brand or brand == "Unbranded":
            return "Aucun"
        return brand

    @staticmethod
    def clean_images(image_field_contents):
        if image_field_contents:
            images = [image.strip() for image in image_field_contents.split("|")]
        else:
            images = []
        while len(images) < 4:
            images.append("")
        return images[:4]
