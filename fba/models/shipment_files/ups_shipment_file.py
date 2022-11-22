"""UPS Shipment creator."""

import csv
import io


class UPSShipmentFile:
    """UPS Shipment file generator."""

    CONTACT_NAME = "Contact Name"
    COMPANY_OR_NAME = "Company or Name"
    COUNTRY = "Country"
    ADDRESS_1 = "Address 1"
    ADDRESS_2 = "Address 2"
    ADDRESS_3 = "Address 3"
    CITY = "City"
    STATE_PROV_OTHER = "State/Prov/Other"
    POSTAL_CODE = "Postal Code"
    TELEPHONE = "Telephone"
    EXT = "Ext"
    RESIDENTIAL_IND = "Residential Ind"
    CONSIGNEE_EMAIL = "Consignee Email"
    PACKAGING_TYPE = "Packaging Type"
    CUSTOMS_VALUE = "Customs Value"
    WEIGHT = "Weight"
    LENGTH = "Length"
    WIDTH = "Width"
    HEIGHT = "Height"
    UNIT_OF_MEASURE = "Unit of Measure"
    DESCRIPTION_OF_GOODS = "Description of Goods"
    DOCUMENTS_OF_NO_COMMERCIAL_VALUE = "Documents of No Commercial Value"
    GNIFC = "GNIFC"
    PKG_DECL_VALUE = "Pkg Decl Value"
    SERVICE = "Service"
    DELIVERY_CONFIRM = "Delivery Confirm"
    SHIPPER_RELEASE = "Shipper Release"
    RET_OF_DOCUMENTS = "Ret of Documents"
    SATURDAY_DELIVER = "Saturday Deliver"
    CARBON_NEUTRAL = "Carbon Neutral"
    LARGE_PACKAGE = "Large Package"
    ADDL_HANDLING = "Addl handling"
    REFERENCE_1 = "Reference 1"
    REFERENCE_2 = "Reference 2"
    REFERENCE_3 = "Reference 3"
    QV_NOTIF_1_ADDR = "QV Notif 1-Addr"
    QV_NOTIF_1_SHIP = "QV Notif 1-Ship"
    QV_NOTIF_1_EXCP = "QV Notif 1-Excp"
    QV_NOTIF_1_DELV = "QV Notif 1-Delv"
    QV_NOTIF_2_ADDR = "QV Notif 2-Addr"
    QV_NOTIF_2_SHIP = "QV Notif 2-Ship"
    QV_NOTIF_2_EXCP = "QV Notif 2-Excp"
    QV_NOTIF_2_DELV = "QV Notif 2-Delv"
    QV_NOTIF_3_ADDR = "QV Notif 3-Addr"
    QV_NOTIF_3_SHIP = "QV Notif 3-Ship"
    QV_NOTIF_3_EXCP = "QV Notif 3-Excp"
    QV_NOTIF_3_DELV = "QV Notif 3-Delv"
    QV_NOTIF_4_ADDR = "QV Notif 4-Addr"
    QV_NOTIF_4_SHIP = "QV Notif 4-Ship"
    QV_NOTIF_4_EXCP = "QV Notif 4-Excp"
    QV_NOTIF_4_DELV = "QV Notif 4-Delv"
    QV_NOTIF_5_ADDR = "QV Notif 5-Addr"
    QV_NOTIF_5_SHIP = "QV Notif 5-Ship"
    QV_NOTIF_5_EXCP = "QV Notif 5-Excp"
    QV_NOTIF_5_DELV = "QV Notif 5-Delv"
    QV_NOTIF_MSG = "QV Notif Msg"
    QV_FAILURE_ADDR = "QV Failure Addr"
    UPS_PREMIUM_CARE = "UPS Premium Care"
    ADL_LOCATION_ID = "ADL Location ID"
    ADL_MEDIA_TYPE = "ADL Media Type"
    ADL_LANGUAGE = "ADL Language"
    ADL_NOTIFICATION_ADDR = "ADL Notification Addr"
    ADL_FAILURE_ADDR = "ADL Failure Addr"
    ADL_COD_VALUE = "ADL COD Value"
    ADL_DELIVER_TO_ADDRESSEE = "ADL Deliver to Addressee"
    ADL_SHIPPER_MEDIA_TYPE = "ADL Shipper Media Type"
    ADL_SHIPPER_LANGUAGE = "ADL Shipper Language"
    ADL_SHIPPER_NOTIFICATION_ADDR = "ADL Shipper Notification Addr"
    ADL_DIRECT_DELIVERY_ONLY = "ADL Direct Delivery Only"
    ELECTRONIC_PACKAGE_RELEASE_AUTHENTICATION = (
        "Electronic Package Release Authentication"
    )
    LITHIUM_ION_ALONE = "Lithium Ion Alone"
    LITHIUM_ION_IN_EQUIPMENT = "Lithium Ion In Equipment"
    LITHIUM_ION_WITH_EQUIPMENT = "Lithium Ion With_Equipment"
    LITHIUM_METAL_ALONE = "Lithium Metal Alone"
    LITHIUM_METAL_IN_EQUIPMENT = "Lithium Metal In Equipment"
    LITHIUM_METAL_WITH_EQUIPMENT = "Lithium Metal With Equipment"
    WEEKEND_COMMERCIAL_DELIVERY = "Weekend Commercial Delivery"

    HEADER = [
        "Contact Name",
        "Company or Name",
        "Country",
        "Address 1",
        "Address 2",
        "Address 3",
        "City",
        "State/Prov/Other",
        "Postal Code",
        "Telephone",
        "Ext",
        "Residential Ind",
        "Consignee Email",
        "Packaging Type",
        "Customs Value",
        "Weight",
        "Length",
        "Width",
        "Height",
        "Unit of Measure",
        "Description of Goods",
        "Documents of No Commercial Value",
        "GNIFC",
        "Pkg Decl Value",
        "Service",
        "Delivery Confirm",
        "Shipper Release",
        "Ret of Documents",
        "Saturday Deliver",
        "Carbon Neutral",
        "Large Package",
        "Addl handling",
        "Reference 1",
        "Reference 2",
        "Reference 3",
        "QV Notif 1-Addr",
        "QV Notif 1-Ship",
        "QV Notif 1-Excp",
        "QV Notif 1-Delv",
        "QV Notif 2-Addr",
        "QV Notif 2-Ship",
        "QV Notif 2-Excp",
        "QV Notif 2-Delv",
        "QV Notif 3-Addr",
        "QV Notif 3-Ship",
        "QV Notif 3-Excp",
        "QV Notif 3-Delv",
        "QV Notif 4-Addr",
        "QV Notif 4-Ship",
        "QV Notif 4-Excp",
        "QV Notif 4-Delv",
        "QV Notif 5-Addr",
        "QV Notif 5-Ship",
        "QV Notif 5-Excp",
        "QV Notif 5-Delv",
        "QV Notif Msg",
        "QV Failure Addr",
        "UPS Premium Care",
        "ADL Location ID",
        "ADL Media Type",
        "ADL Language",
        "ADL Notification Addr",
        "ADL Failure Addr",
        "ADL COD Value",
        "ADL Deliver to Addressee",
        "ADL Shipper Media Type",
        "ADL Shipper Language",
        "ADL Shipper Notification Addr",
        "ADL Direct Delivery Only",
        "Electronic Package Release Authentication",
        "Lithium Ion Alone",
        "Lithium Ion In Equipment",
        "Lithium Ion With_Equipment",
        "Lithium Metal Alone",
        "Lithium Metal In Equipment",
        "Lithium Metal With Equipment",
        "Weekend Commercial Delivery",
    ]

    @classmethod
    def _create_rows(cls, shipment_export):
        rows = []
        for order in shipment_export.shipment_order.all():
            for package in order.shipment_package.all():
                row_data = cls._create_row_data(shipment_order=order, package=package)
                row = [row_data.get(header) for header in cls.HEADER]
                rows.append(row)
        return rows

    @classmethod
    def _create_row_data(cls, shipment_order, package):
        row_data = {
            cls.CONTACT_NAME: shipment_order.destination.recipient_name,
            cls.COMPANY_OR_NAME: shipment_order.destination.recipient_name,
            cls.COUNTRY: shipment_order.destination.country_iso,
            cls.ADDRESS_1: shipment_order.destination.address_line_1,
            cls.ADDRESS_2: shipment_order.destination.address_line_2,
            cls.ADDRESS_3: shipment_order.destination.address_line_3,
            cls.CITY: shipment_order.destination.city,
            cls.STATE_PROV_OTHER: shipment_order.destination.state,
            cls.POSTAL_CODE: shipment_order.destination.postcode,
            cls.TELEPHONE: shipment_order.destination.contact_telephone,
            cls.PACKAGING_TYPE: "2",
            cls.WEIGHT: package.weight_kg(),
            cls.LENGTH: package.length_cm,
            cls.WIDTH: package.width_cm,
            cls.HEIGHT: package.height_cm,
            cls.UNIT_OF_MEASURE: "KG",
            cls.DESCRIPTION_OF_GOODS: package.customs_declaration(),
            cls.PKG_DECL_VALUE: str(float(package.value() / 100)).format("{:2f}"),
            cls.SERVICE: "86",
            cls.REFERENCE_1: package.package_number(),
        }
        return row_data

    @classmethod
    def create(cls, shipment_export):
        """Generate a shipment file for the orders associated with an export."""
        rows = cls._create_rows(shipment_export)
        output = io.StringIO()
        writer = csv.writer(output)
        # writer.writerow(cls.HEADER)
        for row in rows:
            writer.writerow(row)
        return output.getvalue()
