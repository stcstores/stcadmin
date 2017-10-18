from . cloud_commerce_country_id import CloudCommerceCountryID  # NOQA
from . destination_zone_model import DestinationZone  # NOQA
from . spring_manifest_model import SpringManifest  # NOQA
from . spring_order_model import SpringOrder  # NOQA

from ccapi import CCAPI

COURIER_RULES = {
    SpringOrder.PARCEL: (SpringManifest.TRACKED, None),
    SpringOrder.TRACKED: (SpringManifest.TRACKED, None),
    SpringOrder.PACKET: (SpringManifest.UNTRACKED, 11747),
}


def get_manifest(manifest_type):
    try:
        manifest = SpringManifest.unfiled.get(manifest_type=manifest_type)
    except SpringManifest.DoesNotExist:
        manifest = SpringManifest(manifest_type=manifest_type)
        manifest.save()
    except SpringManifest.MultipleObjectsReturned as e:
        raise e
    return manifest


def get_orders(courier_rule_id):
    return CCAPI.get_orders_for_dispatch(
        order_type=1, number_of_days=1, courier_rule_id=courier_rule_id)


def update_spring_orders():
    for service, manifest in COURIER_RULES.items():
        manifest_type, rule_id = manifest
        if rule_id is None:
            continue
        manifest = get_manifest(manifest_type)
        orders = get_orders(rule_id)
        for order in orders:
            order_id = str(order.order_id)
            if not SpringOrder.objects.filter(order_id=order_id).exists():
                SpringOrder.objects.create_from_order(
                    order, service=service, manifest=manifest)
