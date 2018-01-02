from . barcodes import Barcode, get_barcode  # NOQA
from . stcadmin_image import STCAdminImage, get_product_image_upload_to  # NOQA
from . stock_check import Warehouse, Bay, Product  # NOQA
from ccapi import CCAPI


def update_locations():
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
