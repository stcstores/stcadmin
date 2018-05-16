{% load inventory_extras %}

function vat_price_widget(vat_input, ex_vat_input, with_vat_input) {
    vat_input.change(function() {
        var value = $(this).val()
        if (value == '') {
            ex_vat_input.prop('disabled', true);
            with_vat_input.prop('disabled', true);
            return
        }
        $(this).find('option[value=""]').remove();
        ex_vat_input.prop('disabled', false);
        with_vat_input.prop('disabled', false);
        with_vat_input.change();
    });

    ex_vat_input.change(function() {
        var value = $(this).val();
        if (value == '') {
            with_vat_input.val('');
            return;
        }
        var ex_vat_price = parseFloat(value);
        var gross = (ex_vat_price / 100 * parseInt(vat_input.val())) + ex_vat_price;
        with_vat_input.val(gross.toFixed(2));
    });

    with_vat_input.change(function () {
        var value = $(this).val();
        if (value == '') {
            ex_vat_input.val('');
            return;
        }
        var with_vat_price = parseFloat(value);
        var net = value / (1 + (parseInt(vat_input.val()) / 100));
        ex_vat_input.val(net.toFixed(2));
    });
    ex_vat_input.change();
    vat_input.change();
}

function warehouse_bay(warehouse, bay, lock_warehouse) {
    var warehouses = {% warehouses %};
    var bay_options = bay[0].selectize.options;

    function filter_bays() {
        var department_id = warehouse[0].selectize.getValue();
        return warehouses[department_id];
    }

    warehouse.change(function() {
        if (warehouse.val() == '') {
            bay[0].selectize.disable();
            return;
        }
        bay[0].selectize.enable();
        var selectize = bay[0].selectize;
        var value = bay.val();
        var bays = filter_bays();
        selectize.clear();
        selectize.clearOptions();
        selectize.addOption(bays);
        selectize.setValue(value);
    });

    $(document).ready(function() {
        warehouse.change();
        var value = warehouse.val();
        var name = warehouse.attr('name');
        if (lock_warehouse) {
            warehouse[0].selectize.destroy();
            warehouse.replaceWith('<input value="' + value + '" name="' + name + '" hidden/>');
            warehouse.remove();
        }
    });
}
