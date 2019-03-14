class PriceCalculator {
    constructor(data) {
        this.exchange_rate = 1;
        this.currency_code = 'GBP';
        this.currency_symbol = '£';
        this.sale_price = this.to_pence(data.sale_price);
        this.postage_price = this.to_pence(data.postage_price);
        this.purchase_price = this.to_pence(data.purchase_price);
        this.min_channel_fee = data.min_channel_fee
        this.vat_rate = data.vat_rate;
        this.channel_fee_percentage = data.channel_fee_percentage;
        this.shipping_service = 'No Shipping Service'
        this.valid = true;
    }
    recalculate() {
        this.calculate_vat();
        this.calculate_channel_fee();
        this.calculate_profit();
        this.calculate_profit_percentage();
        this.calculate_return_percentage();
        this.foreign_sale_price = this.sale_price / this.exchange_rate;
        this.change();
    }
    to_pence(price) {
        return parseInt(price * 100);
    }
    to_pounds(pence) {
        return parseFloat(pence / 100).toFixed(2);
    }
    set_sale_price(sale_price_pounds) {
        this.sale_price = this.to_pence(sale_price_pounds);
        this.recalculate();
    }
    set_exchange_rate(exchange_rate) {
        this.exchange_rate = exchange_rate;
        this.recalculate();
    }
    set_foreign_sale_price(foreign_sale_price_pounds) {
        this.foreign_sale_price = this.to_pence(foreign_sale_price_pounds);
        this.set_sale_price(this.foreign_sale_price * this.exchange_rate);
    }
    get_sale_price() {
        return this.to_pounds(this.sale_price_pence);
    }
    get_foreign_sale_price() {
        return this.to_pounds(this.foreign_sale_price);
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
    get_return_percentage() {
        return this.return_percentage;
    }
    calculate_ex_vat() {
        this.ex_vat = parseInt(this.sale_price / (1 + (this.vat_rate / 100)));
    }
    calculate_vat() {
        this.calculate_ex_vat()
        this.vat = parseInt(this.sale_price - this.ex_vat);
    }
    calculate_channel_fee() {
        var fee = parseInt(this.sale_price * (this.channel_fee_percentage / 100));
        if (fee < this.min_channel_fee) {
            this.channel_fee = this.min_channel_fee;
        } else {
            this.channel_fee = fee;
        }

    }
    calculate_profit() {
      if (!this.valid) {
        this.profit = 0;
      } else {
        this.profit = this.sale_price - this.vat - this.postage_price - this.channel_fee - this.purchase_price;
      }
    }
    calculate_profit_percentage() {
      if (!this.valid) {
        this.profit_percentage = 0;
      } else {
        this.profit_percentage = percentage(this.profit, this.sale_price).toFixed(2);
      }
    }
    calculate_return_percentage() {
      if (!this.valid) {
        this.return_percentage = 0;
      } else {
        this.return_percentage = percentage(this.profit, this.purchase_price).toFixed(2);
      }
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

function get_postage_price(
    calculator, country, package_type, international_shipping, weight, price) {
  var data = {
    'country': country,
    'package_type': package_type,
    'international_shipping': international_shipping,
    'weight': weight,
    'price': price,
  }
  console.log(data);
  $.post(
    get_postage_price_url,
    data,

    function(response) {
      data = $.parseJSON(response);
      console.log(data);
      console.log(data['vat_rates']);
      update_vat_rates(data['vat_rates'], calculator);
      calculator.set_postage_price(parseInt(data['price']) / 100);
      calculator.set_exchange_rate(parseFloat(data['exchange_rate']));
      calculator.currency_code = data['currency_code'];
      calculator.currency_symbol = data['currency_symbol'];
      calculator.min_channel_fee = parseInt(data['min_channel_fee']);
      calculator.shipping_service = data['price_name'];
      calculator.valid = data['success'];
      calculator.recalculate();
      calculator.change();
      $(document).trigger('calculator_update');
    },
  ).error(function() {
    alert('Error finding shipping service.');
  });
}

function format_percentage(element, value, high, warn) {
  if (value >= high) {
    element.removeClass('low_percentage').removeClass('warning_percentage').addClass('good_percentage');
  } else if (value < warn) {
    element.removeClass('warning_percentage').removeClass('good_percentage').addClass('low_percentage');
  } else {
    element.removeClass('low_percentage').removeClass('good_percentage').addClass('warning_percentage');
  }
}

function fixed_decimal(element) {
  var value = parseFloat(element.val());
  if (isNaN(value)) {
    element.val(0);
  } else {
    element.val(parseFloat(element.val()).toFixed(2));
  }
}

function percentage(whole, part) {
  return parseFloat((whole / part) * 100);
}
