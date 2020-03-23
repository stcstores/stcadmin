from unittest.mock import patch

import pytest

from fnac.management import commands


@pytest.fixture
def mocked_update_inventory():
    with patch(
        "fnac.management.commands.update_fnac_inventory.update_inventory"
    ) as mock_update_inventory:
        yield mock_update_inventory


def test_update_inventory(mocked_update_inventory):
    commands.update_fnac_inventory.Command().handle()
    assert mocked_update_inventory.called_once()


def test_update_inventory_error_handling(mocked_update_inventory):
    mocked_update_inventory.side_effect = ValueError
    with pytest.raises(ValueError):
        commands.update_fnac_inventory.Command().handle()
