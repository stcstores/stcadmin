class PriceField {
    constructor(vat_free_field, vat_rate) {
        this.vat_free_field = vat_free_field;
        this.vat_rate = vat_rate;
        this.initial = this.vat_free_field.val();
        vat_free_field.before('Ex VAT&nbsp;');
        vat_free_field.after('&nbsp;With VAT&nbsp;<input type="number" step="any" id="' + vat_free_field.attr('id') + '_plus_vat">');
        this.with_vat_field = $('#' + vat_free_field.attr('id') + '_plus_vat');
        var price_field = this;
        this.vat_free_field.change(this.change_vat_free(price_field));
        this.with_vat_field.change(this.change_with_vat(price_field));
        if (this.initial !== '') {
            this.vat_free_field.val(this.initial);
            this.vat_free_field.change();
        }
        if (this.vat_rate === false) {
            this.disable();
        }
    }
    add_vat(value) {
        var gross = (value / 100 * this.vat_rate) + value;
        return gross.toFixed(2);
    }
    remove_vat(value) {
        var vat_free = value / (1 + (this.vat_rate / 100));
        return vat_free.toFixed(2);
    }
    disable() {
        this.vat_free_field.attr('disabled', true);
        this.with_vat_field.attr('disabled', true);
    }
    enable() {
        this.vat_free_field.attr('disabled', false);
        this.with_vat_field.attr('disabled', false);
    }
    set_vat_rate(vat_rate) {
        this.vat_rate = vat_rate;
        if (this.vat_rate === false) {
            this.disable();
        } else {
            this.enable();
            this.with_vat_field.change();
        }
    }
    change_with_vat(price_field) {
        return function() {
            var gross = parseFloat(price_field.with_vat_field.val());
            price_field.vat_free_field.val(price_field.remove_vat(gross));
        }
    }
    change_vat_free(price_field) {
        return function() {
            var net = parseFloat(price_field.vat_free_field.val());
            price_field.with_vat_field.val(price_field.add_vat(net));
        }
    }
    show_rate() {
        this.with_vat_field.after('&nbsp;at&nbsp;' + this.vat_rate + '%');
    }
}
