class PriceCalculator {
    constructor(data) {
        this.sale_price = this.to_pence(data.sale_price);
        this.postage_price = this.to_pence(data.postage_price);
        this.purchase_price = this.to_pence(data.purchase_price);
        this.vat_rate = data.vat_rate;
        this.channel_fee_percentage = data.channel_fee_percentage;
    }
    recalculate() {
        this.calculate_vat();
        this.calculate_channel_fee();
        this.calculate_profit();
        this.calculate_profit_percentage();
        this.change();
    }
    set_sale_price(sale_price_pounds) {
        this.sale_price = this.to_pence(sale_price_pounds);
        this.recalculate();
    }
    get_sale_price() {
        return this.to_pounds(this.sale_price_pence);
    }
    set_postage_price(postage_price_pounds) {
        this.postage_price = this.to_pence(postage_price_pounds);
        this.recalculate();
    }
    get_postage_price(){
        return this.to_pounds(this.postage_price);
    }
    set_vat_rate(vat_rate) {
        this.vat_rate = vat_rate;
        this.recalculate();
    }
    get_vat_rate() {
        return this.vat_rate;
    }
    get_vat() {
        return this.to_pounds(this.vat);
    }
    get_ex_vat() {
        return this.to_pounds(this.ex_vat);
    }
    set_channel_fee_percentage(channel_fee_percentage) {
        this.channel_fee_percentage = channel_fee_percentage;
        this.recalculate();
    }
    get_channel_fee() {
        return this.to_pounds(this.channel_fee);
    }
    set_purchase_price(purchase_price) {
        this.purchase_price = this.to_pence(purchase_price);
        this.recalculate();
    }
    get_purchase_price() {
        return this.to_pounds(this.purchase_price);
    }
    get_profit() {
        return this.to_pounds(this.profit);
    }
    get_profit_percentage() {
        return this.profit_percentage;
    }
    calculate_ex_vat() {
        this.ex_vat = parseInt(this.sale_price / (1 + (this.vat_rate / 100)));
    }
    calculate_vat() {
        this.calculate_ex_vat()
        this.vat = parseInt(this.sale_price - this.ex_vat);
    }
    calculate_channel_fee() {
        this.channel_fee = parseInt(this.sale_price * (this.channel_fee_percentage / 100));
    }
    calculate_profit() {
        this.profit = this.sale_price - this.vat - this.postage_price - this.channel_fee - this.purchase_price;
    }
    calculate_profit_percentage() {
        this.profit_percentage = parseFloat((this.profit / this.sale_price) * 100).toFixed(2);
    }
    to_pence(price) {
        return parseInt(price * 100);
    }
    to_pounds(pence) {
        return parseFloat(pence / 100).toFixed(2);
    }
    change() {
        console.log(this.profit);
    }
}

function format_price(price) {
    var price_string = '';
    var cls;
    if (price < 0) {
        cls = 'price_negative';
        price_string += '-';
    } else if (price == 0) {
        cls = 'price_zero';
    } else {
        cls = 'price_positive';
    }
    price_string += '£';
    price_string += Math.abs(parseFloat(price)).toFixed(2);
    var span = $(document.createElement('span'));
    span.attr('class', cls);
    span.html(price_string);
    return span;
}

function get_postage_price(calculator, country, package_type, weight, price){
    var data = {
        'country': country,
        'package_type': package_type,
        'weight': weight,
        'price': price,
    }
    console.log(data);
    $.post(
        get_postage_price_url,
        data,
        function(response) {
            data = $.parseJSON(response);
            console.log(data['price_name']);
            calculator.set_postage_price(parseInt(data['price']) / 100);
        }
    );
}
