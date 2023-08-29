var loading = '<i class="fa-solid fa-spinner fa-spin-pulse fa-xl"></i>';

function arraymove(arr, fromIndex, toIndex) {
  var element = arr[fromIndex];
  arr.splice(fromIndex, 1);
  arr.splice(toIndex, 0, element);
}

function get_product_image_order(product_id) {
  var row = $("#row_" + product_id);
  console.log(row);
  var image_order = [];
  row.find(".product_image").each(function () {
    console.log($(this));
    image_order.push($(this).data("image-id"));
  });
  console.log(image_order);
  return image_order;
}

function get_range_image_order(product_id) {
  var row = $(".product_range_images");
  var image_order = [];
  row.find(".product_image").each(function () {
    image_order.push($(this).data("image-id"));
  });
  return image_order;
}

function select_products(product_ids) {
  var checkboxes = $(".selected input:checkbox");
  checkboxes.prop("checked", false);
  for (var i = 0; i < product_ids.length; i++) {
    $("#select_" + product_ids[i]).prop("checked", true);
  }
  $(".selected input:checkbox").change();
}

function update_product_image_order(product_id, image_order) {
  var url = setProductImageOrderURL;
  var data = {
    product_pk: product_id,
    image_order: image_order,
  };
  $("#product_images_" + product_id).html(loading);
  $.post({
    url: url,
    data: JSON.stringify(data),
    contentType: "application/json",
    dataType: "json",
    success: function (image_order) {
      console.log(image_order);
      load_product_images(product_id);
    },
    error: function () {
      api_error();
    },
  });
}

function update_range_image_order(image_order) {
  var url = setRangeImageOrderURL;
  var data = {
    product_pk: rangeId,
    image_order: image_order,
  };
  $("#product_range_images").html(loading);
  $.post({
    url: url,
    data: JSON.stringify(data),
    contentType: "application/json",
    dataType: "json",
    success: function (image_order) {
      console.log(image_order);
      load_product_range_images();
    },
    error: function () {
      api_error();
    },
  });
}

function delete_product_image(image_id, product_id) {
  var url = deleteProductImageURL;
  var data = {
    image_id: image_id,
    product_id: product_id,
  };
  $("#product_images_" + product_id).html(loading);
  $.post({
    url: url,
    data: JSON.stringify(data),
    contentType: "application/json",
    dataType: "json",
    success: function (response) {
      console.log(response);
      load_product_images(product_id);
    },
    error: function () {
      api_error();
    },
  });
}

function delete_range_image(image_id, product_id) {
  var data = {
    image_id: image_id,
    product_id: product_id,
  };
  $("#product_range_images").html(loading);
  $.post({
    url: deleteRangeImageURL,
    data: JSON.stringify(data),
    contentType: "application/json",
    dataType: "json",
    success: function (response) {
      console.log(response);
      load_product_range_images();
    },
    error: function () {
      api_error();
    },
  });
}

function load_product_images(product_id) {
  $.post({
    url: productImagesURL,
    data: { product_id: product_id },
    success: function (response) {
      $("#product_images_" + product_id).html(response);
      set_product_image_buttons();
    },
    error: function () {
      api_error();
    },
  });
}

function load_product_range_images() {
  $.post({
    url: rangeImgesURL,
    data: { product_range_id: rangeId },
    success: function (response) {
      $(".product_range_images").html(response);
      set_range_image_buttons();
    },
    error: function () {
      api_error();
    },
  });
}

function set_product_image_buttons() {
  $(".product_images .move_image_left")
    .unbind("click")
    .click(function () {
      var image_id = $(this).data("image-id");
      var product_id = $(this).data("product-id");
      var image_order = get_product_image_order(product_id);
      var current_index = image_order.indexOf(image_id);
      arraymove(image_order, current_index, current_index - 1);
      update_product_image_order(product_id, image_order);
    });

  $(".product_images .move_image_right")
    .unbind("click")
    .click(function () {
      var image_id = $(this).data("image-id");
      var product_id = $(this).data("product-id");
      var image_order = get_product_image_order(product_id);
      var current_index = image_order.indexOf(image_id);
      arraymove(image_order, current_index, current_index + 1);
      update_product_image_order(product_id, image_order);
    });

  $(".product_images .delete_image")
    .unbind("click")
    .click(function () {
      var image_id = $(this).data("image-id");
      var product_id = $(this).data("product-id");
      console.log(image_id);
      delete_product_image(image_id, product_id);
    });
}

function set_range_image_buttons() {
  $(".product_range_images .move_image_left")
    .unbind("click")
    .click(function () {
      var image_id = $(this).data("image-id");
      var image_order = get_range_image_order();
      var current_index = image_order.indexOf(image_id);
      arraymove(image_order, current_index, current_index - 1);
      update_range_image_order(image_order);
    });

  $(".product_range_images .move_image_right")
    .unbind("click")
    .click(function () {
      var image_id = $(this).data("image-id");
      var image_order = get_range_image_order();
      var current_index = image_order.indexOf(image_id);
      arraymove(image_order, current_index, current_index + 1);
      update_range_image_order(image_order);
    });

  $(".product_range_images .delete_image")
    .unbind("click")
    .click(function () {
      var image_id = $(this).data("image-id");
      var product_id = $(this).data("product-id");
      console.log(image_id);
      delete_range_image(image_id, product_id);
    });
}

$(document).ready(function () {
  load_product_range_images();

  $(".product_images").each(function () {
    var product_id = $(this).data("product-id");
    load_product_images(product_id);
  });

  $("#select_none").click(function () {
    var checkboxes = $(".selected input:checkbox");
    checkboxes.prop("checked", false);
    $(".selected input:checkbox").change();
  });

  $("#select_all").click(function () {
    var checkboxes = $(".selected input:checkbox");
    checkboxes.prop("checked", true);
    $(".selected input:checkbox").change();
  });

  $(".selected input:checkbox").change(function () {
    var checked = $(".selected input:checked");
    var product_id_input = $("#" + productIdsFieldId);
    var product_ids = [];
    checked.each(function () {
      var product_id = this.id.split("_")[1];
      product_ids.push(product_id);
    });
    var image_field = $("#" + imagesFieldId);
    var image_field_label = $("label[for='" + imagesFieldId + "']");
    if (checked.length == 0) {
      image_field.attr("disabled", true);
      image_field_label.text("No Products Selected");
      image_field_label.addClass("disabled");
    } else {
      image_field.attr("disabled", false);
      image_field_label.removeClass("disabled");
      image_field_label.text("Add images to selected products");
    }
    product_id_input.val(JSON.stringify(product_ids));
  });

  $("#" + imagesFieldId).change(function () {
    $(this).closest("form").submit();
  });

  $("#range_images").change(function () {
    $(this).closest("form").submit();
  });

  $("input:checkbox").change(function () {
    var row = $(this).closest("tr");
    if ($(this).is(":checked")) {
      row.addClass("selected");
    } else {
      row.removeClass("selected");
    }
  });

  $(".selected input:checkbox").change();
});
