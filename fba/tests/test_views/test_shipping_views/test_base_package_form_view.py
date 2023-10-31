from fba.forms import PackageForm
from fba.models import FBAShipmentPackage
from fba.views.shipping import BasePackageFormView


def test_model_attribute():
    assert BasePackageFormView.model == FBAShipmentPackage


def test_template_name_attribute():
    assert (
        BasePackageFormView.template_name
        == "fba/shipments/create_shipment/package_form.html"
    )


def test_form_class_attribute():
    assert BasePackageFormView.form_class == PackageForm
