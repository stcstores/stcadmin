$(document).ready(function() {
    $('.bay_stock_save').click(function () {
        var ids = $(this).attr('name').split(';');
        var product_id = ids[0];
        var bay_ID = ids[1];
        var level = $('#input_' + product_id + '-' + bay_ID).val();
        var status = $('#stock_check_status_' + product_id + '-' + bay_ID);
        status.attr('src', loading_image);
        $.ajax({
            type: 'POST',
            url: update_stock_check_url,
            data: JSON.stringify({
                'product_id': product_id,
                'bay_ID': bay_ID,
                'level': level,
            }),
            success: function(response) {
                status.attr('src', complete_image);
            },
            error: function() {
                api_error();
                status.attr('src', error_image);
            },
            contentType: "application/json",
            dataType: 'json'
        });
    });

    $.getJSON(open_orders_url, function(data) {
      $.each(data, function(product_id, in_open_orders) {
        $('#open_orders_' + product_id).text(in_open_orders);
      });
    });
});
