var successIcon = '<i class="bi bi-check text-success"></i>';
var loadingIcon = '<div class="spinner-border spinner-border-sm text-warning"><span class="sr-only"></span></div>';
var errorIcon = '<i class="bi bi-exclamation-triangle-fill text-danger"></i>';

function setReorderCount() {
    $.each(reorderCounts, function(productId, count) {
        $("#order_count_input_" + productId).val(count);
    });
}

function setComments() {
    $.each(reorderComments, function(productId, reorderComment) {
        $("#comment_" + productId).val(reorderComment);
        updateCommentAvailability();
    });
}

function updateCommentAvailability() {
    $(".comment_input").each(function() {
        var productId = $(this).data('product_id');
        if ($("#order_count_input_" + productId).val() === "0") {
            $(this).val("");
            $(this).attr('disabled', true);
        } else {
            $(this).attr('disabled', false);
        }
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

function enableComment() {
    $('.comment_input').change(function() {
        var productId = $(this).data('product_id');
        var comment = $(this).val();
        updateComment(productId, comment);
    });
}
function enableSupplierComment() {
    $('.supplier_comment_input').change(function() {
        var supplierId = $(this).data('supplier_id');
        var comment = $(this).val();
        updateSupplierComment(supplierId, comment);
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
    status.html(loadingIcon);
    $.ajax({
        url: updatePriceUrl,
        type: "POST",
        data: {"product_id": productId, "updated_purchase_price": updatedPrice},
        success: function(response) {
            $("#purchase_price_input_" + productId).val(response['purchase_price']);
            status.html(successIcon);
        },
        error: function(response) {
            status.html(errorIcon);
        }
    });
}

function updateOrderCount(productId, updatedCount) {
    var status = $('#order_count_status_' + productId);
    status.html('<div class="spinner-border spinner-border-sm text-warning"><span class="sr-only"></span></div>');
    $.ajax({
        url: updateOrderCountUrl,
        type: "POST",
        data: {"product_id": productId, "updated_order_count": updatedCount},
        success: function(response) {
            $("#order_count_input_" + productId).val(response['count'])
            status.html(successIcon);
            updateCommentAvailability();
        },
        error: function(response) {
            status.html(errorIcon);
            updateCommentAvailability();
        }
    });
}

function updateComment(productId, comment) {
    var status = $('#comment_status_' + productId);
    status.html(loadingIcon);
    $.ajax({
        url: updateCommentUrl,
        type: "POST",
        data: {"product_id": productId, "comment": comment},
        success: function(response) {
            $("#comment_" + productId).val(response['comment'])
            status.html(successIcon);
        },
        error: function(response) {
            status.html(errorIcon);
        }
    });
}

function updateSupplierComment(supplierId, comment) {
    var status = $('#supplier_comment_status' + supplierId);
    status.html(loadingIcon);
    $.ajax({
        url: updateSupplierCommentUrl,
        type: "POST",
        data: {"supplier_id": supplierId, "comment": comment},
        success: function(response) {
            $("#suplier_comment_" + supplierId).val(response['comment'])
            status.html(successIcon);
        },
        error: function(response) {
            status.html(errorIcon);
        }
    });
}