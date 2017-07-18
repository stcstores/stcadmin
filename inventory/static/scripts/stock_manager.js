$(document).ready(function() {

    $('.stock_update_button').each(function () {
        var button = $(this);
        var product_id = $(this).attr('id').replace('update_', '');
        button.click(update_stock_button(product_id));
    });

    $('.show_hide_products').click(function() {
        var range_id = $(this).attr('id').replace('show_hide_products_', '');
        var table = $('#products_table_' + range_id);
        toggle_table(table);
    });

    $('#show_hide_all').click(function() {
        var tables = $('.products_table');
        if (tables.first().css('display') === 'none') {
            tables.each(function() {
                show_table($(this));
            });
        } else {
            tables.each(function() {
                hide_table($(this));
            });
        }
    });

    function toggle_table(table) {
        if (table.css('display') === 'none') {
            show_table(table);
        } else if (table.css('display') === 'block') {
            hide_table(table);
        }
    }

    function show_table(table) {
        var range_id = table.attr('id').replace('products_table_', '');
        var show_hide = $('#show_hide_products_' + range_id);
        table.css('display', 'block');
        show_hide.text('[[ hide ]]');
    }

    function hide_table(table) {
        var range_id = table.attr('id').replace('products_table_', '');
        var show_hide = $('#show_hide_products_' + range_id);
        table.css('display', 'none');
        show_hide.text('[[ show ]]');
    }

    function change_stock_level(variation_id, stock_level) {
        $('#stock_' + variation_id).val(stock_level);
    }

    function update_stock_button(product_id) {
        return function (event) {
            var stock_input = $('#stock_' + product_id);
            if (stock_input.val() != product_details[product_id].stock_level) {
                update_stock(product_id);
            }
        }
    }

    function update_stock(product_id) {
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
});
