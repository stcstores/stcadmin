"""UPS Shipment creator."""

import csv
import io


class UPSShipmentFile:
    """UPS Shipment file generator."""

    ORDER_NUMBER = "OrderNumber"
    PACKAGE_NUMBER = "PackageNumber"
    PACKAGE_LENGTH = "Package Length"
    PACKAGE_WIDTH = "Package Width"
    PACKAGE_HEIGHT = "Package Height"
    PACKAGE_ITEM_DESCRIPTION = "PackageItemDescription"
    PACKAGE_ITEM_SKU = "PackageItemSKU"
    PACKAGE_ITEM_WEIGHT = "Package Item Weight"
    PACKAGE_ITEM_VALUE = "PackageItemValue"
    PACKAGE_ITEM_QUANTITY = "PackageItemQuantity"
    PACKAGE_ITEM_COUNTRY_ORIGIN = "PackageItemCountryOrigin"
    PACKAGE_ITEM_HARMONISATION_CODE = "PackageItemHarmonisationCode"
    ORDER_SHIPMENT_METHOD = "Order Shipment Method"
    PACKAGE_UNIT_OF_MEASURE = "PackageUnitOfMeasure"

    HEADER = [
        ORDER_NUMBER,
        PACKAGE_NUMBER,
        PACKAGE_LENGTH,
        PACKAGE_WIDTH,
        PACKAGE_HEIGHT,
        PACKAGE_ITEM_DESCRIPTION,
        PACKAGE_ITEM_SKU,
        PACKAGE_ITEM_WEIGHT,
        PACKAGE_ITEM_VALUE,
        PACKAGE_ITEM_QUANTITY,
        PACKAGE_ITEM_COUNTRY_ORIGIN,
        PACKAGE_ITEM_HARMONISATION_CODE,
        ORDER_SHIPMENT_METHOD,
        PACKAGE_UNIT_OF_MEASURE,
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
        rows.append(cls._get_total_row(shipment_export))
        return rows

    @classmethod
    def _get_total_row(cls, shipment_export):
        total_weight = cls._calculate_total_weight(shipment_export)
        formatted_value = round(total_weight, 3)
        new_row = [None for _ in cls.HEADER]
        new_row[cls.HEADER.index(cls.PACKAGE_ITEM_WEIGHT)] = formatted_value
        return new_row

    @classmethod
    def _calculate_total_weight(cls, shipment_export):
        values = [order.weight_kg for order in shipment_export.shipment_order.all()]
        return sum(values)

    @classmethod
    def _create_row_data(cls, shipment_order, package, item):
        row_data = {
            cls.ORDER_NUMBER: shipment_order.order_number,
            cls.PACKAGE_NUMBER: package.package_number,
            cls.PACKAGE_LENGTH: package.length_cm,
            cls.PACKAGE_WIDTH: package.width_cm,
            cls.PACKAGE_HEIGHT: package.height_cm,
            cls.PACKAGE_ITEM_DESCRIPTION: item.description.replace("'", ""),
            cls.PACKAGE_ITEM_SKU: item.sku,
            cls.PACKAGE_ITEM_WEIGHT: item.weight_kg,
            cls.PACKAGE_ITEM_VALUE: str(float(item.value / 100)).format("{:2f}"),
            cls.PACKAGE_ITEM_QUANTITY: item.quantity,
            cls.PACKAGE_ITEM_COUNTRY_ORIGIN: item.country_of_origin,
            cls.PACKAGE_ITEM_HARMONISATION_CODE: item.hr_code,
            cls.ORDER_SHIPMENT_METHOD: "UPSES",
            cls.PACKAGE_UNIT_OF_MEASURE: "EACH",
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
