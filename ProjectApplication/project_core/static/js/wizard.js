$(document).ready(function () {
    localStorage.clear();
    var current_fs, next_fs, previous_fs; // fieldsets
    var current = 1;
    var steps = $("fieldset").length;
    var errorMessages = []; // Declare errorMessages outside functions for scope
    $('#id_data_collection_form-privacy_policy').removeAttr('required');

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
        var orcidRegex = /^(\d{4}-){3}\d{4}$/;
        return orcidRegex.test(orcid) && orcid !== "0000-0002-1825-0097";
    }

    function addValidation(callback) {
        errorMessages = []; // Clear error messages

        var proposalTitle = $("input[name='proposal_application_form-title']").val();
        var callId = $("input[name='proposal_application_form-call_id']").val();

        //adding error span
        $("input[name='proposal_application_form-title'], input[name='person_application_form-orcid'], input[name='person_application_form-first_name'], input[name='person_application_form-surname'], select[name='person_application_form-academic_title'], select[name='person_application_form-gender'], input[name='person_application_form-career_stage'], input[name='person_application_form-email'], input[name='person_application_form-phone'], select[name='person_application_form-organisation_names'], textarea[name='postal_address_application_form-address'], input[name='postal_address_application_form-city'], input[name='postal_address_application_form-postcode'], input[name='postal_address_application_form-country'], input[name='proposal_application_form-start_date'], input[name='proposal_application_form-end_date'], input[name='proposal_application_form-duration_months']").each(function () {
            var input = $(this);
            var value = input.val();
            var label = getLabelText(input).replace('*', ''); // Get field label
            var formGroup = input.closest('.form-group'); // Find parent form-group

            var errorSpan = formGroup.find('.error-message');
            if (value === '') {
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
        });
        $('.quetions-fields input, .quetions-fields select, .quetions-fields textarea').each(function () {
            var input = $(this);
            var value = getInputValue(input);
            var label = getLabelText(input).replace('*', '').replace('(maximum 2500 words)', '');
            var formGroup = input.closest('.form-group');

            var errorSpan = formGroup.find('.error-message');
            if (value === '') {
                if (errorSpan.length === 0) {
                    errorSpan = $('<span class="error-message is-invalid"></span>');
                    formGroup.append(errorSpan);
                }
                errorSpan.text(label + ' is required.');
                errorMessages.push(label + ' is required.');
                formGroup.addClass("has-error");
            } else {
                if (errorSpan.length > 0) errorSpan.remove();
                formGroup.removeClass("has-error");
            }
        });

        function getInputValue(input) {
            if (input.is('textarea') && input.hasClass('ckeditoruploadingwidget')) {
                var editorId = input.attr('id');
                return CKEDITOR.instances[editorId].getData();
            } else if (input.is('input[type="checkbox"]')) {
                return input.is(':checked') ? input.attr('data-label') : '';
            } else {
                return input.val();
            }
        }



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
                console.log("test");
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
        $("fieldset :input").each(function () {
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
                } else if (input.is(':checkbox')) {
                    var checkboxId = input.attr('id');
                    var checkboxLabel = $("label[for='" + checkboxId + "']").text().trim();
                    localStorage.setItem(checkboxId + '_checked', input.is(':checked') ? 'true' : 'false');
                    if (input.is(':checked')) {
                        localStorage.setItem(checkboxId, checkboxLabel);
                    } else {
                        localStorage.removeItem(checkboxId); // Remove unchecked checkbox from storage
                    }
                } else if (input.is(':radio')) {
                    if (input.is(':checked')) {
                        localStorage.setItem(name, input.val());
                        localStorage.setItem(name + '_checked', 'true');
                    }
                } else if (input.is('textarea')) {
                    localStorage.setItem(name, input.val());
                } else {
                    localStorage.setItem(name, input.val());
                }
            }
        });
        if (typeof CKEDITOR !== 'undefined') {
            // Handle CKEditor fields
            for (var instanceName in CKEDITOR.instances) {
                var editor = CKEDITOR.instances[instanceName];
                var editorData = editor.getData();
                var label = $("label[for='" + instanceName + "']").text() || $("#" + instanceName).closest('.form-group').find('label').first().text();
                if (label) {
                    localStorage.setItem(instanceName + '_label', label);
                }
                localStorage.setItem(instanceName, editorData);
            }
        }
    }

    function retrieveFormData() {
        $("fieldset :input").each(function () {
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

        // Handle CKEditor fields
        for (var instanceName in CKEDITOR.instances) {
            var editor = CKEDITOR.instances[instanceName];
            var editorData = localStorage.getItem(instanceName);
            if (editorData) {
                editor.setData(editorData);
            }
        }
    }

    function populateSummary() {
        var fieldsets = {};

        // Group fields by their fieldset
        $("fieldset").each(function () {
            var fieldsetId = $(this).attr('id') || $(this).index();
            fieldsets[fieldsetId] = [];
            $(this).find(":input").each(function () {
                var input = $(this);
                var name = input.attr('name');
                var inputId = input.attr('id'); // Get the ID of the input element
                if (name) {
                    var key = name + '_label';
                    var label = localStorage.getItem(key) ? localStorage.getItem(key).replace('*', '') : null;
                    var value = input.is(':checkbox') ? localStorage.getItem(inputId) : localStorage.getItem(name); // Use ID for checkboxes

                    if (value && !value.includes('button') && !value.includes('submit') && value != "---------") {
                        if (label) {
                            fieldsets[fieldsetId].push('<p><strong>' + label + ':</strong> ' + value + '</p>');
                        }
                    }
                }
            });

            // Handle CKEditor fields within each fieldset
            $(this).find("textarea").each(function () {
                var textarea = $(this);
                var name = textarea.attr('name');
                if (name && CKEDITOR.instances[name]) {
                    var key = name + '_label';
                    var label = localStorage.getItem(key) ? localStorage.getItem(key).replace('*', '') : null;
                    var value = localStorage.getItem(name);

                    if (value) {
                        if (label) {
                            fieldsets[fieldsetId].push('<p><strong>' + label + ':</strong> ' + value + '</p>');
                        }
                    }
                }
            });
        });

        // Generate HTML grouped by fieldset
        var summaryHtml = '';
        for (var fieldset in fieldsets) {
            if (fieldsets[fieldset].length > 0) {
                summaryHtml += fieldsets[fieldset].join('');
            }
        }

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
