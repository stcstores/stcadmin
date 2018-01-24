from . stock_check import Warehouse, Bay, Product, ProductBay  # NOQA
from ccapi import CCAPI


def get_cc_product_by_sku(sku):
    search_result = CCAPI.search_products(sku)
    if len(search_result) != 1:
        raise Exception(
            'Wrong number of products found for SKU {}'.format(sku))
    return CCAPI.get_product(search_result[0].variation_id)


def update_products(inventory_table):
    print('Updating Products...')
    skus = [sku for sku in inventory_table.get_column('VAR_SKU') if sku]
    db_skus = [p.sku for p in Product.objects.all()]
    new_skus = [sku for sku in skus if sku not in db_skus]
    old_skus = [sku for sku in db_skus if sku not in skus]
    for sku in old_skus:
        try:
            Product.objects.get(sku__in=old_skus).delete()
        except Product.MultipleObjectsReturned:
            raise Exception('Multiple products found with SKU {}.'.format(sku))
    print('Deleted {} products.'.format(len(old_skus)))
    new_products = []
    for sku in new_skus:
        cc_product = get_cc_product_by_sku(sku)
        new_product = Product(
            range_id=cc_product.range_id, product_id=cc_product.id,
            sku=cc_product.sku)
        new_products.append(new_product)
    Product.objects.bulk_create(new_products)
    print('Added {} products'.format(len(new_products)))


def update_product_bays(inventory_table):
    print('Updating product bay mapping...')
    locations = {}
    for row in inventory_table:
        sku = row['VAR_SKU']
        bays = row['VAR_Bays'].strip()
        if bays:
            locations[sku] = bays.split(';')
        else:
            locations[sku] = []
    for product in Product.objects.all():
        bay_names = locations[product.sku]
        bays = []
        for bay_name in bay_names:
            try:
                bay = Bay.objects.get(name=bay_name)
            except Bay.DoesNotExist:
                raise Exception('Cannot find bay "{}"'.format(bay_name))
            else:
                bays.append(bay)
        product_bays = product.bays.all()
        for bay in product_bays:
            if bay not in bays:
                ProductBay._base_manager.filter(
                    product=product, bay=bay).delete()
        for bay in bays:
            if bay not in product_bays:
                ProductBay._base_manager.get_or_create(
                    product=product, bay=bay)


def update_locations():
    print('Updating warehouses...')
    warehouses_created = 0
    bays_created = 0
    warehouses_deleted = 0
    bays_deleted = 0
    warehouses = CCAPI.get_warehouses()
    warehouse_ids = [int(w.id) for w in warehouses]
    bay_ids = []
    for warehouse in warehouses:
        bay_ids += [int(bay.id) for bay in warehouse]
        w, created = Warehouse.objects.get_or_create(
            warehouse_id=warehouse.id,
            defaults={'name': warehouse.name})
        if created:
            warehouses_created += 1
        else:
            w.name = warehouse.name
            w.save()
        for bay in warehouse:
            b, created = Bay.objects.get_or_create(
                bay_id=bay.id,
                defaults={'name': bay.name, 'warehouse': w})
            if created:
                bays_created += 1
            else:
                b.name = bay.name
                b.warehouse = w
                b.save()
    warehouses_to_delete = Warehouse.objects.exclude(
        warehouse_id__in=warehouse_ids)
    warehouses_deleted += warehouses_to_delete.count()
    warehouses_to_delete.delete()
    for bay in Bay.objects.all():
        if bay.bay_id not in bay_ids:
            bays_deleted += 1
            bay.delete()
    print('Warehouses Created: {}'.format(warehouses_created))
    print('Bays Created: {}'.format(bays_created))
    print('Warehouses Deleted: {}'.format(warehouses_deleted))
    print('Bays deleted: {}'.format(bays_deleted))


def update_stock_check(inventory_table):
    update_locations()
    update_products(inventory_table)
    update_product_bays(inventory_table)
