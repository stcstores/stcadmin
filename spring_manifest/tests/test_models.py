from datetime import datetime, timedelta
from unittest.mock import Mock, call, patch

from django.db.models import QuerySet
from django.utils import timezone

from spring_manifest import models
from stcadmin.tests.stcadmin_test import STCAdminTest


def mock_now():
    return timezone.make_aware(datetime(2020, 1, 16))


class TestSecuredMailDestination(STCAdminTest):
    fixtures = ("spring_manifest/secured_mail_destination",)

    def test_create_object(self):
        name = "Test Destination"
        manifest_row_number = 5
        models.SecuredMailDestination.objects.create(
            name=name, manifest_row_number=manifest_row_number
        )

    def test_str(self):
        destination = models.SecuredMailDestination.objects.get(id=1)
        self.assertEqual(destination.name, str(destination))


class TestCloudCommerceCountyID(STCAdminTest):
    fixtures = (
        "spring_manifest/secured_mail_destination",
        "spring_manifest/cloud_commerce_country_id",
    )

    def test_create_object(self):
        name = "Test Country"
        cc_id = "38493893"
        iso_code = "TC"
        secured_mail_destination = models.SecuredMailDestination.objects.get(id=1)
        currency_code = "GBP"
        country = models.CloudCommerceCountryID.objects.create(
            name=name,
            cc_id=cc_id,
            iso_code=iso_code,
            secured_mail_destination=secured_mail_destination,
            currency_code=currency_code,
        )
        self.assertEqual(name, country.name)
        self.assertEqual(cc_id, country.cc_id)
        self.assertEqual(iso_code, country.iso_code)
        self.assertEqual(secured_mail_destination, country.secured_mail_destination)
        self.assertEqual(currency_code, country.currency_code)

    def test_str(self):
        country = models.CloudCommerceCountryID.objects.get(id=401)
        self.assertEqual(country.name, str(country))


class TestCloudCommerceShippingRule(STCAdminTest):
    fixtures = ("spring_manifest/cloud_commerce_shipping_rule",)

    def test_create_object(self):
        name = "Test Shipping Rule"
        full_name = "Test Shipping Rule - Royal Mail"
        rule_id = "3859348"
        rule = models.CloudCommerceShippingRule.objects.create(
            name=name, full_name=full_name, rule_id=rule_id
        )
        self.assertEqual(name, rule.name)
        self.assertEqual(full_name, rule.full_name)
        self.assertEqual(rule_id, rule.rule_id)

    def test_str(self):
        rule = models.CloudCommerceShippingRule.objects.get(id=1)
        self.assertEqual(f"{rule.rule_id} - {rule.name}", str(rule))


class TestCounter(STCAdminTest):
    fixtures = ("spring_manifest/counter",)

    def test_create_object(self):
        name = "New Counter"
        count = 5
        counter = models.Counter.objects.create(name=name, count=count)
        self.assertEqual(name, counter.name)
        self.assertEqual(count, counter.count)

    def test_str(self):
        counter = models.Counter.objects.get(id=1)
        self.assertEqual(counter.name, str(counter))


class TestManifestType(STCAdminTest):
    fixtures = ("spring_manifest/manifest_type",)

    def test_create_object(self):
        name = "Test Manifest Type"
        manifest_type = models.ManifestType.objects.create(name=name)
        self.assertEqual(name, manifest_type.name)

    def test_str(self):
        manifest_type = models.ManifestType.objects.get(id=1)
        self.assertEqual(manifest_type.name, str(manifest_type))


class TestManifestService(STCAdminTest):
    fixtures = (
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/cloud_commerce_shipping_rule",
    )

    def test_create_object(self):
        name = "Test Manifest Service"
        code = "TMS"
        manifest_type = models.ManifestType.objects.get(id=1)
        shipping_rules = list(
            models.CloudCommerceShippingRule.objects.filter(id__lte=3)
        )
        manifest_service = models.ManifestService.objects.create(
            name=name, code=code, manifest_type=manifest_type
        )
        manifest_service.shipping_rules.set(shipping_rules)
        self.assertEqual(name, manifest_service.name)
        self.assertEqual(code, manifest_service.code)
        self.assertEqual(manifest_type, manifest_service.manifest_type)
        self.assertTrue(manifest_service.enabled)
        self.assertCountEqual(
            list(manifest_service.shipping_rules.all()), shipping_rules
        )

    def test_str(self):
        manifest_service = models.ManifestService.objects.get(id=1)
        self.assertEqual(manifest_service.name, str(manifest_service))

    def test_shipping_fule_IDs(self):
        manifest_service = models.ManifestService.objects.get(id=1)
        shipping_rules = list(
            models.CloudCommerceShippingRule.objects.filter(id__lte=3)
        )
        manifest_service.shipping_rules.set(shipping_rules)
        self.assertEqual(
            ", ".join([str(rule) for rule in shipping_rules]),
            manifest_service.shipping_rule_IDs(),
        )
        manifest_service.shipping_rules.set([])
        self.assertEqual(
            "No shipping rules selected.", manifest_service.shipping_rule_IDs()
        )

    def test_enabled_services(self):
        self.assertCountEqual(
            list(models.ManifestService.objects.filter(enabled=True)),
            list(models.ManifestService.enabled_services.all()),
        )


class TestSecuredMailService(STCAdminTest):
    fixtures = (
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/cloud_commerce_shipping_rule",
        "spring_manifest/secured_mail_service",
    )

    def test_create_object(self):
        shipping_service = models.ManifestService.objects.get(id=1)
        docket_service = "Test Docket Service"
        format = "Test Format"
        proof_of_delivery = "Test Proof of Delivery"
        secured_mail_service = models.SecuredMailService.objects.create(
            shipping_service=shipping_service,
            docket_service=docket_service,
            format=format,
            proof_of_delivery=proof_of_delivery,
        )
        self.assertEqual(shipping_service, secured_mail_service.shipping_service)
        self.assertFalse(secured_mail_service.on_manifest)
        self.assertFalse(secured_mail_service.on_docket)
        self.assertEqual(docket_service, secured_mail_service.docket_service)
        self.assertEqual(format, secured_mail_service.format)
        self.assertEqual(proof_of_delivery, secured_mail_service.proof_of_delivery)

    def test_str(self):
        name = "Test Name"
        secured_mail_service = models.SecuredMailService.objects.get(id=1)
        secured_mail_service.shipping_service.name = name
        self.assertEqual(name, str(secured_mail_service))
        secured_mail_service.shipping_service = None
        self.assertEqual(
            "Secured Mail Service Not Matched To Manifest Service",
            str(secured_mail_service),
        )

    def test_filed(self):
        self.assertCountEqual(
            list(models.Manifest.filed.all()),
            list(models.Manifest.objects.filter(status=models.Manifest.FILED)),
        )

    def test_unfiled(self):
        self.assertCountEqual(
            list(models.Manifest.unfiled.all()),
            list(models.Manifest.objects.exclude(status=models.Manifest.FILED)),
        )


class TestManifest(STCAdminTest):
    fixtures = (
        "spring_manifest/manifest_type",
        "spring_manifest/manifest",
    )

    @patch("django.utils.timezone.now", mock_now)
    def test_create(self):
        manifest_type = models.ManifestType.objects.get(id=1)
        manifest = models.Manifest.objects.create(manifest_type=manifest_type)
        self.assertEqual(manifest_type, manifest.manifest_type)
        self.assertEqual(mock_now(), manifest.time_created)
        self.assertIsNone(manifest.time_filed)
        self.assertFalse(manifest.manifest_file)
        self.assertFalse(manifest.item_advice_file)
        self.assertFalse(manifest.docket_file)
        self.assertEqual(manifest.UNFILED, manifest.status)
        self.assertFalse(manifest.closed)
        self.assertFalse(manifest.files_sent)
        self.assertIsNone(manifest.errors)

    def test_str(self):
        manifest = models.Manifest.objects.get(id=1)
        manifest.time_filed = None
        self.assertEqual(f"1_{manifest.manifest_type.name}_Unfiled", str(manifest))
        manifest.time_filed = mock_now()
        self.assertEqual(
            f'1_{manifest.manifest_type.name}_{mock_now().strftime("%Y-%m-%d")}',
            str(manifest),
        )

    @patch("spring_manifest.models.manifest_model.timezone.now", mock_now)
    def test_file_manifest(self):
        manifest_type = models.ManifestType.objects.get(id=1)
        manifest = models.Manifest.objects.create(manifest_type=manifest_type)
        self.assertIsNone(manifest.time_filed)
        manifest.file_manifest()
        manifest.refresh_from_db()
        self.assertEqual(mock_now(), manifest.time_filed)

    def test_get_error_list(self):
        manifest_type = models.ManifestType.objects.get(id=1)
        manifest = models.Manifest.objects.create(manifest_type=manifest_type)
        self.assertIsNone(manifest.get_error_list())
        manifest.errors = "Error 1\nError 2"
        self.assertEqual(["Error 1", "Error 2"], manifest.get_error_list())


class TestManifestUpdate(STCAdminTest):
    fixtures = ("spring_manifest/manifest_update",)

    @patch("django.utils.timezone.now", mock_now)
    def test_create_object(self):
        update = models.ManifestUpdate.objects.create()
        self.assertEqual(mock_now(), update.started)
        self.assertIsNone(update.finished)
        self.assertEqual(update.IN_PROGRESS, update.status)

    def test_str(self):
        update = models.ManifestUpdate.objects.create()
        self.assertEqual(update.started.strftime("%d-%m-%Y %H:%M:%S"), str(update))

    @patch("django.utils.timezone.now", mock_now)
    def test_complete(self):
        update = models.ManifestUpdate.objects.create()
        update.complete()
        update.refresh_from_db()
        self.assertEqual(update.COMPLETE, update.status)
        self.assertEqual(mock_now(), update.finished)

    def test_fail(self):
        update = models.ManifestUpdate.objects.create()
        update.fail()
        update.refresh_from_db()
        self.assertEqual(update.FAILED, update.status)
        self.assertIsNone(update.finished)

    @patch("spring_manifest.models.manifest_model.timezone.now", mock_now)
    def test_time_since_update(self):
        update = models.ManifestUpdate.objects.create()
        self.assertIsNone(update.time_since_update())
        update.finished = mock_now() - timedelta(days=1)
        self.assertEqual(timedelta(days=1), update.time_since_update())


class TestManifestOrder(STCAdminTest):
    fixtures = (
        "spring_manifest/secured_mail_destination",
        "spring_manifest/cloud_commerce_country_id",
        "spring_manifest/cloud_commerce_shipping_rule",
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/secured_mail_service",
        "spring_manifest/manifest",
        "spring_manifest/manifest_order",
        "spring_manifest/manifest_package",
        "spring_manifest/manifest_item",
    )

    def test_create_object(self):
        order_id = "384939"
        customer_name = "Test Customer Name"
        date_recieved = mock_now()
        dispatch_date = mock_now() + timedelta(days=2)
        country = models.CloudCommerceCountryID.objects.get(id=401)
        order = models.ManifestOrder.objects.create(
            order_id=order_id,
            customer_name=customer_name,
            date_recieved=date_recieved,
            dispatch_date=dispatch_date,
            country=country,
        )
        self.assertEqual(order_id, order.order_id)
        self.assertEqual(customer_name, order.customer_name)
        self.assertEqual(date_recieved, order.date_recieved)
        self.assertEqual(dispatch_date, order.dispatch_date)
        self.assertEqual(country, order.country)
        self.assertIsNone(order.manifest)
        self.assertIsNone(order.service)
        self.assertFalse(order.canceled)
        self.assertIsNone(order._packages)

    def test_datetimes_localized(self):
        order = models.ManifestOrder.objects.get(id=1)
        order.date_recieved = datetime(2019, 7, 22)
        order.dispatch_date = datetime(2019, 7, 23)
        order.save()
        self.assertTrue(timezone.is_aware(order.date_recieved))
        self.assertTrue(timezone.is_aware(order.dispatch_date))

    def test_str(self):
        order = models.ManifestOrder.objects.get(id=1)
        self.assertEqual(order.order_id, str(order))

    def test_canceled_order_is_removed_from_manifest(self):
        order = models.ManifestOrder.objects.get(id=1)
        self.assertIsNotNone(order.manifest)
        order.canceled = True
        order.save()
        order.refresh_from_db()
        self.assertIsNone(order.manifest)

    def test_add_to_manifest(self):
        order = models.ManifestOrder.objects.get(id=1)
        manifest = models.Manifest.objects.get(id=1)
        order.manifest = None
        order.save()
        order.refresh_from_db()
        self.assertIsNone(order.manifest)
        order.add_to_manifest(manifest)
        order.refresh_from_db()
        self.assertEqual(manifest, order.manifest)

    def test_items(self):
        order = models.ManifestOrder.objects.get(id=1)
        items = models.ManifestItem.objects.filter(package__order=order)
        self.assertEqual(list(items), list(order.items()))

    @patch("spring_manifest.models.manifest_order_model.CCAPI")
    def test_get_order_data(self, mock_CCAPI):
        cc_order = Mock()
        mock_CCAPI.get_orders_for_dispatch.return_value = [cc_order]
        order = models.ManifestOrder.objects.get(id=1)
        self.assertEqual(cc_order, order.get_order_data())
        mock_CCAPI.get_orders_for_dispatch.assert_called_once_with(
            order_type=1, number_of_days=30, id_list=[order.order_id]
        )

    @patch("spring_manifest.models.manifest_order_model.CCAPI")
    def test_get_cc_item_dict(self, mock_CCAPI):
        product_id = "384939"
        quantity = 5
        cc_order = Mock(products=[Mock(product_id=product_id, quantity=quantity)])
        mock_CCAPI.get_orders_for_dispatch.return_value = [cc_order]
        order = models.ManifestOrder.objects.get(id=1)
        self.assertEqual({int(product_id): quantity}, order.get_cc_item_dict())
        mock_CCAPI.get_orders_for_dispatch.assert_called_once_with(
            order_type=1, number_of_days=30, id_list=[order.order_id]
        )

    def test_get_item_dict(self):
        order = models.ManifestOrder.objects.get(id=1)
        items = models.ManifestItem.objects.filter(package__order=order)
        item_dict = {item.item_id: item.quantity for item in items}
        self.assertDictEqual(item_dict, order.get_item_dict())

    @patch("spring_manifest.models.manifest_order_model.CCAPI")
    def test_check_items(self, mock_CCAPI):
        product_id = "384939"
        quantity = 5
        cc_order = Mock(products=[Mock(product_id=product_id, quantity=quantity)])
        mock_CCAPI.get_orders_for_dispatch.return_value = [cc_order]
        order = models.ManifestOrder.objects.get(id=1)
        self.assertFalse(order.check_items())
        models.ManifestPackage.objects.all().delete()
        models.ManifestItem.objects.all().delete()
        package = models.ManifestPackage.objects.create(order=order)
        models.ManifestItem.objects.create(
            package=package, item_id=product_id, quantity=quantity
        )

    def test_check_item_quantity(self):
        order = models.ManifestOrder.objects.get(id=1)
        items = models.ManifestItem.objects.filter(package__order=order)
        quantity = sum((item.quantity for item in items))
        self.assertEqual(quantity, order.item_quantity())

    def test_packages(self):
        order = models.ManifestOrder.objects.get(id=1)
        self.assertIsNone(order._packages)
        packages = order.packages
        self.assertEqual(
            list(packages), list(models.ManifestPackage.objects.filter(order=order)),
        )
        self.assertEqual(packages, order._packages)
        mock_packages = Mock()
        order._packages = mock_packages
        self.assertEqual(mock_packages, order.packages)

    def test_secured_mail_service(self):
        order = models.ManifestOrder.objects.get(id=1)
        service = models.SecuredMailService.objects.get(id=1)
        order.service = service.shipping_service
        self.assertEqual(service, order.secured_mail_service)
        models.SecuredMailService.objects.all().delete()
        order.refresh_from_db()
        self.assertIsNone(order.secured_mail_service)

    def test_weight(self):
        order = models.ManifestOrder.objects.get(id=1)
        items = models.ManifestItem.objects.filter(package__order=order)
        weight = sum((_.weight for _ in items))
        self.assertEqual(weight, order.weight)

    def test_manifested_manager(self):
        manifested = models.ManifestOrder.manifested.all()
        self.assertIsInstance(manifested, QuerySet)
        self.assertGreater(manifested.count(), 0)
        self.assertEqual(
            list(manifested),
            list(models.ManifestOrder.objects.filter(manifest__isnull=False)),
        )

    def test_unmanifested_manager(self):
        unmanifested = models.ManifestOrder.unmanifested.all()
        self.assertIsInstance(unmanifested, QuerySet)
        self.assertGreater(unmanifested.count(), 0)
        self.assertEqual(
            list(unmanifested),
            list(
                models.ManifestOrder.objects.filter(
                    manifest__isnull=True, canceled=False
                )
            ),
        )

    def test_filed_manager(self):
        filed = models.ManifestOrder.filed.all()
        self.assertIsInstance(filed, QuerySet)
        self.assertGreater(filed.count(), 0)
        self.assertEqual(
            list(filed),
            list(
                models.ManifestOrder.objects.filter(
                    manifest__isnull=False, manifest__time_filed__isnull=False
                )
            ),
        )

    def test_unfiled_manager(self):
        unfiled = models.ManifestOrder.unfiled.all()
        self.assertIsInstance(unfiled, QuerySet)
        self.assertGreater(unfiled.count(), 0)
        self.assertEqual(
            list(unfiled),
            list(
                models.ManifestOrder.objects.filter(
                    manifest__isnull=False,
                    manifest__time_filed__isnull=True,
                    canceled=False,
                )
            ),
        )

    def test_canceled_orders_manager(self):
        canceled_orders = models.ManifestOrder.canceled_orders.all()
        self.assertIsInstance(canceled_orders, QuerySet)
        self.assertGreater(canceled_orders.count(), 0)
        self.assertEqual(
            list(canceled_orders),
            list(models.ManifestOrder.objects.filter(canceled=True)),
        )

    def test_manager_order_ids(self):
        order_ids = set(o.order_id for o in models.ManifestOrder.objects.all())
        self.assertEqual(order_ids, models.ManifestOrder.objects.order_ids())

    def test_manager_items(self):
        items = models.ManifestItem.objects.all()
        self.assertEqual(list(items), list(models.ManifestOrder.objects.items()))


class TestManifestPackage(STCAdminTest):
    fixtures = (
        "spring_manifest/secured_mail_destination",
        "spring_manifest/cloud_commerce_country_id",
        "spring_manifest/cloud_commerce_shipping_rule",
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/secured_mail_service",
        "spring_manifest/manifest",
        "spring_manifest/manifest_order",
        "spring_manifest/manifest_package",
        "spring_manifest/manifest_item",
    )

    def test_create_object(self):
        order = models.ManifestOrder.objects.get(id=1)
        package_number = 15
        package = models.ManifestPackage.objects.create(
            order=order, package_number=package_number
        )
        self.assertEqual(order, package.order)
        self.assertEqual(package_number, package.package_number)
        self.assertIsNone(package._items)

    def test_package_id(self):
        package = models.ManifestPackage.objects.get(id=1)
        self.assertEqual(
            f"{package.order.order_id}_{package.package_number}", package.package_id()
        )

    def test_str(self):
        package = models.ManifestPackage.objects.get(id=1)
        self.assertEqual(package.package_id(), str(package))

    def test_items(self):
        package = models.ManifestPackage.objects.get(id=1)
        self.assertIsNone(package._items)
        items = package.items
        self.assertEqual(
            list(items),
            list(models.ManifestItem.objects.filter(package=package, quantity__gt=0)),
        )
        self.assertEqual(items, package._items)
        mock_items = Mock()
        package._items = mock_items
        self.assertEqual(mock_items, package.items)

    def test_quantity(self):
        package = models.ManifestPackage.objects.get(id=1)
        quantity = sum(
            (
                _.quantity
                for _ in models.ManifestItem.objects.filter(
                    package=package, quantity__gt=0
                )
            )
        )
        self.assertEqual(quantity, package.quantity)

    def test_weight(self):
        package = models.ManifestPackage.objects.get(id=1)
        weight = sum(
            (
                _.weight
                for _ in models.ManifestItem.objects.filter(
                    package=package, quantity__gt=0
                )
            )
        )
        self.assertEqual(weight, package.weight)


class TestManifestItem(STCAdminTest):
    fixtures = (
        "spring_manifest/secured_mail_destination",
        "spring_manifest/cloud_commerce_country_id",
        "spring_manifest/cloud_commerce_shipping_rule",
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/secured_mail_service",
        "spring_manifest/manifest",
        "spring_manifest/manifest_order",
        "spring_manifest/manifest_package",
        "spring_manifest/manifest_item",
    )

    def test_create_object(self):
        package = models.ManifestPackage.objects.get(id=1)
        item_id = 28793783
        weight = 50
        quantity = 5
        item = models.ManifestItem.objects.create(
            package=package, item_id=item_id, weight=weight, quantity=quantity
        )
        self.assertEqual(package, item.package)
        self.assertEqual(item_id, item.item_id)
        self.assertEqual(weight, item.weight)
        self.assertEqual(quantity, item.quantity)
        self.assertEqual("?", item.name)
        self.assertEqual("?", item.full_name)

    def test_str(self):
        item = models.ManifestItem.objects.get(id=1)
        self.assertEqual(f"{item.package}_{item.item_id}", str(item))

    @patch("spring_manifest.models.manifest_item_model.CCAPI")
    def test_get_item(self, mock_CCAPI):
        product = Mock()
        mock_CCAPI.get_product.return_value = product
        item = models.ManifestItem.objects.get(id=1)
        self.assertEqual(product, item.get_item())
        mock_CCAPI.get_product.assert_called_once_with(item.item_id)


class TestGetManifest(STCAdminTest):
    fixtures = (
        "spring_manifest/secured_mail_destination",
        "spring_manifest/cloud_commerce_country_id",
        "spring_manifest/cloud_commerce_shipping_rule",
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/secured_mail_service",
        "spring_manifest/manifest",
        "spring_manifest/manifest_order",
        "spring_manifest/manifest_package",
        "spring_manifest/manifest_item",
    )

    def test_returns_existing_manifest(self):
        manifest_type = models.ManifestType.objects.get(id=1)
        query = models.Manifest.objects.filter(
            closed=False,
            status__in=(models.Manifest.UNFILED, models.Manifest.CLOSING),
            manifest_type=manifest_type,
        )
        self.assertEqual(1, query.count())
        manifest = query[0]
        self.assertEqual(manifest, models.get_manifest(manifest_type))

    def test_creates_new_manifest(self):
        manifest_type = models.ManifestType.objects.get(id=2)
        self.assertFalse(
            models.Manifest.objects.filter(
                closed=False,
                status__in=(models.Manifest.UNFILED, models.Manifest.CLOSING),
                manifest_type=manifest_type,
            ).exists()
        )
        manifest = models.get_manifest(manifest_type)
        self.assertEqual(manifest_type, manifest.manifest_type)
        self.assertFalse(manifest.closed)
        self.assertEqual(models.Manifest.UNFILED, manifest.status)
        self.assertIsNotNone(manifest.id)

    def test_raises_exception_when_multiple_manifests_exist(self):
        manifest_type = models.ManifestType.objects.get(id=1)
        models.Manifest.objects.create(
            manifest_type=manifest_type, closed=False, status=models.Manifest.UNFILED
        )
        query = models.Manifest.objects.filter(
            closed=False,
            status__in=(models.Manifest.UNFILED, models.Manifest.CLOSING),
            manifest_type=manifest_type,
        )
        self.assertEqual(2, query.count())
        with self.assertRaises(models.Manifest.MultipleObjectsReturned):
            models.get_manifest(manifest_type)


class TestGetManifestByService(STCAdminTest):
    fixtures = (
        "spring_manifest/secured_mail_destination",
        "spring_manifest/cloud_commerce_country_id",
        "spring_manifest/cloud_commerce_shipping_rule",
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/secured_mail_service",
        "spring_manifest/manifest",
        "spring_manifest/manifest_order",
        "spring_manifest/manifest_package",
        "spring_manifest/manifest_item",
    )

    def test_get_manifest_by_service(self):
        manifest_type = models.ManifestType.objects.get(id=1)
        query = models.Manifest.objects.filter(
            closed=False,
            status__in=(models.Manifest.UNFILED, models.Manifest.CLOSING),
            manifest_type=manifest_type,
        )
        self.assertEqual(1, query.count())
        manifest = query[0]
        service = models.ManifestService.objects.filter(manifest_type=manifest_type)[0]
        self.assertEqual(manifest, models.get_manifest_by_service(service))


class TestGetOrders(STCAdminTest):
    @patch("spring_manifest.models.CCAPI")
    def test_get_orders(self, mock_CCAPI):
        courier_rule_id = "389383"
        number_of_days = 3
        mock_orders = Mock()
        mock_CCAPI.get_orders_for_dispatch.return_value = mock_orders
        self.assertEqual(
            mock_orders,
            models.get_orders(
                courier_rule_id=courier_rule_id, number_of_days=number_of_days
            ),
        )
        mock_CCAPI.get_orders_for_dispatch.assert_called_once_with(
            order_type=1, courier_rule_id=courier_rule_id, number_of_days=number_of_days
        )


class TestCloseManifest(STCAdminTest):
    fixtures = (
        "spring_manifest/secured_mail_destination",
        "spring_manifest/cloud_commerce_country_id",
        "spring_manifest/cloud_commerce_shipping_rule",
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/secured_mail_service",
        "spring_manifest/manifest",
        "spring_manifest/manifest_order",
        "spring_manifest/manifest_package",
        "spring_manifest/manifest_item",
    )

    @patch("spring_manifest.models.update_manifest_orders")
    def test_close_manifest(self, mock_update_manifest_orders):
        manifest = models.Manifest.objects.get(closed=False)
        models.close_manifest(manifest)
        manifest.refresh_from_db()
        self.assertTrue(manifest.closed)
        self.assertEqual(manifest.UNFILED, manifest.status)
        mock_update_manifest_orders.assert_called_once()

    @patch("spring_manifest.models.update_manifest_orders")
    def test_close_closed_manifest(self, mock_update_manifest_orders):
        manifest = models.Manifest.objects.get(id=1)
        self.assertTrue(manifest.closed)
        models.close_manifest(manifest)
        manifest.refresh_from_db()
        self.assertTrue(manifest.closed)
        mock_update_manifest_orders.assert_not_called()


class TestCreateOrder(STCAdminTest):
    fixtures = (
        "spring_manifest/secured_mail_destination",
        "spring_manifest/cloud_commerce_country_id",
        "spring_manifest/cloud_commerce_shipping_rule",
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/secured_mail_service",
    )

    def test_create_order(self):
        country = models.CloudCommerceCountryID.objects.get(id=401)
        mock_products = [
            Mock(
                product_name="First Product Name",
                product_full_name="First Product Full Name",
                product_id="384939",
                quantity=5,
                per_item_weight=45,
            ),
            Mock(
                product_name="Second Product Name",
                product_full_name="Second Product Full Name",
                product_id="9461651",
                quantity=2,
                per_item_weight=105,
            ),
        ]
        mock_order = Mock(
            order_id="383939",
            delivery_name="Test Customer Name",
            date_recieved=datetime(2019, 4, 13),
            dispatch_date=datetime(2019, 4, 15),
            delivery_country_code=country.cc_id,
            products=mock_products,
        )
        service = models.ManifestService.objects.get(id=1)
        models.create_order(mock_order, service)
        self.assertTrue(
            models.ManifestOrder.objects.filter(order_id=mock_order.order_id).exists()
        )
        order = models.ManifestOrder.objects.get(order_id=mock_order.order_id)
        self.assertEqual(order.order_id, mock_order.order_id)
        self.assertEqual(order.customer_name, mock_order.delivery_name)
        self.assertEqual(
            order.date_recieved, timezone.make_aware(mock_order.date_recieved)
        )
        self.assertEqual(
            order.dispatch_date, timezone.make_aware(mock_order.dispatch_date)
        )
        self.assertEqual(order.country, country)
        self.assertTrue(models.ManifestPackage.objects.filter(order=order).exists())
        package = models.ManifestPackage.objects.get(order=order)
        self.assertTrue(
            models.ManifestItem.objects.filter(
                item_id=mock_products[0].product_id
            ).exists()
        )
        product_1 = models.ManifestItem.objects.get(item_id=mock_products[0].product_id)
        self.assertTrue(
            models.ManifestItem.objects.filter(
                item_id=mock_products[1].product_id
            ).exists()
        )
        product_2 = models.ManifestItem.objects.get(item_id=mock_products[1].product_id)
        products = [product_1, product_2]
        for mock_product, product in zip(mock_products, products):
            self.assertEqual(package, product.package)
            self.assertEqual(int(mock_product.product_id), product.item_id)
            self.assertEqual(mock_product.product_name, product.name)
            self.assertEqual(mock_product.product_full_name, product.full_name)
            self.assertEqual(mock_product.quantity, product.quantity)
            self.assertEqual(mock_product.per_item_weight, product.weight)


class TestGetManifestUpdate(STCAdminTest):
    fixtures = ("spring_manifest/manifest_update",)

    def test_get_manifest_update(self):
        self.assertEqual(
            models.ManifestUpdate.objects.latest("started"),
            models.get_manifest_update(),
        )


class TestUpdateManifestOrders(STCAdminTest):
    @patch("spring_manifest.models.update_manifest_database")
    def test_update_manifest_orders(self, mock_update_manifest_database):
        self.assertFalse(models.ManifestUpdate.objects.exclude(id=1).exists())
        models.update_manifest_orders()
        mock_update_manifest_database.assert_called_with(1)
        self.assertTrue(models.ManifestUpdate.objects.exclude(id=1).exists())
        update = models.ManifestUpdate.objects.exclude(id=1).all()[0]
        self.assertEqual(update.COMPLETE, update.status)

    @patch("spring_manifest.models.update_manifest_database")
    def test_update_manifest_orders_when_in_progress(
        self, mock_update_manifest_database
    ):
        models.ManifestUpdate.objects.filter(id=1).update(
            status=models.ManifestUpdate.IN_PROGRESS
        )
        self.assertFalse(models.ManifestUpdate.objects.filter(id=2).exists())
        models.update_manifest_orders()
        mock_update_manifest_database.assert_not_called()
        self.assertFalse(models.ManifestUpdate.objects.filter(id=2).exists())

    @patch("spring_manifest.models.update_manifest_database")
    def test_error_handling(self, mock_update_manifest_database):
        self.assertFalse(models.ManifestUpdate.objects.exclude(id=1).exists())
        mock_update_manifest_database.side_effect = Exception("Error")
        with self.assertRaises(Exception):
            models.update_manifest_orders()
        mock_update_manifest_database.assert_called_with(1)
        self.assertTrue(models.ManifestUpdate.objects.exclude(id=1).exists())
        update = models.ManifestUpdate.objects.exclude(id=1).all()[0]
        self.assertEqual(update.FAILED, update.status)


class TestUpdateManifestDatabase(STCAdminTest):
    fixtures = (
        "spring_manifest/secured_mail_destination",
        "spring_manifest/cloud_commerce_country_id",
        "spring_manifest/cloud_commerce_shipping_rule",
        "spring_manifest/manifest_type",
        "spring_manifest/manifest_service",
        "spring_manifest/secured_mail_service",
        "spring_manifest/manifest",
        "spring_manifest/manifest_order",
        "spring_manifest/manifest_package",
        "spring_manifest/manifest_item",
    )

    @patch("spring_manifest.models.create_order")
    @patch("spring_manifest.models.get_orders")
    def test_update_manifest_database(self, mock_get_orders, mock_create_order):
        models.ManifestOrder.objects.all().delete()
        number_of_days = 5
        mock_order = Mock(order_id="389339")
        mock_get_orders.return_value = [mock_order]
        models.update_manifest_database(number_of_days)
        shipping_rules = models.CloudCommerceShippingRule.objects.filter(
            manifestservice__isnull=False, manifestservice__enabled=True
        )
        get_orders_calls = [
            call(shipping_rule.rule_id, number_of_days=number_of_days)
            for shipping_rule in shipping_rules
        ]
        mock_get_orders.assert_has_calls(get_orders_calls, any_order=True)
        services = models.ManifestService.enabled_services.all()
        create_order_calls = [call(mock_order, service=service) for service in services]
        mock_create_order.assert_has_calls(create_order_calls, any_order=True)

    @patch("spring_manifest.models.create_order")
    @patch("spring_manifest.models.get_orders")
    def test_does_not_create_duplcate_orders(self, mock_get_orders, mock_create_order):
        number_of_days = 5
        order_id = "389339"
        mock_order = Mock(order_id=order_id)
        models.ManifestOrder.objects.filter(id=1).update(order_id=order_id)
        mock_get_orders.return_value = [mock_order]
        models.update_manifest_database(number_of_days)
        mock_create_order.assert_not_called()
