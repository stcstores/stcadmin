$(document).ready(function() {

    var csrftoken = $.cookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    function add_product_to_table(product) {
        var row = "<tr><td>" + product['sku'] + "</td><td>" + product['name'] + "</td>";
        $('#stock_search_result').append(row);
    }

    $('#stock_search_button').click(function() {
        var search_text = $('#stock_search').val();
        var url = search_url.replace('search_text', search_text);
        $.post(url, function(response) {
            var products = JSON.parse(response);
            for (var i = 0; i < products.length; i++) {
                console.log(i);
                add_product_to_table(products[i]);
            }
        });
    });
});
