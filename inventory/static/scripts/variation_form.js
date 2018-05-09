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
      $('.field_select').removeClass('selected');
      field_selector.addClass('selected');
      var name = field_selector.attr('id');
      var target = $('.' + name.replace('hide_', ''));
      $('.field_cell').prop('hidden', true);
      target.prop('hidden', false);
  }

  $(document).ready(function() {
      $('.field_cell').prop('hidden', true);
      $('.field_select').click(function() {
          hide_field($(this));
      });

      $('#copybutton').click(function() {
          $('.product').each(function() {
              product_row_copy($(this));
          });
      });

  });
