"""ITD Shipment creator."""
import csv
import io


class ITDShipmentFile:
    """ITD Shipment file generator."""

    LAST_NAME = "Recipient Last Name"
    ADDRESS_1 = "Ship to Address 1"
    ADDRESS_2 = "Ship to Address 2"
    ADDRESS_3 = "Ship to Address 3"
    CITY = "Ship to City"
    STATE = "Ship to State"
    COUNTRY = "Ship to Country"
    POSTCODE = "Ship to Zip/Postcode"
    ORDER_NUMBER = "Order Number"
    PACKAGE_NUMBER = "Package Number"
    LENGTH = "Package Length"
    WIDTH = "Package Width"
    HEIGHT = "Package Height"
    DESCRIPTION = "Package Item Description"
    SKU = "Package Item SKU"
    WEIGHT = "Package Item Weight"
    VALUE = "Package Item Value"
    QUANTITY = "Package Item Quantity"
    COUNTRY_OF_ORIGIN = "Package Item Country of Origin"
    HR_CODE = "Package Item Harmonisation Code"
    SHIPMENT_METHOD = "Order Shipment Method"

    HEADER = [
        LAST_NAME,
        ADDRESS_1,
        ADDRESS_2,
        ADDRESS_3,
        CITY,
        STATE,
        COUNTRY,
        POSTCODE,
        ORDER_NUMBER,
        PACKAGE_NUMBER,
        LENGTH,
        WIDTH,
        HEIGHT,
        DESCRIPTION,
        SKU,
        WEIGHT,
        VALUE,
        QUANTITY,
        COUNTRY_OF_ORIGIN,
        HR_CODE,
        SHIPMENT_METHOD,
    ]

    @classmethod
    def _create_rows(cls, shipment_export):
        rows = []
        for order in shipment_export.shipment_order.all():
            for package in order.shipment_package.all():
                for item in package.shipment_item.all():
                    row_data = cls._create_row_data(
                        shipment_order=order, package=package, item=item
                    )
                    row = [row_data[header] for header in cls.HEADER]
                    rows.append(row)
        return rows

    @classmethod
    def _create_row_data(cls, shipment_order, package, item):
        row_data = {
            cls.LAST_NAME: shipment_order.destination.recipient_name,
            cls.ADDRESS_1: shipment_order.destination.address_line_1,
            cls.ADDRESS_2: shipment_order.destination.address_line_2,
            cls.ADDRESS_3: shipment_order.destination.address_line_3,
            cls.CITY: shipment_order.destination.city,
            cls.STATE: shipment_order.destination.state,
            cls.COUNTRY: shipment_order.destination.country,
            cls.POSTCODE: shipment_order.destination.postcode,
            cls.ORDER_NUMBER: shipment_order.order_number(),
            cls.PACKAGE_NUMBER: package.package_number(),
            cls.LENGTH: package.length_cm,
            cls.WIDTH: package.width_cm,
            cls.HEIGHT: package.height_cm,
            cls.DESCRIPTION: item.description,
            cls.SKU: item.sku,
            cls.WEIGHT: item.weight_kg,
            cls.VALUE: str(float(item.value / 100)).format("{:2f}"),
            cls.QUANTITY: item.quantity,
            cls.COUNTRY_OF_ORIGIN: item.country_of_origin,
            cls.HR_CODE: item.hr_code,
            cls.SHIPMENT_METHOD: shipment_order.shipment_method.identifier,
        }
        return row_data

    @classmethod
    def create(cls, shipment_export):
        """Generate a shipment file for the orders associated with an export."""
        rows = cls._create_rows(shipment_export)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(cls.HEADER)
        for row in rows:
            writer.writerow(row)
        return output.getvalue()
