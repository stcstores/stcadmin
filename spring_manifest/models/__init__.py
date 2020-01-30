"""Models for manifests."""

import logging

from ccapi import CCAPI
from django.db import transaction

from .cloud_commerce_country_id import CloudCommerceCountryID  # NOQA
from .cloud_commerce_shipping_rule import CloudCommerceShippingRule  # NOQA
from .counter_model import Counter  # NOQA
from .manifest_item_model import ManifestItem  # NOQA
from .manifest_model import Manifest, ManifestUpdate  # NOQA
from .manifest_order_model import ManifestOrder  # NOQA
from .manifest_package_model import ManifestPackage  # NOQA
from .manifest_type_model import ManifestType  # NOQA
from .secured_mail_destination_model import SecuredMailDestination  # NOQA
from .service_models import ManifestService, SecuredMailService  # NOQA

logger = logging.getLogger("file_manifest")


def get_manifest(manifest_type):
    """Return current manifest matching manfiest_type."""
    try:
        manifest = Manifest.unfiled.get(
            closed=False,
            status__in=(Manifest.UNFILED, Manifest.CLOSING),
            manifest_type=manifest_type,
        )
    except Manifest.DoesNotExist:
        manifest = Manifest.objects.create(
            manifest_type=manifest_type, closed=False, status=Manifest.UNFILED
        )
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
        order_type=1, number_of_days=number_of_days, courier_rule_id=courier_rule_id
    )


def close_manifest(manifest):
    """Close manifest if not already closed."""
    if manifest.closed is False:
        manifest.status = Manifest.CLOSING
        manifest.save()
        update_manifest_orders()
        manifest.closed = True
        manifest.status = Manifest.UNFILED
        manifest.save()


def create_order(cc_order, service):
    """Add Cloud Commerce Order to database."""
    order = ManifestOrder._base_manager.create(
        order_id=str(cc_order.order_id),
        customer_name=cc_order.delivery_name,
        date_recieved=cc_order.date_recieved,
        dispatch_date=cc_order.dispatch_date,
        country=CloudCommerceCountryID._base_manager.get(
            cc_id=cc_order.delivery_country_code
        ),
        manifest=get_manifest_by_service(service),
        service=service,
    )
    package = ManifestPackage._base_manager.create(order=order)
    for product in cc_order.products:
        ManifestItem._base_manager.create(
            package=package,
            name=product.product_name,
            full_name=product.product_full_name,
            item_id=product.product_id,
            quantity=product.quantity,
            weight=int(product.per_item_weight),
        )


def get_manifest_update():
    """Return the most recent manifest update."""
    return ManifestUpdate.objects.order_by("-started")[0]


def update_manifest_orders(number_of_days=1):
    """Update database with new orders."""
    update, created = ManifestUpdate.objects.get_or_create(
        status=ManifestUpdate.IN_PROGRESS
    )
    update_already_in_progress = not created
    if not update_already_in_progress:
        try:
            update_manifest_database(number_of_days)
        except Exception as e:
            logger.exception(f"Manifest update raised an exception.")
            update.fail()
            raise e
        else:
            update.complete()
    else:
        logger.info("Manifest update already in progress.")


@transaction.atomic
def update_manifest_database(number_of_days):
    """Download new orders and update the database."""
    for service in ManifestService.enabled_services.all():
        for shipping_rule in service.shipping_rules.all():
            orders = get_orders(shipping_rule.rule_id, number_of_days=number_of_days)
            for order in orders:
                order_id = str(order.order_id)
                if not ManifestOrder.objects.filter(order_id=order_id).exists():
                    create_order(order, service=service)
