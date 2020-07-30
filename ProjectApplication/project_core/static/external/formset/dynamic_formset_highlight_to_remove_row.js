function highlight_row_delete_link_hover(selector) {
    /* There are two types of jquery forms:
        a) Type "proposal partners": (vertical)
        b) Type "funding organisations" (horizontal)

        The first hover (parents('tr')) is needed for the funding organisations style,
        the second for the normal setup (proposal partners).

        If changes on this verify all the different formats.
     */
    $(selector).find('.delete-row').hover(
        function () {
            $(this).parents('tr').addClass('highlighted-to-remove');
        }, function () {
            $(this).parents('tr').removeClass('highlighted-to-remove');
        });

    $(selector).find('.delete-row').hover(
        function () {
            $(this).parent().addClass('highlighted-to-remove');
        }, function () {
            $(this).parent().removeClass('highlighted-to-remove');
        });
}
