from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms

from ProjectApplication import settings


class CommentForm(forms.Form):
    FORM_NAME = 'comment_form'

    # Note that Comments are not editable, so initial is always empty, always a new comment
    def __init__(self, *args, **kwargs):
        comment_category = kwargs.pop('category_queryset').exclude(category__name=settings.DATA_IMPORT_CATEGORY_NAME)
        form_action = kwargs.pop('form_action')
        form_tag = kwargs.pop('form_tag', True)
        self._fields_required = kwargs.pop('fields_required', True)
        self._form_errors = None

        super().__init__(*args, **kwargs)

        self.fields['category'] = forms.ModelChoiceField(label='Category', queryset=comment_category,
                                                         help_text='Select category of comment',
                                                         required=self._fields_required)
        self.fields['text'] = forms.CharField(label='Text', max_length=10000,
                                              help_text='Write the comment (max length: 10000 characters)',
                                              widget=forms.Textarea(attrs={'rows': 4}), required=self._fields_required)

        self.helper = FormHelper(self)

        self.divs = None  # defined later on

        if form_tag:
            self.helper.form_action = form_action
            self.helper.add_input(Submit('comment_form_submit', 'Save Comment', css_class='btn-primary'))

        self.helper.form_tag = form_tag

        self.divs = [
            Div(
                Div('category', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('text', css_class='col-12'),
                css_class='row'
            )
        ]

        self.helper.layout = Layout(*self.divs)

    def get_errors(self):
        assert self._form_errors is not None, 'clean() needs to be called before'

        return self._form_errors

    def clean(self):
        cd = super().clean()

        category = cd.get('category', None)
        text = cd.get('text', None)

        self._form_errors = {}

        if category is None and text:
            self._form_errors['category'] = 'Please select a category'

        if text is None and category:
            self._form_errors['text'] = 'Please write a comment'

        if self._form_errors:
            raise forms.ValidationError(self._form_errors)

        return cd

    def _is_empty(self):
        # A comment form might have self._fields_required == False when is part of another form.
        # In this case if category is None and text is empty the form is valid: no error would occur
        # But the form is empty: save should not be called (reponsability of the user of this class)
        return 'category' not in self.cleaned_data and 'text' not in self.cleaned_data

    def save(self, parent, user):
        if self._fields_required is False and self._is_empty():
            # For places like invoices where the fields are not required and the comment can be empty
            # (when this form is part of another form)
            return

        comment = parent.comment_object()()

        comment.set_parent(parent)
        comment.text = self.cleaned_data['text']
        comment.created_by = user
        comment.category = self.cleaned_data['category']

        comment.save()
