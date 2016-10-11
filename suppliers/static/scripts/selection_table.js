var SelectionTable = function(table) {

    var get_rows = function() {
        var rows = [];
        table.find('tbody tr').each(function() {
            rows.push(SelectionTableRow($(this)));
        });
        return rows;
    };

    var self = {
        rows: get_rows(),
        colour: function(colour) {
            table.css('background', colour);
        },
        text_colour: function(colour) {
            table.css('color', colour);
        },
        export: function() {
            data = {};
            $.each(self.rows, function(index, row) {
                if (row.selected()) {
                    data[row.item_id] = row.quantity.value();
                }
            });
            console.log(data);
            json = JSON.stringify(data);
            $('#json_field').val(json);
            $('#export_form').submit();
        }
    };
    $.each(self.rows, function(index, row) {
        row.table = self;
        row.checkbox.table = self;
        row.checkbox.row = row;
        row.product_code.table = self;
        row.product_code.row = row;
        row.supplier_title.table = self;
        row.supplier_title.row = row;
        row.notes.table = self;
        row.notes.row = row;
        row.linnworks_title.table = self;
        row.linnworks_title.row = row;
        row.box_quantity.table = self;
        row.box_quantity.row = row;
    });
    return self;
};

var SelectionTableRow = function(row) {

    var self = {
        update_url: row.find(".update_url").text(),
        reload_url: row.find(".reload_url").text(),
        delete_url: row.find(".delete_url").text(),
        checkbox: CheckboxField(row.find(".checkbox")),
        product_code: TextField(row.find(".product_code")),
        supplier_title: TextField(row.find(".supplier_title")),
        box_quantity: TextField(row.find(".box_quantity")),
        notes: TextField(row.find(".notes")),
        linnworks_title: TextField(row.find(".linnworks_title")),
        quantity: QuantityField(row.find(".quantity")),
        item_id: row.find(".pk").html(),
        delete_button: row.find('.delete_button'),
        colour: function(colour) {
            self.row.css('background', colour);
        },
        selected: function() {
            return self.checkbox.selected();
        },
        select: function() {
            self.checkbox.select();
        },
        deselect: function() {
            self.checkbox.deselect();
        },
        toggle: function() {
            self.checkbox.toggle();
        },
        reload: function() {
            $.post(self.reload_url, function(response) {
                var result = $.parseJSON(response);
                self.product_code.field.html(result.product_code);
                self.supplier_title.field.html(result.supplier_title);
                self.box_quantity.field.html(result.box_quantity);
                self.notes.field.html(result.notes);
                self.linnworks_title.field.html(result.linnworks_title);
            });
        },
        update: function() {
            $.post(
                self.update_url,
                {
                    'product_code': self.product_code.value(),
                    'supplier_title': self.supplier_title.value(),
                    'box_quantity': self.box_quantity.value(),
                    'notes': self.notes.value(),
                    'linnworks_title': self.linnworks_title.value(),
                }
            );
        }
    };
    self.delete_button.click(function() {
        $.post(self.delete_url);
        row.remove();
    });
    return self;
};

var CheckboxField = function(checkbox) {
    var self = {
        checkbox: checkbox,
        selected: function() {
            return self.checkbox.prop('checked');
        },
        select: function() {
            self.checkbox.prop('checked', true);
        },
        deselect: function() {
            self.checkbox.prop('checked', false);
        },
        toggle: function() {
            self.checkbox.prop('checked', !checkbox.prop('checked'));
        }
    };
    return self;
};

var QuantityField = function (field){
    var self = {
        input: field.find('input'),
        value: function() {
            return self.input.val();
        },
        clear: function() {
            self.input.val('0');
        }
    };
    return self;
};

var TextField = function(field) {
    var self = {
        field: field,
        input: null,
        colour: function(colour) {
            self.field.css('background', colour);
        },
        value: function() {
            if (self.input !== null) {
                return self.input.val();
            } else {
                return self.field.html();
            }
        },
        set_click: function() {
            field.bind('mouseup', function() {
                var value = self.value();
                self.disable_click();
                self.field.html('<input type="text" value="' + value + '">');
                self.input = self.field.find('input');
                self.input.focus();
                self.input.select();
                self.set_blur();
            });
        },
        disable_click: function() {
            self.field.unbind('mouseup');
        },
        set_blur: function() {
            self.input.bind('blur', function() {
                self.field.html(self.input.val());
                self.row.update();
                self.input = null;
                self.set_click();
            });
        }
    };

    self.set_click();

    return self;
};
