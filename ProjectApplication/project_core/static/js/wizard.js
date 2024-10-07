$(document).ready(function () {
    $('input.required_field, select.required_field, textarea.required_field').each(function () {
        var fieldId = $(this).attr('id');
        var label = $('label[for="' + fieldId + '"]');
        if (!label.text().includes('*')) {
            label.text(label.text().trim() + ' *');
        }
    });
    localStorage.clear();
    var current_fs, next_fs, previous_fs;
    var current = 1;
    var steps = $("fieldset").length;
    var errorMessages = [];
    $('#id_data_collection_form-privacy_policy').removeAttr('required');

    function validateBudgetItems(errorMessages) {
         var totalSum = 0;
        var max_budget = $('#total_budget').val();
        $('.budget-item').each(function () {
            var detailsField = $(this).find('textarea[name$="-details"]');
            var amountField = $(this).find('input[name$="-amount"]');
            var detailsValue = detailsField.val().trim();
            var amountValue = amountField.val().trim();
            var formGroupDetails = detailsField.closest('.form-group');
            var formGroupAmount = amountField.closest('.form-group');

            // Clear previous error messages
            formGroupDetails.find('.error-message').remove();
            formGroupAmount.find('.error-message').remove();
            formGroupDetails.removeClass("has-error");
            formGroupAmount.removeClass("has-error");

            var errorMessage = 'Both Details and Total (CHF) fields are required.';
            var amountErrorMessage = 'Total (CHF) must be a number.';

            if ((detailsValue && !amountValue) || (!detailsValue && amountValue)) {
                if (!detailsValue) {
                    formGroupDetails.addClass("has-error");
                    formGroupDetails.append('<span class="error-message is-invalid">' + errorMessage + '</span>');
                    errorMessages.push(errorMessage);
                }
                if (!amountValue) {
                    formGroupAmount.addClass("has-error");
                    formGroupAmount.append('<span class="error-message is-invalid">' + errorMessage + '</span>');
                    errorMessages.push(errorMessage);
                }
            }

            if (amountValue) {
                var amount = parseFloat(amountValue);
                if (isNaN(amount) || amount < 0) {
                    formGroupAmount.addClass("has-error");
                    formGroupAmount.append('<span class="error-message is-invalid">' + amountErrorMessage + '</span>');
                    errorMessages.push(amountErrorMessage);
                }else{
                    totalSum += parseFloat(amountValue);
                }
            }
        });
        if (totalSum > max_budget) {
            alert('Budget is greater than the maximum budget for this call.');
            var budget_step_class = $('.budget-table').closest('fieldset').attr('data-step');
            $("." + budget_step_class).addClass("budgetinvalid").removeClass("budgetvalid");
        }else{
            var budget_step_class = $('.budget-table').closest('fieldset').attr('data-step');
            $("." + budget_step_class).addClass("budgetvalid").removeClass("budgetinvalid");
        }
    }

    function checkDuplicateProposal(proposalTitle, callId, callback) {
        $.ajax({
            url: '/check_duplicate_proposal/',  // URL to check for duplicates
            data: {
                'proposal_title': proposalTitle,
                'call_id': callId
            },
            success: function (data) {
                if (data.exists) {
                    var proposalTitleInput = $("input[name='proposal_application_form-title']");
                    var label = getLabelText(proposalTitleInput).replace('*', '');
                    errorMessages.push('A proposal with this ' + label + ' already exists.');
                    alert('A proposal with this ' + label + ' already exists.');
                }
                if (callback) callback();
            },
            error: function () {
                alert('Error checking for duplicate proposals.');
            }
        });
    }

    function validateOrcid(orcid) {
    if (typeof orcid !== 'string') {
        return false; // Input is not a valid string
    }

    var orcidRegex = /^(\d{4}-){3}(\d{3}[0-9X])$/; // Updated regex to allow 'X'
    return orcidRegex.test(orcid) && orcid !== "0000-0002-1825-0097"; // Check format and exclude specific ORCID
}

    function addValidation(callback) {
        errorMessages = []; // Clear error messages

        var proposalTitle = $("input[name='proposal_application_form-title']").val();
        var callId = $("input[name='proposal_application_form-call_id']").val();

        //adding error span
        $(".required_field").each(function () {

            var input = $(this);
            if (input.hasClass('modelselect2multiple')) {
                return true;
            }
            var value;

            if (input.hasClass('select2-hidden-accessible')) {
                value = $(this).val();
            } else if (input.is('textarea') && input.hasClass('ckeditoruploadingwidget') && typeof CKEDITOR !== 'undefined') {
                var editorId = input.attr('id');
                value = CKEDITOR.instances[editorId].getData();
            } else {
                value = input.val();
            }

            var label = getLabelText(input).replace('*', '');
            var formGroup = input.closest('.form-group');
            var errorSpan = formGroup.find('.error-message');

            if (value === '' || value === null) {
                if (errorSpan.length === 0) {
                    errorSpan = $('<span class="error-message is-invalid"></span>');
                    formGroup.append(errorSpan);
                }
                errorSpan.text(label + ' is required.');
                errorMessages.push(label + ' is required.');
                formGroup.addClass("has-error");
            } else {
                if (errorSpan.length > 0) {
                    errorSpan.remove();
                    formGroup.removeClass("has-error");

                    // setTimeout(function () {
                    //     $("#div_" + ddId).find('span.error-message').remove();
                    // }, 2000);
                }
            }
        });


        validateBudgetItems(errorMessages);



        var keywordsInput = $("select[name='proposal_application_form-keywords']");
        if (keywordsInput.length) {
            var selectedKeywords = keywordsInput.find("option:selected");
            var label = getLabelText(keywordsInput);
            var formGroup = keywordsInput.closest('.form-group');
            var errorSpan = formGroup.find('.error-message');

            if (selectedKeywords.length < 5) {
                if (errorSpan.length === 0) {
                    errorSpan = $('<span class="error-message is-invalid"></span>'); // Create error span if not already present
                    formGroup.append(errorSpan); // Append error span
                }
                errorSpan.text('Please enter at least 5 ' + label + '.'); // Update error message text
                errorMessages.push('Please enter at least 5 ' + label + '.');
                formGroup.addClass("has-error");
            } else {
                if (errorSpan.length > 0) errorSpan.remove(); // Remove error span if input is valid
                formGroup.removeClass("has-error");
            }
        }

        var organisationInput = $("select[name='person_application_form-organisation_names']");
        if (organisationInput.length) {
            var selectedKeywords = organisationInput.find("option:selected");
            var label = getLabelText(organisationInput);
            var formGroup = organisationInput.closest('.form-group');
            var errorSpan = formGroup.find('.error-message');

            if (selectedKeywords.length < 1) {
                if (errorSpan.length === 0) {
                    errorSpan = $('<span class="error-message is-invalid"></span>'); // Create error span if not already present
                    formGroup.append(errorSpan); // Append error span
                }
                errorSpan.text(label + ' is required.'); // Update error message text
                errorMessages.push(label + ' is required.');
                formGroup.addClass("has-error");
            } else {
                if (errorSpan.length > 0) errorSpan.remove(); // Remove error span if input is valid
                formGroup.removeClass("has-error");
            }
        }

        var orcidInput = $("input[name='person_application_form-orcid']");
        if (orcidInput.length) {
            var orcidValue = orcidInput.val();
            var label = getLabelText(orcidInput);
            var formGroup = orcidInput.closest('.form-group');
            var errorSpan = formGroup.find('.error-message');

            if (!validateOrcid(orcidValue)) {
                if (errorSpan.length === 0) {
                    errorSpan = $('<span class="error-message is-invalid"></span>'); // Create error span if not already present
                    formGroup.append(errorSpan); // Append error span
                }
                errorSpan.text('Invalid ' + label + '. The ORCID 0000-0002-1825-0097 is not allowed.'); // Update error message text
                errorMessages.push('Invalid ' + label + '. The ORCID 0000-0002-1825-0097 is not allowed.');
                formGroup.addClass("has-error");
            } else {
                if (errorSpan.length > 0) errorSpan.remove(); // Remove error span if input is valid
                formGroup.removeClass("has-error");
            }
        }

        var privacyPolicy = $("input[name='data_collection_form-privacy_policy']");
        var formGroupPrivacyPolicy = privacyPolicy.closest('.form-group');
        var errorSpanPrivacyPolicy = formGroupPrivacyPolicy.find('.error-message');

        if (privacyPolicy.length && privacyPolicy.prop('checked')) {
            if (errorSpanPrivacyPolicy.length > 0) errorSpanPrivacyPolicy.remove(); // Remove error span if input is valid
            formGroupPrivacyPolicy.removeClass("has-error");
        } else {
            if (errorSpanPrivacyPolicy.length === 0) {
                errorSpanPrivacyPolicy = $('<span class="error-message is-invalid"></span>'); // Create error span if not already present
                formGroupPrivacyPolicy.append(errorSpanPrivacyPolicy); // Append error span
            }
            errorSpanPrivacyPolicy.text('This field is required.'); // Update error message text
            errorMessages.push('This field is required.');
            formGroupPrivacyPolicy.addClass("has-error");
        }

        // Iterate over each fieldset with class "questions-fields"
        $('fieldset').each(function () {
            var step_class = $(this).attr('data-step');
            if ($(this).find('.error-message').length > 0) {
                $("." + step_class).addClass("invalid").removeClass("valid");
            } else {
                $("." + step_class).addClass("valid").removeClass("invalid");
            }
        });

        checkDuplicateProposal(proposalTitle, callId, function () {
            // Display error messages
            if (errorMessages.length > 0) {
                var errorMessageHtml = '<ul>';
                errorMessages.forEach(function (message) {
                    errorMessageHtml += '<li>' + message + '</li>';
                });
                errorMessageHtml += '</ul>';
                var errormessagetext = "Please fill out all required fields."
                $('#error-messages').html(errormessagetext).css('display', 'block');
                $('html, body').animate({scrollTop: 0}, 'slow');
            } else {
                $("#final-result").removeClass("submit_btn");
                $("#final-result").click();
            }
        });
    }


    function storeFormData() {
        var fieldsToStore = [
            'proposal_application_form-title',
            'proposal_application_form-keywords',
            'proposal_application_form-geographical_areas'
        ];

        fieldsToStore.forEach(function (fieldName) {
            var input = $("[name='" + fieldName + "']");
            if (input.length) {
                var label = $("label[for='" + fieldName + "']").text() || input.closest('.form-group').find('label').first().text();
                if (label) {
                    localStorage.setItem(fieldName + '_label', label);
                }
                if (input.is('select')) {
                    var selectedOptionText = input.find('option:selected').text();
                    localStorage.setItem(fieldName, selectedOptionText);
                } else if (input.is(':checkbox')) {
                    var checkedValues = [];
                    input.each(function () {
                        if ($(this).is(':checked')) {
                            checkedValues.push($(this).val());
                        }
                    });
                    localStorage.setItem(fieldName, JSON.stringify(checkedValues));
                } else if (input.is(':radio')) {
                    if (input.is(':checked')) {
                        localStorage.setItem(fieldName, input.val());
                        localStorage.setItem(fieldName + '_checked', 'true');
                    }
                } else if (input.is('textarea')) {
                    localStorage.setItem(fieldName, input.val());
                } else {
                    localStorage.setItem(fieldName, input.val());
                }
            }
        });
    }

    function retrieveFormData() {
        var fieldsToRetrieve = [
            'proposal_application_form-title',
            'proposal_application_form-keywords',
            'proposal_application_form-geographical_areas'
        ];

        fieldsToRetrieve.forEach(function (fieldName) {
            var input = $("[name='" + fieldName + "']");
            if (input.length) {
                var value = localStorage.getItem(fieldName);
                if (value) {
                    if (input.is('select')) {
                        input.find('option').each(function () {
                            if ($(this).text() === value) {
                                $(this).prop('selected', true);
                            }
                        });
                    } else if (input.is(':checkbox')) {
                        var checkedValues = JSON.parse(value);
                        input.each(function () {
                            if (checkedValues.includes($(this).val())) {
                                $(this).prop('checked', true);
                            }
                        });
                    } else if (input.is(':radio')) {
                        input.prop('checked', localStorage.getItem(fieldName + '_checked') === 'true');
                    } else {
                        input.val(value);
                    }
                }
            }
        });
    }

    function populateSummary() {
        var fieldsets = {};
        var fieldsToPopulate = [
            'proposal_application_form-title',
            'proposal_application_form-keywords',
            'proposal_application_form-geographical_areas'
        ];

        fieldsToPopulate.forEach(function (fieldName) {
            var input = $("[name='" + fieldName + "']");
            var label = localStorage.getItem(fieldName + '_label') ? localStorage.getItem(fieldName + '_label').replace('*', '') : null;
            var value = localStorage.getItem(fieldName);

            if (value && !value.includes('button') && !value.includes('submit') && value !== "---------") {
                if (label) {
                    if (input.is(':checkbox')) {
                        var checkedValues = JSON.parse(value);
                        if (checkedValues.length > 0) {
                            var checkedLabels = checkedValues.map(function (val) {
                                return $("label[for='" + input.filter("[value='" + val + "']").attr('id') + "']").text().trim();
                            }).join(', ');
                            fieldsets[fieldName] = '<p><strong>' + label + ':</strong> ' + checkedLabels + '</p>';
                        }
                    } else {
                        fieldsets[fieldName] = '<p><strong>' + label + ':</strong> ' + value + '</p>';
                    }
                }
            }
        });

        var summaryHtml = Object.values(fieldsets).join('');
        $('#summary-content').html(summaryHtml);
    }


    function getLabelText(input) {
        var name = input.attr('name');
        var label = $("label[for='" + name + "']").text() || input.closest('.form-group').find('label').first().text();
        return label;
    }

    function setStep(stepIndex) {
        storeFormData();
        if (stepIndex < 0 || stepIndex >= steps) return;

        $(".progressbar .step").removeClass("active finished");
        $(".top-wizard-wrapper .step").removeClass("active finished");

        $(".progressbar .step").slice(0, stepIndex + 1).addClass("active finished");
        $(".top-wizard-wrapper .step").slice(0, stepIndex + 1).addClass("active finished");

        $("fieldset").css({'display': 'none', 'position': 'relative', 'opacity': 0});
        $("fieldset").eq(stepIndex).css({'display': 'block'}).animate({
            opacity: 1
        }, 500);
    }

    $(".next").click(function () {
        current_fs = $(this).closest('fieldset');
        next_fs = $(this).closest('fieldset').next();

        if (next_fs.length) {
            var nextIndex = $("fieldset").index(next_fs);
            setStep(nextIndex);

            if (nextIndex === steps - 1) {
                populateSummary();
            }
        }
    });

    $(".previous").click(function () {
        current_fs = $(this).closest('fieldset');
        previous_fs = $(this).closest('fieldset').prev();

        if (previous_fs.length) {
            var prevIndex = $("fieldset").index(previous_fs);
            setStep(prevIndex);
        }
        retrieveFormData();
    });

    $(".progressbar .step, .top-wizard-wrapper .step").click(function () {
        var index = $(this).index();
        setStep(index);
        populateSummary();
    });

    $(document).on('click', '.submit_btn', function (e) {
        e.preventDefault();
        addValidation();
    });

    setStep(0);
});
