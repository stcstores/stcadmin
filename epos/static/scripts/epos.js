products = {
    '1235489' :{
        'id': '1235489',
        'name': 'Test Item 1',
        'sku': 'JLK-KLE-EJL',
        'barcode': '123456789',
        'base_price': 5.25,
        'vat_rate': 20,
        'stock_level': 50,
        'order_quantity': 1,
    },
    '987654321': {
        'id': '987654321',
        'name': 'Test Item 2',
        'sku': 'JLK-SEJ-EL3',
        'barcode': '9876543211',
        'base_price': 8.90,
        'vat_rate': 20,
        'stock_level': 50,
        'order_quantity': 5,
    }
}

products = {}
barcode_queue = {}

function change_order_quantity(product, quantity) {
    return function(event) {
        var new_quantity = quantity.val();
        if (new_quantity > 0) {
            product.order_quantity = new_quantity;
        } else {
            delete products[product.id];
        }
        update_table();
    }
}

function remove_product(product_id) {
    return function(event) {
        delete products[product_id];
        update_table();
    }
}

function update_table() {
    var product_list = $('#product_list');
    product_list.html('');
    var total_price = 0;
    var products_exist = false;
    $.each(products, function(id, product){
        products_exist = true;
        var id = product.id;
        product_list.append('<div class="product" id="product_' + id + '">');
        var product_div = $('#product_' + id);
        var price = product.base_price + (product.base_price * (product.vat_rate / 100));
        product_div.append('<div class="basic_info" id="basic_info_' + id + '">')
        var basic_info = $('#basic_info_' + id);
        basic_info.append('<p class="name">' + product.name);
        basic_info.append('<p class="sku">SKU: ' + product.sku);
        basic_info.append('<p class="barcode">Barcode: ' + product.barcode);
        basic_info.append('<p class="stock_level">Stock Level: ' + product.stock_level);
        product_div.append('<div class="quantity" id="quantity_' + id +'">');
        var quantity_div = $('#quantity_' + id);
        quantity_div.append('<input type="text" class="order_quantity" size="3" value="' + product.order_quantity + '" id="product_' + id + '_quantity">');
        quantity_div.append('<button class="remove_product" id="remove_product_' + id + '">Remove</button>');
        var remove_button = $('#remove_product_' + id);
        remove_button.click(remove_product(id));
        product_div.append('<div class="product_price" id="price_' + id + '">')
        var price_div = $('#price_' + id);
        price_div.append('<p class="base_price">' + accounting.formatMoney(product.base_price, "£ ", 2));
        price_div.append('<p class="vat_rate">VAT: ' + product.vat_rate + '%');
        price_div.append('<p class="item_price">' + accounting.formatMoney(price, "£ ", 2));
        var product_total = price * product.order_quantity;
        total_price += product_total;
        price_div.append('<p class="total_price">' + accounting.formatMoney(product_total, "£ ", 2));
        var quantity = $('#product_' + id + '_quantity');
        quantity.change(change_order_quantity(product, quantity));
        if (product.order_quantity > 1) {
            quantity.css('background', 'black');
            quantity.css('color', 'white');
        }

    });
    $('#order_total').html(accounting.formatMoney(total_price, "£ ", 2));
    if ((products_exist === true) && ($.active <= 1)) {
        $('#complete_order').attr('disabled', false);
    } else {
        $('#complete_order').attr('disabled', true);
    }
    $('#barcode_search').val('');
    $('#barcode_search').focus();
}

$( document ).ajaxComplete(function() {
    if ($.active === 1) {
        $('.search, #epos_footer').css('background', '#ddd');
        update_table();
    }
});

$(document).ready(function() {
    $('#barcode_search_button').click(function() {
        var barcode = $('#barcode_search').val();
        $('#barcode_search').val('');
        var done = false;
        $.each(products, function(id, product) {
            if (product.barcode == barcode) {
                product.order_quantity ++;
                update_table();
                done = true;
            }
        });
        if (done === false){
            if (barcode in barcode_queue) {
                barcode_queue[barcode] += 1;
            } else {
                barcode_queue[barcode] = 1;
                $('.search, #epos_footer').css('background', 'blue');
                $('#complete_order').attr('disabled', true);
                $.post(search_url, {'barcode': barcode}, function(data) {
                    if (data === 'Not Found') {
                        alert('No Product found with barcode: ' + barcode);
                    } else {
                        product = JSON.parse(data);
                        product.order_quantity = barcode_queue[barcode];
                        delete barcode_queue[barcode];
                        products[product.id] = product;
                    }
                });
            }
            update_table();
        }
    });

    $('#barcode_search').keypress(function (e) {
        if (e.which == 13) {
            $('#barcode_search_button').click();
        }
    });

    $('#complete_order').click(function (){
        $.ajax({
            url: complete_url,
            type: "POST",
            data: JSON.stringify(products),
            contentType: "application/json",
            success: function (data) {
                alert(data);
                products = {};
            }
        });
    });

    $('#cancel_order').click(function() {
        location.reload();
    });

    update_table();
});
