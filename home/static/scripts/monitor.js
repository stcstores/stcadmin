auto_toggle = true;
current = '';

function get_pack_count() {
    $('.pack_count').html('');
    $('.feedback').html('');
    $.get(pack_count_URL,
        function (response) {
            $('.pack_count').html(response);
            current = 'pack_count'
        }
    );
}

function get_feedback() {
    $('.pack_count').html('');
    $('.feedback').html('');
    $.get(feedback_URL,
        function (response) {
            $('.feedback').html(response);
            current = 'feedback'
        }
    );
}


function toggle() {
    if (current == 'pack_count') {
        get_feedback();
    } else {
        get_pack_count();
    }
}

if (auto_toggle) {
    setInterval(function () {
        if ($('.auto_toggle').is(':checked')) {
            toggle();
        }
    }, 1000 * 30);
}

$(document).ready(function () {
    get_pack_count();
    $('.toggle').click(function () {
        toggle();
    });
});