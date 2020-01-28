auto_advance = true;
current = '';

function get_pack_count() {
    $('.pack_count').html('');
    $('.feedback').html('');
    $('.undispatched').html('');
    $.get(pack_count_URL,
        function (response) {
            $('.pack_count').html(response);
            current = 'pack_count';
        }
    );
}

function get_feedback() {
    $('.pack_count').html('');
    $('.feedback').html('');
    $('.undispatched').html('');
    $.get(feedback_URL,
        function (response) {
            $('.feedback').html(response);
            current = 'feedback';
        }
    );
}

function get_undispatched() {
    $('.pack_count').html('');
    $('.feedback').html('');
    $('.undispatched').html('');
    $.get(undispatched_URL,
        function (response) {
            $('.undispatched').html(response);
            current = 'undispatched';
            setup_order_ids();
        }
    )
}


function advance() {
    if (current == 'pack_count') {
        get_feedback();
    } else if (current == 'feedback') {
        get_undispatched();
    } else if (current == 'undispatched') {
        get_pack_count();
    }
}

if (auto_advance) {
    setInterval(function () {
        if ($('.auto_advance').is(':checked')) {
            advance();
        }
    }, 1000 * 30);
}

$(document).ready(function () {
    get_pack_count();
    $('.next').click(function () {
        advance();
    });
});