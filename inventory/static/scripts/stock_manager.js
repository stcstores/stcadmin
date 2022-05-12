function get_stock_level(product_id) {
  $.ajax({
    type: "POST",
    url: get_stock_url,
    data: JSON.stringify({'product_ids': [product_id]}),
    success: function (response) {
      var stock_level=response[product_id];
      set_stock_level_display(product_id, stock_level);
    },
    error: function (response) {
      get_stock_level_error_display(product_id);
    },
    contentType: "application/json",
    dataType: 'json'
  });
}

function update_stock_level(product_id) {
  var stock_input = $('#stock_' + product_id);
  var stock_level = stock_input.val();
  request_data = {"stock_updates": [{
      'product_id': product_id,
      'new_stock_level': stock_level,
  }]};
  $.ajax({
    type: "POST",
    url: update_stock_url, 
    data: JSON.stringify(request_data),
    success: function (response) {
      var new_stock_level = response[product_id];
      stock_level_update_success(product_id, new_stock_level);
    },
    error: function() {
      stock_level_update_failure(product_id);
    },
    contentType: "application/json",
    dataType: 'json',
  });
}

function set_stock_level_display(product_id, stock_level) {
  $('#stock_' + product_id).val(stock_level);
  $('#update_' + product_id).prop('disabled', true);
  $('#status_' + product_id).hide();
}

function click_update_button(product_id) {
  return function (event) {
    $('#update_' + product_id).prop('disabled', true);
    $('#status_' + product_id).attr('src', loading_image);
    $('#status_' + product_id).show();
    update_stock_level(product_id);
  };
}

function stock_level_update_success(product_id, new_stock_level) {
  $('#stock_' + product_id).val(new_stock_level);
  $('#status_' + product_id).attr('src', complete_image);
  $('#update_' + product_id).prop('disabled', false);
}

function stock_level_update_failure(product_id) {
  $('#status_' + product_id).attr('src', error_image);
  $('#update_' + product_id).prop('disabled', false);
}

function get_stock_level_error_display(product_id) {
  $('#stock_' + product_id).val("");
  $('#status_' + product_id).attr('src', error_image);
  $('#update_' + product_id).prop('disabled', true);
}

$(document).ready(function() {
  $('.stock_update_button').prop('disabled', true);
  $('.stock_level_field').val('');
  $(".stock_level_field").on("input", function() {
    var product_id = $(this).attr('id').replace("stock_", "");
    $("#update_" + product_id).prop('disabled', false);
  });
  $(".stock_level_field").focus(function() {
    $(this).select();
 });
});
