closed_arrow = "&#9658;";
open_arrow = "&#9660;";
show_urgent = true;
show_priority = true;
show_non_priority = true;

function show_orders(type_name) {
    $('#' + type_name + '_ids').show();
    $('#' + type_name + '_toggle').html(open_arrow);
}

function hide_orders(type_name) {
    $('#' + type_name + '_ids').hide();
    $('#' + type_name + '_toggle').html(closed_arrow);
}

function toggle_urgent() {
    if (show_urgent === true) {
        show_urgent = false;
        hide_orders('urgent');
    } else {
        show_urgent = true;
        show_orders('urgent');
    }
}

function toggle_priority() {
    if (show_priority === true) {
        show_priority = false;
        hide_orders('priority');
    } else {
        show_priority = true;
        show_orders('priority');
    }
}

function toggle_non_priority() {
    if (show_non_priority === true) {
        show_non_priority = false;
        hide_orders('non_priority');
    } else {
        show_non_priority = true;
        show_orders('non_priority');
    }
}

function setup_order_ids() {
    hide_orders('urgent');
    hide_orders('priority');
    hide_orders('non_priority');
    show_urgent = false;
    show_priority = false;
    show_non_priority = false;
    $('#urgent_count').click(function () {
        toggle_urgent();
    });
    $('#priority_count').click(function () {
        toggle_priority();
    });
    $('#non_priority_count').click(function () {
        toggle_non_priority();
    });
}