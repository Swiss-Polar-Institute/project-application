$(document).ready(function () {
    var current_fs, next_fs, previous_fs; // fieldsets
    var opacity;
    var current = 1;
    var steps = $("fieldset").length;

    function addValidation() {
        var errorMessages = []; // Array to store error messages

        // Check each required field
        $("input[name='proposal_application_form-title'], input[name='person_form-orcid'], input[name='person_form-first_name'], input[name='person_form-surname'], select[name='person_form-academic_title'], select[name='person_form-gender'], input[name='person_form-career_stage'], input[name='person_form-email'], input[name='person_form-phone'], select[name='person_form-organisation_names'], input[name='postal_address_form-address'], input[name='postal_address_form-city'], input[name='postal_address_form-postcode'], input[name='postal_address_form-country'], input[name='proposal_application_form-title'], input[name='proposal_application_form-start_date'], input[name='proposal_application_form-end_date'], input[name='proposal_application_form-duration_months'], input[name='data_collection_form-privacy_policy']").each(function() {
            if ($(this).val() === '') {
                var label = getLabelText($(this));
                errorMessages.push(label + ' is required.');
            }
        });

        // Display error messages
        if (errorMessages.length > 0) {
            var errorMessageHtml = '<ul>';
            errorMessages.forEach(function(message) {
                errorMessageHtml += '<li>' + message + '</li>';
            });
            errorMessageHtml += '</ul>';

            // Display error messages in a div
            $('#error-messages').html(errorMessageHtml).css('display', 'block');;
            $('html, body').animate({ scrollTop: 0 }, 'slow');
        } else {
            // Clear error messages if there are none
            $('#error-messages').html('');
        }
    }

    function storeFormData() {
        $("fieldset:visible :input").each(function () {
            var input = $(this);
            var name = input.attr('name');
            if (name) {
                var label = $("label[for='" + name + "']").text() || input.closest('.form-group').find('label').first().text();
                if (label) {
                    localStorage.setItem(name + '_label', label);
                }
                if (input.is('select')) {
                    var selectedOptionText = input.find('option:selected').text();
                    localStorage.setItem(name, selectedOptionText);
                } else if (input.is(':checkbox') || input.is(':radio')) {
                    if (input.is(':checked')) {
                        localStorage.setItem(name, input.val());
                        localStorage.setItem(name + '_checked', 'true');
                    } else {
                        localStorage.setItem(name + '_checked', 'false');
                    }
                } else {
                    localStorage.setItem(name, input.val());
                }
            }
        });
    }

    function retrieveFormData() {
        $("fieldset:visible :input").each(function () {
            var input = $(this);
            var name = input.attr('name');
            if (name) {
                var value = localStorage.getItem(name);
                if (value) {
                    if (input.is('select')) {
                        input.find('option').each(function () {
                            if ($(this).text() === value) {
                                $(this).prop('selected', true);
                            }
                        });
                    } else if (input.is(':checkbox') || input.is(':radio')) {
                        input.prop('checked', localStorage.getItem(name + '_checked') === 'true');
                    } else {
                        input.val(value);
                    }
                }
            }
        });
    }

    function populateSummary() {
        var summaryHtml = '';
        for (var i = 0; i < localStorage.length; i++) {
            var key = localStorage.key(i);
            if (key.endsWith('_label')) {
                var fieldName = key.replace('_label', '');
                var label = localStorage.getItem(key);
                var value = localStorage.getItem(fieldName);
                if (value) {
                    if ($(":input[name='" + fieldName + "']").is(':checkbox') || $(":input[name='" + fieldName + "']").is(':radio')) {
                        if (localStorage.getItem(fieldName + '_checked') === 'true') {
                            summaryHtml += '<p><strong>' + label + ':</strong> ' + value + '</p>';
                        }
                    } else {
                        summaryHtml += '<p><strong>' + label + ':</strong> ' + value + '</p>';
                    }
                }
            }
        }
        $('#summary-content').html(summaryHtml);
    }

    function validateOrcid(orcid) {
        var orcidRegex = /^(\d{4}-){3}\d{4}$/;
        return orcidRegex.test(orcid) && orcid !== "0000-0002-1825-0097";
    }

    function clearValidationErrors() {
        $(".is-invalid").removeClass("is-invalid");
        $(".invalid-feedback").remove();
    }

    function showValidationError(input, message) {
        input.addClass("is-invalid");
        input.after('<div class="invalid-feedback">' + message + '</div>');
    }

    function getLabelText(input) {
        var name = input.attr('name');
        var label = $("label[for='" + name + "']").text() || input.closest('.form-group').find('label').first().text();
        return label;
    }

    function validateCurrentFieldset() {
        current_fs = $(".next:visible").closest('fieldset');
        next_fs = $(".next:visible").closest('fieldset').next();
        var isValid = true;
        clearValidationErrors();

        current_fs.find(":input[required]").each(function () {
            if (!this.checkValidity()) {
                isValid = false;
                var label = getLabelText($(this));
                showValidationError($(this), label + ' is required.');
            }
        });

        // ORCID specific validation
        var orcidInput = current_fs.find("input[name='person_form-orcid']");
        if (orcidInput.length) {
            var orcidValue = orcidInput.val();
            if (!validateOrcid(orcidValue)) {
                isValid = false;
                var label = getLabelText(orcidInput);
                showValidationError(orcidInput, 'Invalid ' + label + '. The ORCID 0000-0002-1825-0097 is not allowed.');
            }
        }

        // Keywords validation
        var keywordsInput = current_fs.find("select[name='proposal_application_form-keywords']");
        if (keywordsInput.length) {
            var selectedKeywords = keywordsInput.find("option:selected");
            if (selectedKeywords.length < 5) {
                isValid = false;
                var label = getLabelText(keywordsInput);
                showValidationError(keywordsInput, 'Please enter at least 5 ' + label + '.');
            }
        }

        // Geographical areas validation
        var geographicalAreas = current_fs.find("input[name='proposal_application_form-geographical_areas']");
        if (geographicalAreas.length && geographicalAreas.filter(':checked').length === 0) {
            isValid = false;
            var label = getLabelText(geographicalAreas.first());
            showValidationError(geographicalAreas.first(), 'At least one ' + label + ' must be selected.');
        }

        return isValid;
    }

    function checkDuplicateProposal(callback) {
        var proposalTitle = $("input[name='proposal_title']").val();
        var applicantId = $("input[name='applicant_id']").val();
        var callId = $("input[name='call_id']").val();

        $.ajax({
            url: '/check_duplicate_proposal/',  // URL to check for duplicates
            data: {
                'proposal_title': proposalTitle,
                'applicant_id': applicantId,
                'call_id': callId
            },
            success: function (data) {
                if (data.exists) {
                    var proposalTitleInput = $("input[name='proposal_title']");
                    var label = getLabelText(proposalTitleInput);
                    showValidationError(proposalTitleInput, 'A proposal with this ' + label + ' already exists.');
                    callback(false);
                } else {
                    callback(true);
                }
            },
            error: function () {
                alert('Error checking for duplicate proposals.');
                callback(false);
            }
        });
    }

    retrieveFormData();

    $(".next").click(function () {
        current_fs = $(this).closest('fieldset');
        next_fs = $(this).closest('fieldset').next();

        next_fs.show();

        current_fs.animate({
            opacity: 0
        }, {
            step: function (now) {
                opacity = 1 - now;
                current_fs.css({
                    'display': 'none',
                    'position': 'relative'
                });
                next_fs.css({
                    'opacity': opacity
                });
            },
            duration: 500,
            complete: function () {
                if ($("fieldset").index(next_fs) === steps - 1) {
                    populateSummary();
                }
            }
        });
    });

    $(".previous").click(function () {
        current_fs = $(this).closest('fieldset');
        previous_fs = $(this).closest('fieldset').prev();

        previous_fs.show();

        retrieveFormData();

        current_fs.animate({
            opacity: 0
        }, {
            step: function (now) {
                opacity = 1 - now;
                current_fs.css({
                    'display': 'none',
                    'position': 'relative'
                });
                previous_fs.css({
                    'opacity': opacity
                });
            },
            duration: 500
        });
    });

    $(document).on('click', '.submit_btn', function (e) {
        e.preventDefault();
        addValidation(); // Call addValidation directly

        if ($('#error-messages').html().trim() !== '') {
            // If there are error messages, return without submitting the form
            return;
        }

        // If no errors, proceed with form submission
        storeFormData();
        $("form#dd-form").submit();
        $("#final-result").click();
    });
});
