from channels.forms import VariationFormset
from channels.models import shopify_models


def test_formset():
    formset = VariationFormset()
    assert formset.model == shopify_models.ShopifyVariation
    assert formset.extra == 0
    assert formset.can_delete is False
