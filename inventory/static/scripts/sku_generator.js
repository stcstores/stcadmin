$(document).ready(function() {
    var variation_sku_box = $('#variation_sku');
    var variation_sku_button = $('#get_variation_sku');

    var range_sku_box = $('#range_sku');
    var range_sku_button = $('#get_range_sku');

    variation_sku_button.click(function() {
        $.post(new_sku_url, function(response) {
            variation_sku_box.val(response);
            variation_sku_box.select();
        });
    });

    range_sku_button.click(function() {
        $.post(new_range_sku_url, function(response) {
            range_sku_box.val(response);
            range_sku_box.select();
        });
    });
});
