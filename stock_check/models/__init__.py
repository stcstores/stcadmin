"""Models for the Stock Check app."""

from .stock_check import StockCheckProduct, ProductBay  # NOQA
from inventory.models import Bay, Warehouse  # NOQA
from ccapi import CCAPI
import cc_products
import sys


API_ATTEMPTS = 500


def get_cc_product_by_sku(sku):
    """Return Cloud Commerce product with SKU sku."""
    search_result = search_cc_products(sku)
    if len(search_result) != 1:
        raise Exception("Wrong number of products found for SKU {}".format(sku))
    return get_cc_product(search_result[0].variation_id)


def search_cc_products(sku):
    """Return search results for SKU."""
    for i in range(API_ATTEMPTS):
        try:
            return CCAPI.search_products(sku)
        except Exception:
            pass


def get_cc_product(product_id):
    """Return Cloud Commerce product."""
    for i in range(API_ATTEMPTS):
        try:
            return cc_products.get_product(product_id)
        except Exception:
            pass


def update_products(inventory_table):
    """
    Update Product database.

    Add new products and delete any no longer in the inventory export.
    """
    print("Updating Products...", file=sys.stderr)
    table_skus = [sku for sku in inventory_table.get_column("VAR_SKU") if sku]
    db_skus = [p.sku for p in StockCheckProduct.objects.all()]
    new_skus = [sku for sku in table_skus if sku not in db_skus]
    missing_skus = [sku for sku in db_skus if sku not in table_skus]
    for sku in missing_skus:
        StockCheckProduct.objects.filter(sku__in=missing_skus).delete()
    print(f"Deleted {len(missing_skus)} products.", file=sys.stderr)
    new_products = []
    for sku in new_skus:
        cc_product = get_cc_product_by_sku(sku)
        new_product = StockCheckProduct(
            range_id=cc_product.range_id, product_id=cc_product.id, sku=cc_product.sku
        )
        new_products.append(new_product)
    StockCheckProduct.objects.bulk_create(new_products)
    print(f"Added {len(new_products)} products", file=sys.stderr)


def update_product_bays(inventory_table):
    """
    Update Warehouse model.

    Add new Warehouses and delete any that no longer exist.
    """
    print("Updating product bay mapping...", file=sys.stderr)
    ProductBay.objects.all().delete()
    product_bays = []
    for row in inventory_table:
        if row["VAR_Bays"] is None or len(row["VAR_Bays"]) == 0:
            continue
        product = StockCheckProduct.objects.get(sku=row["VAR_SKU"])
        bay_names = list(set(row["VAR_Bays"].split(";")))
        try:
            bays = [Bay.objects.get(name=name) for name in bay_names]
        except Bay.DoesNotExist:
            raise Exception("Bay not found: {}".format(", ".join(bay_names)))
        for bay in bays:
            product_bays.append(ProductBay(product=product, bay=bay))
    ProductBay.objects.bulk_create(product_bays)
    print(
        f"Created {ProductBay.objects.all().count()} product bay links.",
        file=sys.stderr,
    )


def update_stock_check(inventory_table):
    """Update Stock Check models from a Cloud Commerce inventory export."""
    update_products(inventory_table)
    update_product_bays(inventory_table)
