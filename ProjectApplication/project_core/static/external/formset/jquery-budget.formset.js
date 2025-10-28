/**
 * SPI: Downloaded from: https://github.com/elo80ka/django-dynamic-formset/blob/master/src/jquery.formset.js
 * See lines with SPI to identify the changes
 *
 * jQuery Formset 1.5-pre
 * @author Stanislaus Madueke
 * @requires jQuery 1.2.6 or later
 *
 * Copyright (c) 2009, Stanislaus Madueke
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
;(function($) {
    $.fn.formset = function(opts)
    {
        var options = $.extend({}, $.fn.formset.defaults, opts),
            flatExtraClasses = options.extraClasses.join(' '),
            totalForms = $('#id_' + options.prefix + '-TOTAL_FORMS'),
            maxForms = $('#id_' + options.prefix + '-MAX_NUM_FORMS'),
            minForms = $('#id_' + options.prefix + '-MIN_NUM_FORMS'),
            childElementSelector = 'input,select,textarea,label,div',
            $$ = $(this),

            applyExtraClasses = function(row, ndx) {
                if (options.extraClasses) {
                    row.removeClass(flatExtraClasses);
                    row.addClass(options.extraClasses[ndx % options.extraClasses.length]);
                }
            },

            updateElementIndex = function(elem, prefix, ndx) {
                var idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
                    replacement = prefix + '-' + ndx + '-';
                if (elem.attr("for")) elem.attr("for", elem.attr("for").replace(idRegex, replacement));
                if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
                if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
                if (elem.attr('data-select2-id')) elem.attr('data-select2-id', elem.attr('data-select2-id').replace(idRegex, replacement));   // SPI fix
            },

            hasChildElements = function(row) {
                return row.find(childElementSelector).length > 0;
            },

            showAddButton = function() {
                return maxForms.length == 0 ||
                    (maxForms.val() == '' || (maxForms.val() - totalForms.val() > 0));
            },

            showDeleteLinks = function() {
                return minForms.length == 0 ||
                    (minForms.val() == '' || (totalForms.val() - minForms.val() > 0));
            },

            insertDeleteLink = function(row) {
                var delCssSelector = $.trim(options.deleteCssClass).replace(/\s+/g, '.'),
                    addCssSelector = $.trim(options.addCssClass).replace(/\s+/g, '.');

                var delButtonHTML = '<a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText +'</a>';
                if (options.deleteContainerClass) {
                    row.find('[class*="' + options.deleteContainerClass + '"]').append(delButtonHTML);
                } else if (row.is('TR')) {
                    row.children(':last').append(delButtonHTML);
                } else if (row.is('UL') || row.is('OL')) {
                    row.append('<li>' + delButtonHTML + '</li>');
                } else {
                    row.append(delButtonHTML);
                }

                if (!showDeleteLinks()){
                    row.find('a.' + delCssSelector).hide();
                }

                row.find('a.' + delCssSelector).click(function() {
                    var row = $(this).parents('.' + options.formCssClass),
                        del = row.find('input:hidden[id$="-DELETE"]'),
                        buttonRow = row.siblings("a." + addCssSelector + ', .' + options.formCssClass + '-add'),
                        forms;

                    if (del.length) {
                        del.val('on');
                        row.hide();
                        forms = $('.' + options.formCssClass).not(':hidden');
                    } else {
                        row.remove();
                        forms = $('.' + options.formCssClass).not('.formset-custom-template');
                    }

                    for (var i=0, formCount=forms.length; i<formCount; i++) {
                        applyExtraClasses(forms.eq(i), i);
                        if (!del.length) {
                            forms.eq(i).find(childElementSelector).each(function() {
                                updateElementIndex($(this), options.prefix, i);
                            });
                        }
                    }

                    if (!showDeleteLinks()){
                        $('a.' + delCssSelector).each(function(){$(this).hide();});
                    }

                    if (buttonRow.is(':hidden') && showAddButton()) buttonRow.show();

                    if (options.removed) options.removed(row);
                    return false;
                });
            };

        $$.each(function(i) {
            var row = $(this),
                del = row.find('input:checkbox[id$="-DELETE"]');

            if (del.length) {
                // ✅ FIXED delete checkbox logic:
                if (del.is(':checked')) {
                    del.before('<input type="hidden" name="' + del.attr('name') + '" id="' + del.attr('id') + '" value="on" />');
                    row.hide();
                } else {
                    del.before('<input type="hidden" name="' + del.attr('name') + '" id="' + del.attr('id') + '" />');
                }

                // Hide label + checkbox instead of removing
                $('label[for="' + del.attr('id') + '"]').hide();
                //del.hide();  // ✅ fixed: don't remove checkbox, just hide it
            }

            if (hasChildElements(row)) {
                row.addClass(options.formCssClass);
                if (row.is(':visible')) {
                    insertDeleteLink(row);
                    applyExtraClasses(row, i);
                }
            }
        });

        if ($$.length) {
            var hideAddButton = !showAddButton(),
                addButton, template;
            if (options.formTemplate) {
                template = (options.formTemplate instanceof $) ? options.formTemplate : $(options.formTemplate);
                template.removeAttr('id').addClass(options.formCssClass + ' formset-custom-template');
                template.find(childElementSelector).each(function() {
                    updateElementIndex($(this), options.prefix, '__prefix__');
                });
                insertDeleteLink(template);
            } else {
                if (options.hideLastAddForm) $('.' + options.formCssClass + ':last').hide();
                template = $('.' + options.formCssClass + ':last').clone(true).removeAttr('id');
                // ✅ remove hidden DELETE from cloned forms
                template.find('input:hidden[id$="-DELETE"]').remove();
                template.find(childElementSelector).not(options.keepFieldValues).each(function() {
                    var elem = $(this);
                    if (elem.is('input:checkbox') || elem.is('input:radio')) {
                        elem.prop('checked', false);
                    } else {
                        elem.val('');
                    }
                });
            }

            options.formTemplate = template;

            var addButtonHTML = '<a class="' + options.addCssClass + '" href="javascript:void(0)">' + options.addText + '</a>';
            if (options.addContainerClass) {
                var addContainer = $('[class*="' + options.addContainerClass + '"]');
                addContainer.append(addButtonHTML);
                addButton = addContainer.find('[class="' + options.addCssClass + '"]');
            } else if ($$.is('TR')) {
                var numCols = $$.eq(0).children().length,
                    buttonRow = $('<tr><td colspan="' + numCols + '">' + addButtonHTML + '</tr>').addClass(options.formCssClass + '-add');
                $$.parent().append(buttonRow);
                addButton = buttonRow.find('a');
            } else {
                $$.filter(':last').after(addButtonHTML);
                addButton = $$.filter(':last').next();
            }

            if (hideAddButton) addButton.hide();

            addButton.click(function() {
                var formCount = parseInt(totalForms.val()),
                    row = options.formTemplate.clone(true).removeClass('formset-custom-template'),
                    buttonRow = $($(this).parents('tr.' + options.formCssClass + '-add').get(0) || this),
                    delCssSelector = $.trim(options.deleteCssClass).replace(/\s+/g, '.');

                applyExtraClasses(row, formCount);
                row.insertBefore(buttonRow).show();

                // ✅ ensure DELETE hidden not cloned
                row.find('input:hidden[id$="-DELETE"]').remove();

                row.find(childElementSelector).each(function() {
                    updateElementIndex($(this), options.prefix, formCount);
                });

                totalForms.val(formCount + 1);

                if (showDeleteLinks()){
                    $('a.' + delCssSelector).each(function(){$(this).show();});
                }

                if (!showAddButton()) buttonRow.hide();

                if (options.added) options.added(row);
                return false;
            });
        }

        return $$;
    };

    $.fn.formset.defaults = {
        prefix: 'form',
        formTemplate: null,
        addText: 'add another',
        deleteText: 'remove',
        addContainerClass: null,
        deleteContainerClass: null,
        addCssClass: 'add-row',
        deleteCssClass: 'delete-row',
        formCssClass: 'dynamic-form',
        extraClasses: [],
        keepFieldValues: '',
        added: null,
        removed: null,
        hideLastAddForm: false
    };
})(jQueryForFormset);  // SPI: use isolated jQuery reference
