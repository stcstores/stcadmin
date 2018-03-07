$(document).ready(function() {
    // Colour fields.
    $('.new_product input, .new_product select, .new_product textarea').each(function(){
        var label = $('label[for="'+$(this).attr('id')+'"]');
        var row = $(this).closest('tr');
        if ($(this).prop('required')) {
            label.text(label.text().replace(':', '*:'));
            row.css('background', '#DDD');
        } else if ($(this).prop('name').startsWith('opt_')) {
            row.css('background', '#e2edff');
        } else {
            label.css('color', '#555');
        }
    });

    // Prevent enter key submitting form.
    $(".new_product").keypress(function(e){
        var no_enter = true;
        if (e.which == 13) {
            if ($(e.target).prop('type') == 'password') {
                no_enter = false;
            }
            if ($(e.target).is('textarea')) {
                no_enter = false;
            }
            if (no_enter) {
                return false;
            }
       }
    });

    // Prevent the backspace key from navigating back.
    $(document).unbind('keydown').bind('keydown', function (event) {
        var doPrevent = false;
        if (event.keyCode === 8) {
            var d = event.srcElement || event.target;
            if ((d.tagName.toUpperCase() === 'INPUT' &&
                 (
                     d.type.toUpperCase() === 'TEXT' ||
                     d.type.toUpperCase() === 'PASSWORD' ||
                     d.type.toUpperCase() === 'FILE' ||
                     d.type.toUpperCase() === 'SEARCH' ||
                     d.type.toUpperCase() === 'EMAIL' ||
                     d.type.toUpperCase() === 'NUMBER' ||
                     d.type.toUpperCase() === 'DATE' )
                 ) ||
                 d.tagName.toUpperCase() === 'TEXTAREA') {
                doPrevent = d.readOnly || d.disabled;
            }
            else {
                doPrevent = true;
            }
        }

        if (doPrevent) {
            event.preventDefault();
        }
    });
});
