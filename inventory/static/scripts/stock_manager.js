var getting_stock_level_icon = '<div class="spinner-border spinner-border-sm"><span class="sr-only"></span></div>';
var setting_stock_level_icon = '<div class="spinner-border spinner-border-sm text-warning"><span class="sr-only"></span></div>';;
var get_stock_level_success_icon = '<i class="bi bi-check text-muted"></i>';
var set_stock_level_success_icon = '<i class="bi bi-check text-success"></i>';
var get_stock_level_error_icon = '<i class="bi bi-exclamation-triangle-fill text-warning"></i>';
var set_stock_level_error_icon = '<i class="bi bi-exclamation-triangle-fill text-danger"></i>';

var refresh_icon_available = '<i class="bi bi-arrow-clockwise"></i>';
var refresh_icon_in_progress = '<div class="spinner-border spinner-border-sm"><span class="sr-only"></span></div>';;
var refresh_icon_locked = '<i class="bi bi-arrow-clockwise text-muted"></i>';

class StockLevelWidget {
  constructor(product_id) {
    this.product_id = product_id;
    this.stock_level_field = $("#available_stock_" + product_id);
    this.in_orders_field = $("#in_orders_" + product_id);
    this.status_icon = $("#stock_level_status_" + product_id);
    this.update_button = $("#stock_level_update_button_" + product_id);
    this.refresh_button = $("#refresh_button_" + product_id);
    this.stock_level_field.focus(function () {
      $(this).select();
    });
    this.stock_level_field.on("input", () => this.enable_update_button());
    this.update_button.on("click", () => this.update_stock_level());
  }

  refresh() {
    this.write_stock_level("");
    this.write_in_orders("");
    this.set_status_icon(getting_stock_level_icon);
    this.set_refresh_in_progress();
    stock_level_widget_manager.get_stock_level(this.product_id);
  }

  write_stock_level(stock_level) {
    this.stock_level_field.val(stock_level);
  }

  write_in_orders(stock_level) {
    this.in_orders_field.text(stock_level);
  }

  set_error_getting_stock_level() {
    this.write_stock_level("");
    this.write_in_orders("");
    this.set_status_icon(get_stock_level_error_icon);
  }

  update_stock_level() {
    var new_stock_level = this.stock_level_field.val();
    this.disable_update_field();
    this.set_refresh_locked();
    this.disable_update_button();
    this.set_status_icon(getting_stock_level_icon);
    stock_level_widget_manager.update_stock_level(
      this.product_id,
      new_stock_level
    );
  }

  display_updated_stock_level(new_stock_level) {
    this.write_stock_level(new_stock_level);
    this.set_status_icon(set_stock_level_success_icon);
    this.set_refresh_available();
    this.set_refresh_available();
    this.enable_update_field();
    this.stock_level_field.trigger("stockLevelChange", [
      this.product_id,
      new_stock_level,
    ]);
  }

  display_stock_level_update_error() {
    this.write_stock_level("");
    this.write_in_orders("");
    this.set_status_icon(set_stock_level_error_icon);
    this.set_refresh_available();
  }

  display_loaded_stock_level(stock_level_info) {
    this.write_stock_level(stock_level_info["available"]);
    this.write_in_orders(stock_level_info["in_orders"]);
    this.set_status_icon(get_stock_level_success_icon);
    this.enable_update_field();
    this.set_refresh_available();
    this.stock_level_field.trigger("stockLevelChange", [
      this.product_id,
      stock_level_info["available"],
    ]);
  }

  set_status_icon(icon_css) {
    this.status_icon.html(icon_css);
  }

  disable_update_button() {
    this.update_button.attr("disabled", true);
  }

  enable_update_button() {
    this.update_button.attr("disabled", false);
  }

  disable_update_field() {
    this.stock_level_field.attr("disabled", true);
  }

  enable_update_field() {
    if (!this.stock_level_field.is("[readonly]")) {
      this.stock_level_field.attr("disabled", false);
    }
  }

  set_refresh_available() {
    this.refresh_button.html(refresh_icon_available);
    this.refresh_button.on("click", () => this.refresh());
  }

  set_refresh_in_progress() {
    this.refresh_button.html(refresh_icon_in_progress);
    this.refresh_button.off("click");
  }

  set_refresh_locked() {
    this.refresh_button.html(refresh_icon_locked);
    this.refresh_button.off("click");
  }
}

let stock_level_widget_manager = {
  widgets: {},

  add_widget(widget) {
    this.widgets[widget.product_id] = widget;
  },

  get_stock_levels() {
    var product_ids = [];
    $.each(this.widgets, function (product_id, widget) {
      product_ids.push(product_id);
    });
    $.ajax({
      type: "POST",
      url: get_stock_url,
      data: JSON.stringify({ product_ids: product_ids }),
      success: function (response) {
        $.each(response, function (product_id, stock_level_info) {
          var widget = stock_level_widget_manager.widgets[product_id];
          widget.display_loaded_stock_level(stock_level_info);
        });
      },
      error: function (response) {
        $.each(
          stock_level_widget_manager.widgets,
          function (product_id, widget) {
            widget.set_error_getting_stock_level();
          }
        );
      },
      contentType: "application/json",
      dataType: "json",
    });
  },

  get_stock_level(product_id) {
    var widget = stock_level_widget_manager.widgets[product_id];
    $.ajax({
      type: "POST",
      url: get_stock_url,
      data: JSON.stringify({ product_ids: [product_id] }),
      success: function (response) {
        $.each(response, function (product_id, stock_level_info) {
          widget.display_loaded_stock_level(stock_level_info);
        });
      },
      error: function (response) {
        widget.set_error_getting_stock_level();
      },
      contentType: "application/json",
      dataType: "json",
    });
  },

  update_stock_level(product_id, new_stock_level) {
    request_data = {
      stock_updates: [
        {
          product_id: product_id,
          new_stock_level: new_stock_level,
        },
      ],
    };
    $.ajax({
      type: "POST",
      url: update_stock_url,
      data: JSON.stringify(request_data),
      success: function (response) {
        var new_stock_level = response[product_id];
        var widget = stock_level_widget_manager.widgets[product_id];
        widget.display_updated_stock_level(new_stock_level);
      },
      error: function () {
        var widget = stock_level_widget_manager.widgets[product_id];
        widget.display_stock_level_update_error();
      },
      contentType: "application/json",
      dataType: "json",
    });
  },
};

$(document).ready(function () {
  if (!$.isEmptyObject(stock_level_widget_manager.widgets)) {
    stock_level_widget_manager.get_stock_levels();
  }
});
