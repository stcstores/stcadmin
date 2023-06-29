$(document).ready(function() {
    var sku_input = $('#sku_input');
    var variation_sku_button = $('#get_variation_sku');
    var range_sku_button = $('#get_range_sku');

    variation_sku_button.click(function() {
        $.post(new_sku_url, function(response) {
            sku_input.val(response);
            sku_input.select();
        });
    });

    range_sku_button.click(function() {
        $.post(new_range_sku_url, function(response) {
            sku_input.val(response);
            sku_input.select();
        });
    });
});
