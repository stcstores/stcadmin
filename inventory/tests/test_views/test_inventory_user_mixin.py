from inventory.views import InventoryUserMixin


def test_inventory_user_mixin_has_groups():
    assert InventoryUserMixin.groups == ["inventory"]
