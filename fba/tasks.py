"""Tasks for the fba app."""

from celery import shared_task

from fba import models


@shared_task
def file_parcelhub_shipment(filing_pk):
    """
    File a Parcelhub shipment.

    Args:
        shipment_order_pk (int): ID of the shipment to file.
    """
    filing = models.ParcelhubShipmentFiling.objects.get(pk=filing_pk)
    try:
        shipment = models.ParcelhubShipment.objects.create_shipment(
            filing.shipment_order
        )
    except Exception as e:
        filing.set_error(str(e))
        raise
    else:
        filing.set_complete(shipment)
