from . cloud_commerce_country_id import CloudCommerceCountryID  # NOQA
from . destination_zone_model import DestinationZone  # NOQA
from . spring_manifest_model import SpringManifest  # NOQA
from . spring_order_model import SpringOrder  # NOQA
from . spring_package_model import SpringPackage  # NOQA
from . spring_item_model import SpringItem  # NOQA
from stcadmin.settings import SPRING_COURIER_RULES  # NOQA
from django.db import transaction

from ccapi import CCAPI


def get_manifest(manifest_type):
    try:
        manifest = SpringManifest.unfiled.get(
            status=SpringManifest.UNFILED, manifest_type=manifest_type)
    except SpringManifest.DoesNotExist:
        manifest = SpringManifest(
            manifest_type=manifest_type, status=SpringManifest.UNFILED)
        manifest.save()
    except SpringManifest.MultipleObjectsReturned as e:
        raise e
    return manifest


def get_manifest_by_service(service):
    manifest_type = SpringOrder.MANIFEST_SELECTION[service]
    return get_manifest(manifest_type)


def get_manifest_for_order(order):
    return get_manifest_by_service(order.service)


def get_orders(courier_rule_id, number_of_days=1):
    return CCAPI.get_orders_for_dispatch(
        order_type=1, number_of_days=number_of_days,
        courier_rule_id=courier_rule_id)


def create_order(cc_order, service):
    order = SpringOrder._base_manager.create(
        order_id=str(cc_order.order_id),
        customer_name=cc_order.delivery_name,
        date_recieved=cc_order.date_recieved,
        dispatch_date=cc_order.dispatch_date,
        country=CloudCommerceCountryID._base_manager.get(
            cc_id=cc_order.delivery_country_code),
        manifest=get_manifest_by_service(service),
        service=service)
    package = SpringPackage._base_manager.create(order=order)
    for product in cc_order.products:
        SpringItem._base_manager.create(
            package=package, item_id=product.product_id,
            quantity=product.quantity)


@transaction.atomic
def update_spring_orders(number_of_days=1):
    for service, rule_ids in SPRING_COURIER_RULES.items():
        print(service)
        if not (rule_ids):
            continue
        for rule_id in rule_ids:
            orders = get_orders(rule_id, number_of_days=number_of_days)
            for order in orders:
                order_id = str(order.order_id)
                if not SpringOrder.objects.filter(order_id=order_id).exists():
                    create_order(order, service=service)
