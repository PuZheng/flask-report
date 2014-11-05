$(function () {
    $('input[type="search"]').keyup(function (e) {
        var needle = $(this).val().trim();

        if (!needle) {
            $('ul.list-group li').show();
            $('.right-inner-addon .fa-remove').hide();
            $('.right-inner-addon .fa-search').show();
        } else {
            $('.right-inner-addon .fa-remove').show();
            $('.right-inner-addon .fa-search').hide();
        }

        $('ul.list-group li').each(function (i) {
            if ($(this).data('name').indexOf(needle) == -1) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    });

    $('.right-inner-addon .fa-remove').click(function (e) {
        $('input[type="search"]').val('').keyup();
    })
});
