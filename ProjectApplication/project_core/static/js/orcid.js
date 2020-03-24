function setup_orcid_lookup(form_prefix, orcid_field, first_name_field, surname_field) {
    let button_selector = "#div_id_" + form_prefix + "-" + orcid_field + " .input-group-append";
    let icon_selector = button_selector + " .input-group-text i";

    let orcid_field_selector = '#id_' + form_prefix + '-' + orcid_field;
    let first_name_selector = '#id_' + form_prefix + '-' + first_name_field;
    let surname_selector = '#id_' + form_prefix + '-' + surname_field;

    let typing_timer;

    const initial_icon_class = $(icon_selector).attr('class');  // It assumes that all the ORCID iD icons are the same,
                                                                // (this function is used for different of them and stores
                                                                // the first attr)
    const initial_icon_style = $(icon_selector).attr('style');

    let start_lookup = function () {
        function success(orcid_record) {
            let family_name = orcid_record['person']['name']['family-name'].value;
            let given_names = orcid_record['person']['name']['given-names'].value;

            $(first_name_selector).val(given_names);
            $(surname_selector).val(family_name);

            $(icon_selector).attr('class', 'fas fa-check');
            $(icon_selector).attr('style', initial_icon_style);
        }

        function error() {
            $(icon_selector).attr('class', 'fas fa-exclamation');
            $(icon_selector).attr('style', 'color:#ff0000');
        }

        // let orcid_id = $('#id_' + form_prefix + '-' + orcid_field + '.textinput.textInput.form-control').val();
        let orcid_id = $(orcid_field_selector).val();
        getOrcid(orcid_id, success, error);
        $(icon_selector).attr('class', 'fas fa-spinner fa-spin');
    };

    $(button_selector).click(start_lookup);

    $(orcid_field_selector).on('input', function () {
        let done_typing = function () {
            start_lookup();
        };
        clearTimeout(typing_timer);

        $(first_name_selector).val('');
        $(surname_selector).val('');
        $(icon_selector).attr('class', initial_icon_class);
        $(icon_selector).attr('style', initial_icon_style);

        typing_timer = setTimeout(done_typing, 1000);
    });
}

function getOrcid(orcid_id, success_function, error_function) {
    $.ajax({
        url: "https://pub.orcid.org/v3.0/" + orcid_id,
        type: "GET",
        dataType: "JSON",
        beforeSend: setHeader,
        success: success_function,
        error: error_function
    });

    function orcid_success(orcid_record) {
        // For debugging
        let family_name = orcid_record['person']['name']['family-name'].value;
        let given_names = orcid_record['person']['name']['given-names'].value;
        alert('orcid success: ' + given_names + " " + family_name);
    }

    function orcid_error() {
        // For debugging
        alert('orcid failure');
    }

    function setHeader(request) {
        request.setRequestHeader('Accept', 'application/json');
    }
}
