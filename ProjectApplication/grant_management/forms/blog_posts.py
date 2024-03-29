from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from dal import autocomplete
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, NumberInput

from grant_management.models import BlogPost
from project_core.models import Project
from project_core.utils.utils import new_person_message
from project_core.widgets import XDSoftYearMonthDayPickerInput


class BlogPostModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['received_date'])

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True  # checked in the higher form level

        self.fields['author'].help_text += new_person_message()

        media = "{% include 'grant_management/_enumeration_of_media.tmpl' %}"

        self.helper.layout = Layout(
            Div(
                Div('project', hidden=True),
                Div('id', hidden=True),
                Div(Field('DELETE', hidden=True)),
                css_class='row', hidden=True
            ),
            Div(
                Div('due_date', css_class='col-4'),
                Div('received_date', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('title', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('text', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('author', css_class='col-6'),
                Div(HTML(media), css_class='col-6'),
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()

        if self.errors:
            return cd

        due_date = cd.get('due_date', None)
        received_date = cd.get('received_date', None)
        author = cd.get('author', None)

        text = cd.get('text', '')
        if text is None:
            text = ''
        title = cd.get('title', '')
        if title is None:
            title = ''

        errors = {}

        if author is None and text != '':
            errors['author'] = 'Please select the author if there is text'
        if received_date is not None and text == '':
            errors['text'] = 'Please enter the text if there is a date received'
        if author is not None and text == '':
            errors['text'] = 'Please enter the text if there is an author'
        if text != '' and received_date is None:
            errors['received_date'] = 'Please enter the date received if there is text'
        if text != '' and title == '':
            errors['title'] = 'Please enter a title for the blog post'

        if errors:
            raise forms.ValidationError(errors)

        return cd

    class Meta:
        model = BlogPost
        fields = ['project', 'due_date', 'received_date', 'title', 'text', 'author']
        labels = {'due_date': 'Due', 'received_date': 'Received'}
        help_texts = {'text': None, 'due_date': 'Date the blog post is due',
                      'received_date': 'Date the blog post was received'}
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'received_date': XDSoftYearMonthDayPickerInput,
            'project': NumberInput,
            'author': autocomplete.ModelSelect2(url='logged-autocomplete-physical-people')
        }


class BlogPostsFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('due_date')


BlogPostsInlineFormSet = inlineformset_factory(Project, BlogPost, form=BlogPostModelForm,
                                               formset=BlogPostsFormSet,
                                               min_num=1, extra=0, can_delete=True)
