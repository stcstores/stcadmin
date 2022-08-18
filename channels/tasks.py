"""Tasks for the channels app."""

from celery import shared_task

from channels import models


@shared_task
def create_shopify_product(listing_pk, update_pk):
    """Create a new listing on Shopify from a ShopifyListing instance.

    Args:
        listing_pk (int): ID of the listing instance.
        update_pk (int): ID of the ShopifyUpdate record for this action.
    """
    listing = models.shopify_models.ShopifyListing.objects.get(pk=listing_pk)
    update = models.shopify_models.ShopifyUpdate.objects.get(pk=update_pk)
    try:
        models.shopify_models.ShopifyListingManager.create_listing(listing)
    except Exception:
        update.set_error()
        raise
    else:
        update.set_complete()
