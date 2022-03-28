

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


