$(document).ready(function() {

    $('.stock_update_button').each(function () {
        var button = $(this);
        var product_id = $(this).attr('id').replace('update_', '');
        button.click(update_stock_button(product_id));
    });

    function change_stock_level(variation_id, stock_level) {
        $('#stock_' + variation_id).val(stock_level);
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
});
