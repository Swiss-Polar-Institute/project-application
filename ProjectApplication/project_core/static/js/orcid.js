function setup_orcid_lookup(form_prefix, orcid_field, first_name_field, surname_field) {
    let selector = "#div_id_" + form_prefix + "-" + orcid_field + " .input-group-append"

    $(selector).click(function () {
        function success(orcid_record) {
            let family_name = orcid_record['person']['name']['family-name'].value;
            let given_names = orcid_record['person']['name']['given-names'].value;

            $('#id_' + form_prefix + '-' + first_name_field).val(given_names);
            $('#id_' + form_prefix + '-' + surname_field).val(family_name);
        }

        function error() {
            alert('Error getting orcid id information');
        }

        let orcid_id = $('#id_' + form_prefix + '-' + orcid_field + '.textinput.textInput.form-control').val()
        getOrcid(orcid_id, success, error);
    });

    $('#id_' + form_prefix + '-' + orcid_field).on('input', function () {
        $('#id_' + form_prefix + '-' + first_name_field).val("");
        $('#id_' + form_prefix + '-' + surname_field).val("");
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
