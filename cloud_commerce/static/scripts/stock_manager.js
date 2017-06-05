$(document).ready(function() {

    var csrftoken = $.cookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function add_product_to_table(product) {
        var stock_input = "<input type='number' id='stock_" + product.variation_id + "''>";
        var row = "<tr><td>" + product.sku + "</td><td>" + product.name + "</td><td>" + stock_input  + "</td><td><button id='update_" + product.variation_id + "'>Update</button></td></tr>";
        $('#stock_search_result').append(row);
    }

    function update_product_table() {
        reset_table();
        for (var i = 0; i < products.length; i++) {
            add_product_to_table(products[i]);
        }
        get_stock_levels_for_products(products.length);
    }

    function reset_table() {
        var table = $('#stock_search_result');
        table.empty();
        table.append('<thead><tr><td>SKU></td><td>Name</td><td>Stock</td></tr></thead>')

    }

    function get_stock_levels_for_products() {
        var variation_ids = [];
        for (var i = 0; i < products.length; i++) {
            variation_ids.push(products[i].variation_id);
        }
        console.log(variation_ids);
        $.ajax({
            type: 'POST',
            url: get_stock_url,
            data: JSON.stringify({'variation_ids': variation_ids}),
            success: function(response) {
                console.log(response);
                update_stock_numbers(response);
            },
            contentType: "application/json",
            dataType: 'json'
        });
    }

    function update_stock_numbers(response) {
        for (var i = 0; i < response.length; i++) {
            $('#stock_' + response[i].variation_id).val(response[i].stock_level);
        }
    }

    $('#stock_search_button').click(function() {
        var search_text = $('#stock_search').val();
        var url = search_url.replace('search_text', search_text);
        $.post(url, function(response) {
            products = JSON.parse(response);
            update_product_table()
        });
    });
});
