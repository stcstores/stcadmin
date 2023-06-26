function setReorderCount() {
    $.each(reorderCounts, function(productId, count) {
        $("#order_count_input_" + productId).val(count);
    });
}

function enablePurchasePrice() {
    $('.purchase_price_input').change(function() {
        var productId = $(this).data('product_id');
        var updatedPrice = $(this).val();
        updatePurchasePrice(productId, updatedPrice);
    });
}

function enableOrderCount() {
    $('.order_count_input').change(function() {
        var productId = $(this).data('product_id');
        var updatedCount = $(this).val();
        updateOrderCount(productId, updatedCount);
    });
}

function enableOrderedButton() {
    $('.ordered_button').click(function() {
        var productId = $(this).data('product_id');
        updateOrderCount(productId, 0);
    });
}

function updatePurchasePrice(productId, updatedPrice) {
    var status = $('#purchase_price_status_' + productId);
    status.html('<i class="fa-solid fa-spinner fa-spin warning"></i>');
    $.ajax({
        url: updatePriceUrl,
        type: "POST",
        data: {"product_id": productId, "updated_purchase_price": updatedPrice},
        success: function(response) {
            $("#purchase_price_input_" + productId).val(response['purchase_price']);
            status.html('<i class="fa-solid fa-spinner fa-spin warning"></i>');
            status.html('<i class="fa-solid fa-square-check success"></i>');
        },
        error: function(response) {
            status.html('<i class="fa-solid fa-triangle-exclamation error"></i>');
        }
    });
}

function updateOrderCount(productId, updatedCount) {
    var status = $('#order_count_status_' + productId);
    status.html('<i class="fa-solid fa-spinner fa-spin warning"></i>');
    $.ajax({
        url: updateOrderCountUrl,
        type: "POST",
        data: {"product_id": productId, "updated_order_count": updatedCount},
        success: function(response) {
            $("#order_count_input_" + productId).val(response['count'])
            status.html('<i class="fa-solid fa-spinner fa-spin warning"></i>');
            status.html('<i class="fa-solid fa-square-check success"></i>');
        },
        error: function(response) {
            status.html('<i class="fa-solid fa-triangle-exclamation error"></i>');
        }
    });
}