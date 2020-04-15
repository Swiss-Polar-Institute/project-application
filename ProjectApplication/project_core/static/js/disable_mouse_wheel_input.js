/** By default browsers allow to change the date using the mouse wheel
 * on a disabled date time widget. We wanted to disable this behaviour.
 *
 * But then we thought that using the mouse wheel to scroll could change
 * the date time of enabled input widgets or even for the type=number
 * input widgets. Here we are disabling the mousewheel action for
 * these widgets.
 *
 * It's a bit of a strange way to do: if there is a mouse wheel action it
 * blurs (focus out) the widget so the page scroll happens. This seems to
 * cause no problems.
 *
 * Another solution was to disable the mouse wheel on the widget disabling
 * the default action. This caused that the mouse wheel could not be used
 * to scroll the page if the mouse cursor was on an input widget.
 */

$(document).ready(function () {
    $(':input[type=number]').on('mousewheel', function (e) {
        $(this).blur();
    });

    // $('.xdsoftyearmonthpickerinput').on('mousewheel', function (e) {
    //     $(this).blur();
    // });
    // console.log('document ready 3');
    // $('.xdsoftyearmonthdaypickerinput').on('mousewheel', function (e) {
    //     $(this).blur();
    // });
    // console.log('document ready 4');
    // $('.xdsoftyearmonthdayhourminutepickerinput').on('mousewheel', function (e) {
    //     $(this).blur();
    // });
});
