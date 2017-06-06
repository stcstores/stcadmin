$(document).ready(function() {

    function add_product_to_table(product) {
        var stock_input = "<input type='number' id='stock_" + product.variation_id + "''>";
        var location_input = "<input id='location_" + product.variation_id + "''>";
        var row = "<tr><td>" + product.sku + "</td><td>" + product.name + "</td><td>" + location_input + "</td><td>" + stock_input  + "</td><td><button id='update_" + product.variation_id + "'>Update</button></td></tr>";
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
        table.append('<thead><tr><th>SKU</th><th>Name</th><th>Location</th><th>Stock</th><th></th></tr></thead>')

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
                update_product_details(response);
            },
            contentType: "application/json",
            dataType: 'json'
        });
    }

    function update_product_details(response) {
        product_details = {};
        for (var i = 0; i < response.length; i++) {
            var variation_id = response[i].variation_id;
            var stock_level = response[i].stock_level;
            var locations = response[i].locations;
            product_details[variation_id] = {
                'stock_level': stock_level,
                'locations': locations,
            }
            change_stock_level(variation_id, stock_level);
            change_locations(variation_id, locations);
            $('#update_' + variation_id).click(update_stock_button(variation_id));
        }
    }

    function change_stock_level(variation_id, stock_level) {
        $('#stock_' + variation_id).val(stock_level);
    }

    function change_locations(variation_id, locations) {
        $('#location_' + variation_id).val(locations);
    }

    function update_stock_button(product_id) {
        return function (event) {
            var stock_input = $('#stock_' + product_id);
            $.ajax({
                type: 'POST',
                url: update_stock_url,
                data: JSON.stringify({
                    'product_id': product_id,
                    'new_stock_level': stock_input.val(),
                    'old_stock_level': product_details[product_id].stock_level,
                }),
                success: function(response) {
                    console.log(response);
                    product_details[product_id].stock_level = response;
                    $('#stock_' + product_id).val(response);
                },
                contentType: "application/json",
                dataType: 'json'
            });
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
