"""Models for manifests."""

from .cloud_commerce_country_id import CloudCommerceCountryID  # NOQA
from .cloud_commerce_shipping_rule import CloudCommerceShippingRule  # NOQA
from .destination_zone_model import DestinationZone  # NOQA
from .secured_mail_destination_model import SecuredMailDestination  # NOQA
from .manifest_model import Manifest  # NOQA
from .manifest_order_model import ManifestOrder  # NOQA
from .manifest_package_model import ManifestPackage  # NOQA
from .manifest_item_model import ManifestItem  # NOQA
from .service_models import ManifestService, SecuredMailService  # NOQA
from .counter_model import Counter  # NOQA
from .manifest_type_model import ManifestType  # NOQA
from django.db import transaction
from ccapi import CCAPI


def get_manifest(manifest_type):
    """Return current manifest matching manfiest_type."""
    try:
        manifest = Manifest.unfiled.get(
            status=Manifest.UNFILED, manifest_type=manifest_type)
    except Manifest.DoesNotExist:
        manifest = Manifest(
            manifest_type=manifest_type, status=Manifest.UNFILED)
        manifest.save()
    except Manifest.MultipleObjectsReturned as e:
        raise e
    return manifest


def get_manifest_by_service(service):
    """Return current manifest for service."""
    return get_manifest(service.manifest_type)


def get_manifest_for_order(order):
    """Return the correct current manifest for order."""
    return get_manifest_by_service(order.service)


def get_orders(courier_rule_id, number_of_days=1):
    """Return current orders matching courier_rule_id."""
    return CCAPI.get_orders_for_dispatch(
        order_type=1,
        number_of_days=number_of_days,
        courier_rule_id=courier_rule_id)


def create_order(cc_order, service):
    """Add Cloud Commerce Order to database."""
    order = ManifestOrder._base_manager.create(
        order_id=str(cc_order.order_id),
        customer_name=cc_order.delivery_name,
        date_recieved=cc_order.date_recieved,
        dispatch_date=cc_order.dispatch_date,
        country=CloudCommerceCountryID._base_manager.get(
            cc_id=cc_order.delivery_country_code),
        manifest=get_manifest_by_service(service),
        service=service)
    package = ManifestPackage._base_manager.create(order=order)
    for product in cc_order.products:
        ManifestItem._base_manager.create(
            package=package,
            item_id=product.product_id,
            quantity=product.quantity)


@transaction.atomic
def update_spring_orders(number_of_days=1):
    """Update database with new orders."""
    for service in ManifestService.enabled_services.all():
        for shipping_rule in service.shipping_rules.all():
            orders = get_orders(
                shipping_rule.rule_id, number_of_days=number_of_days)
            for order in orders:
                order_id = str(order.order_id)
                if not ManifestOrder.objects.filter(
                        order_id=order_id).exists():
                    create_order(order, service=service)
