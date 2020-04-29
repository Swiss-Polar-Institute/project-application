from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, NumberInput

from grant_management.models import BlogPost
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class BlogPostModelForm(forms.ModelForm):
    FORM_NAME = 'blog_post'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['due_date'])
        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['received_date'])

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True  # checked in the higher form level

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
                Div('text', css_class='col-12'),
                css_class='row'
            ),
            Div(
                Div('author', css_class='col-6'),
                css_class='row'
            )
        )

    def clean(self):
        cd = super().clean()

        due_date = cd.get('due_date', None)
        received_date = cd.get('received_date', None)
        text = cd.get('text', None)
        author = cd.get('author', None)

        errors = {}

        if author is None and text is not None:
            errors['author'] = 'Please select the author if there is text'

        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = BlogPost
        fields = ['project', 'due_date', 'received_date', 'text', 'author']
        widgets = {
            'due_date': XDSoftYearMonthDayPickerInput,
            'received_date': XDSoftYearMonthDayPickerInput,
            'project': NumberInput
        }


class BlogPostsFormSet(BaseInlineFormSet):
    FORM_NAME = 'blog_posts_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = BlogPostsFormSet.FORM_NAME

    def get_queryset(self):
        return super().get_queryset().order_by('received_date')


BlogPostsInlineFormSet = inlineformset_factory(Project, BlogPost, form=BlogPostModelForm,
                                               formset=BlogPostsFormSet,
                                               min_num=1, extra=0, can_delete=True)
