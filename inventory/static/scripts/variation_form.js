function product_row_copy(row) {
      if (row.find('.copy_checkbox').is(':checked')) {
          row.find('.field_cell:visible').each(function() {
              cell_copy($(this));
          });
      }
  }

  function cell_copy(target_cell) {
      var copy_inputs = $('.copyrow .field_cell:visible').find('input, select');
      var target_inputs = target_cell.find('input, select');
      for (var i=0; i<target_inputs.length; i++) {
          copy_input = copy_inputs.eq(i);
          target_input = target_inputs.eq(i);
          input_copy(copy_input, target_input);
      }
  }

  function input_copy(copy_input, target_input) {
      if ((copy_input[0].hasOwnProperty('selectize')) && (target_input[0].hasOwnProperty('selectize'))) {
          var copy_value = copy_input[0].selectize.getValue();
          target_input[0].selectize.setValue(copy_value);
      } else {
          target_input.val(copy_input.val());
      }
  }

  function hide_field(field_selector) {
      $('.field_select').removeClass('active');
      field_selector.addClass('active');
      var name = field_selector.attr('id');
      var target = $('.' + name.replace('hide_', ''));
      $('.field_cell').prop('hidden', true);
      target.prop('hidden', false);
  }

  function select_all() {
    $('.copy_checkbox').prop('checked', true);
  }

  function select_none() {
    $('.copy_checkbox').prop('checked', false);
  }

  function select_products(option, value) {
    var column_headers = $('.variation_table').find('tr').eq(0).find('th');
    var checkboxes = [];
    column_headers.each(function() {
      if ($(this).text() == option) {
        var column_number = $(this).index();
        $('.variation_table tr').each(function() {
          header = $(this).children().eq(column_number);
          if (header.text() == value) {
            checkboxes.push($(this).find('.copy_checkbox'));
          }
        });
      }
    });
    toggle_selection(checkboxes);
  }

  function toggle_selection(checkboxes) {
    var checked = [];
    for (var i=0; i<checkboxes.length; i++) {
      if (checkboxes[i].prop('checked')) {
        checked.push(checkboxes[i]);
      }
    }
    if (checked.length == checkboxes.length) {
      for (var i=0; i<checkboxes.length; i++) {
        checkboxes[i].prop('checked', false);
      }
    } else {
      for (var i=0; i<checkboxes.length; i++) {
        checkboxes[i].prop('checked', true);
      }
    }
  }

  $(document).ready(function() {
      $('.field_cell').prop('hidden', true);
      $('.field_select').click(function() {
        $('.field_select').removeClass('selected');
        $(this).addClass('selected');
          hide_field($(this));
      });

      $('#copybutton').click(function() {
          $('.product').each(function() {
              product_row_copy($(this));
          });
      });

      $('#select_all').click(function() {select_all()});
      $('#select_none').click(function() {select_none()});

      $('.select_option').click(function() {
        var value = $(this).data('value');
        var option = $(this).data('option');
        select_products(option, value);
      });

  });
