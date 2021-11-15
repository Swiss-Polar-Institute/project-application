function checkSelector(selectorId) {
    let selector_matched = $(selectorId).length;

    if (selector_matched === 0) {
        alert('Error: selector "' + selectorId + '" did not find any object');
    } else if (selector_matched > 1) {
        alert('Error: selector "' + selectorId + '" matched more than one element');
    }
}

function setupOrcidLookupForFields(orcidFieldSelector, firstNameSelector, surnameSelector, buttonSelector, iconSelector) {
    checkSelector(buttonSelector);
    checkSelector(iconSelector);
    checkSelector(orcidFieldSelector);
    checkSelector(firstNameSelector);
    checkSelector(surnameSelector);

    let typingTimer;

    const INITIAL_ICON_CLASS = $(iconSelector).attr('class');  // It assumes that all the ORCID iD icons are the same,
    // (this function is used for different of them and stores
    // the first attr)
    const INITIAL_ICON_STYLE = $(iconSelector).attr('style');

    let startLookup = function () {
        function success(orcidRecord) {
            // In Orcid the family name can be none
            // For now it fills in N/A but perhaps in the future it should say
            // amend Orcid? Or allow in the database that familyName can be NULL
            let familyName = 'N/A';
            let orcidRecordFamilyName = orcidRecord['person']['name']['family-name'];
            if (orcidRecordFamilyName) {
                familyName = orcidRecordFamilyName.value;
            }

            let givenNames = orcidRecord['person']['name']['given-names'].value;

            $(firstNameSelector).val(givenNames);
            $(surnameSelector).val(familyName);

            $(iconSelector).attr('class', 'fas fa-check');
            $(iconSelector).attr('style', INITIAL_ICON_STYLE);
        }

        function error() {
            $(iconSelector).attr('class', 'fas fa-exclamation');
            $(iconSelector).attr('style', 'color:#ff0000');
        }

        // let orcid_id = $('#id_' + formPrefix + '-' + orcidFieldName + '.textinput.textInput.form-control').val();
        let orcidId = $(orcidFieldSelector).val();
        getOrcid(orcidId, success, error);
        $(iconSelector).attr('class', 'fas fa-spinner fa-spin');
    };

    $(buttonSelector).click(startLookup);

    $(orcidFieldSelector).on('input', function () {
        let doneTyping = function () {
            let orcidId = $(orcidFieldSelector).val();

            if (orcidId === '') {
                $(iconSelector).attr('class', INITIAL_ICON_CLASS);
                $(iconSelector).attr('style', INITIAL_ICON_STYLE);
            } else {
                startLookup();
            }
        };
        clearTimeout(typingTimer);

        $(firstNameSelector).val('');
        $(surnameSelector).val('');
        $(iconSelector).attr('class', INITIAL_ICON_CLASS);
        $(iconSelector).attr('style', INITIAL_ICON_STYLE);

        typingTimer = setTimeout(doneTyping, 100);
    });
}

function setupOrcidLookupForForm(formPrefix, orcidFieldName, firstNameFieldName, surnameFieldName) {
    let orcidFieldSelector = '#id_' + formPrefix + '-' + orcidFieldName;

    let buttonSelector = "#div_id_" + formPrefix + "-" + orcidFieldName + " .input-group-append";
    let iconSelector = buttonSelector + " .input-group-text i";

    let firstNameSelector = '#id_' + formPrefix + '-' + firstNameFieldName;
    let surnameSelector = '#id_' + formPrefix + '-' + surnameFieldName;

    setupOrcidLookupForFields(orcidFieldSelector, firstNameSelector, surnameSelector, buttonSelector, iconSelector);
}

function getOrcid(orcidId, successFunction, errorFunction) {
    $.ajax({
        url: "https://pub.orcid.org/v3.0/" + orcidId,
        type: "GET",
        dataType: "JSON",
        beforeSend: setHeader,
        success: successFunction,
        error: errorFunction
    });

    function setHeader(request) {
        request.setRequestHeader('Accept', 'application/json');
    }
}
