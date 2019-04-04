var initial_stock_levels = {};

function get_stock_level(product_id) {
  $.ajaxSetup({async: false});
  $.post(
    get_stock_url,
    {'product_ID': product_id},
    function(data) {
      initial_stock_levels[data.product_ID] = data.stock_level
      $('#stock_' + data.product_ID).val(data.stock_level);
      $('#update_' + data.product_ID).prop('disabled', false);
      $('#status_' + product_id).hide();
    },
    "json"
  );
}

function click_update_button(product_id) {
  return function (event) {
    $('#update_' + product_id).prop('disabled', true);
    $('#status_' + product_id).attr('src', loading_image);
    $('#status_' + product_id).show();
    update_stock_level(product_id);
  };
}

function update_stock_level(product_id) {
  var stock_input = $('#stock_' + product_id);
  var stock_level = stock_input.val();
  var old_stock_level = initial_stock_levels[product_id];
  request_data = {
      'product_ID': product_id,
      'new_stock_level': stock_level,
      'old_stock_level': old_stock_level,
  }
  $.post(
    update_stock_url, request_data, function(response) {
      new_stock_level = response;
      stock_level_update_success(product_id, new_stock_level);
    }
    , 'json'
    ).fail(function() {
      stock_level_update_failure(product_id);
  });
}

function stock_level_update_success(product_id, new_stock_level) {
  initial_stock_levels[product_id] = new_stock_level
  $('#stock_' + product_id).val(new_stock_level);
  $('#status_' + product_id).attr('src', complete_image);
  $('#update_' + product_id).prop('disabled', false);
}

function stock_level_update_failure(product_id) {
  $('#status_' + product_id).attr('src', error_image);
  $('#update_' + product_id).prop('disabled', false);
}

$(document).ready(function() {
  $('.stock_update_button').prop('disabled', true);
  $('.stock_level_field').val('');
});
