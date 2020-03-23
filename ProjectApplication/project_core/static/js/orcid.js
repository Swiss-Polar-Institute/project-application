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
        let family_name = orcid_record['person']['name']['family-name'].value;
        let given_names = orcid_record['person']['name']['given-names'].value;
        alert('orcid success: ' + given_names + " " + family_name);
    }

    function orcid_error() {
        alert('orcid failure');
    }

    function setHeader(request) {
        request.setRequestHeader('Accept', 'application/json');
    }
}
