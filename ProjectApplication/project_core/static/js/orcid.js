function getOrcid() {
    $.ajax({
        url: "https://pub.orcid.org/v3.0/0000-0003-3120-9475",
        type: "GET",
        dataType: "JSON",
        beforeSend: setHeader,
        success: orcid_success,
        error: orcid_error
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
