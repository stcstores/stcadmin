function changeField() {
  $(".field").prop("hidden", true);
  $(".field_select").removeClass("active");
  $(this).addClass("active");
  $(".field_" + $(this).data("target")).prop("hidden", false);
}

function selectAll() {
  $(".product_select").prop("checked", true);
}

function selectNone() {
  $(".product_select").prop("checked", false);
}

function selectByOption() {
  var option = $(this).data("option");
  var value = $(this).data("value");
  toggleOptionSelection(
    $(".product_select[data-" + option + '="' + value + '"]')
  );
}

function copyInput(source, target) {
  if (source.is("select")) {
    var option = source.find("option:selected");
    var value = option.val();
    var text = option.text();
    if (target.find("option[value='" + value + "']").length) {
      target.val(value).trigger("change");
    } else {
      var newOption = new Option(text, value, true, true);
      target.append(newOption).trigger("change");
    }
  } else {
    target.val(source.val());
  }
}

function copyButton() {
  var fieldName = $(this).data("target");
  var source = $(".copyfield.field_" + fieldName).find("input, select");
  $(".product").each(function () {
    if ($(this).find($(".product_select")).prop("checked")) {
      var target = $(this)
        .find(".input_" + fieldName)
        .find("input, select");
      copyInput(source, target);
    }
  });
}

function toggleOptionSelection(checkboxes) {
  var allChecked = true;
  checkboxes.each(function () {
    if (!$(this).prop("checked")) {
      allChecked = false;
    }
  });

  if (allChecked) {
    checkboxes.prop("checked", false);
  } else {
    checkboxes.prop("checked", true);
  }
}

$(document).ready(function () {
  $(".field").prop("hidden", true);
  $(".field_select").click(changeField);
  $(".select_option").click(selectByOption);
  $(".copybutton").click(copyButton);
  $(".field_select:first").click();
});
