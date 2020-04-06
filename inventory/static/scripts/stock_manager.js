$(document).ready(function () {

    $('.stock_update_button').each(function () {
        var button = $(this);
        var product_id = $(this).attr('id').replace('update_', '');
        button.click(update_stock_button(product_id));
    });

    $('.show_hide_products').click(function () {
        var range_id = $(this).attr('id').replace('show_hide_products_', '');
        var product_lists = $('#products_' + range_id);
        toggle_products(product_lists);
    });

    $('#show_hide_all').click(function () {
        var product_lists = $('.product_list');
        if (product_lists.first().is(":hidden")) {
            product_lists.each(function () {
                show_products($(this));
            });
        } else {
            product_lists.each(function () {
                hide_products($(this));
            });
        }
    });

    function toggle_products(product_list) {
        if (product_list.is(":hidden")) {
            show_products(product_list)
        } else if (product_list.is(":visible")) {
            hide_products(product_list);
        }
    }

    function show_products(product_list) {
        var range_id = product_list.attr('id').replace('products_', '');
        var icon = $('#product_collapse_icon_' + range_id);
        product_list.show();
        icon.removeClass("fa-chevron-circle-right");
        icon.addClass("fa-chevron-circle-down");
    }

    function hide_products(product_list) {
        var range_id = product_list.attr('id').replace('products_', '');
        var icon = $('#product_collapse_icon_' + range_id);
        product_list.hide();
        icon.removeClass("fa-chevron-circle-down");
        icon.addClass("fa-chevron-circle-right");
    }

    function change_stock_level(variation_id, stock_level) {
        $('#stock_' + variation_id).val(stock_level);
    }

    function update_stock_button(product_id) {
        return function (event) {
            update_stock(product_id);
        }
    }

    function update_stock(product_id) {
        var stock_input = $('#stock_' + product_id);
        var new_stock_level = stock_input.val();
        var current_stock_level = product_details[product_id].stock_level
        var sku = product_details[product_id].sku
        console.log(product_details[product_id]);
        if (new_stock_level == current_stock_level) {
            return;
        }
        $('#update_' + product_id).prop('disabled', true);
        var status = $('#status_' + product_id);
        status.attr('src', loading_image);
        $.ajax({
            type: 'POST',
            url: update_stock_url,
            data: JSON.stringify({
                'product_id': product_id,
                'sku': sku,
                'new_stock_level': stock_input.val(),
                'old_stock_level': product_details[product_id].stock_level,
            }),
            success: function (response) {
                product_details[product_id].stock_level = response;
                $('#stock_' + product_id).val(response);
                status.attr('src', complete_image);
                $('#update_' + product_id).prop('disabled', false);
            },
            error: function () {
                api_error();
                status.attr('src', error_image);
            },
            contentType: "application/json",
            dataType: 'json'
        });
    }
});