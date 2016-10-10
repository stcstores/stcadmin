function get_guid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}

var LabelForm = function(parent, settings) {
    var self = {

    };
    $.each(settings, function(index, field) {
        var div = $('<div class="form_section" id="list_' + field + '" ></div>');
        div.append($('<p class="form_section_header">' + field + '</p>'));
        parent.append(div);
        self[field] = MakeList(div, field);
    });


    return self;
};

var MakeList = function(parent, name) {
    var div = $('<div>', {"class": 'listinput'});
    parent.append(div);

    var self = {
        inputs: {},
        update: function() {
            $.each(self.inputs, function(index, input) {
                var input_value = input.get_value();
                console.log(input_value);
                if (input_value.length < 1) {
                    console.log('REMOVE');
                    input.remove();
                }
            });
            self.add();
        },
        add: function() {
            var guid = get_guid();
            var new_input = ListInput(div);
            new_input.guid = guid;
            self.inputs[guid] =  new_input;
            new_input.list = self;
            new_input.input.focus();
            return new_input;
        },
        get_list: function() {
            var values = [];
            $.each(self.inputs, function(index, input) {
                value = input.input.val();
                if ((input.input.val().length > 0) && ($.inArray(value, values))) {
                    values.push(value);
                }
            });
            return values;
        }
    };

    self.add();
    return self;
};

var ListInput = function(parent) {
    var div = $('<div class="list_input"></div>');
    var input = $('<input type="text">');
    parent.append(div);
    div.append(input);
    var remove_button = $('<button>X</button>');
    div.append(remove_button);
    var self = {
        div: div,
        input: input,
        remove_button: remove_button,
        get_value: function(){
            return self.input.val();
        }
    };

    remove_button.click(function() {
        self.remove();
        self.list.update();
    });

    self.remove = function(){
        console.log('Remove');
        self.div.detach();
        self.div.css('background', 'red');
        input.remove();
        remove_button.remove();
        delete self.list.inputs[self.guid];
    };

    input.change(function() {
        if (input.val().length > 0) {
            self.list.update();
        }
    });
    return self;
};

var LabelSelectionTable = function(parent, data, form) {
    parent.html('');
    var self = {
        parent: parent,
        data: data,
        sizes: data.sizes,
        colours: data.colours,
        table: $('<table id="label_selection_table" class="label_selection_table"></table>'),
    };

    self.thead = $('<thead></thead>');
    self.tbody = $('<tbody></tbody>');
    self.table.append(self.thead);
    self.table.append(self.tbody);
    self.thead.append('<tr><th>Size</th><th>Colour</th><th>Quantity</th><tr>');

    $.each(self.sizes, function(index, size) {
        var size_reference = size[0];
        var size_name = size[1];
        $.each(self.colours, function(index, colour) {
            self.tbody.append('<tr><td class="hidden">' + size_reference + '</td><td>' + size_name + '</td><td>' + colour + '</td><td><input type="number" value="0" /></td></tr>');
        });
    });
    parent.append(self.table);
    generate_labels_button = $('<button id="generate_labels_button">Generate labels</button>');
    generate_labels_button.click(function() {
        var data = [];
        var rows = self.tbody.find('tr');
        rows.each(function() {
            data.push({
                'size': $(this).find('td').eq(0).text().replace('UK: ', ''),
                'colour': $(this).find('td').eq(2).text(),
                'quantity': $(this).find('input[type=number]').val()
            });

        });
        console.log(data);
        var input = form.find('#data');
        input.val(JSON.stringify(data));
        $('#product_code').clone().appendTo(form);
        form.submit();
    });
    parent.append(generate_labels_button);
};
