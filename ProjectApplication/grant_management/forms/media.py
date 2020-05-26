from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from dal import autocomplete
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, CheckboxSelectMultiple

from grant_management.models import Medium
from project_core.models import Project
from project_core.widgets import XDSoftYearMonthDayPickerInput


class BlogPostMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        if obj.title:
            return f'{obj.received_date} - {obj.title}'
        else:
            return f'Due {obj.due_date}, not yet received'


class BlogPostCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MediumModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['received_date'])

        self.fields['blog_posts'] = BlogPostMultipleChoiceField(
            queryset=project.blogpost_set.all().order_by('received_date'),
            widget=CheckboxSelectMultiple,
            required=False,
            help_text='Please select the relevant blog posts for this media file')

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
                Div('photographer', css_class='col-4'),
                Div('license', css_class='col-4'),
                Div('copyright', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('file', css_class='col-4'),
                Div('received_date', css_class='col-4'),
                css_class='row'
            ),
            Div(
                Div('descriptive_text', css_class='col-6'),
                Div('blog_posts', css_class='col-6'),
                css_class='row'
            ),
        )

    def clean(self):
        cd = super().clean()

    class Meta:
        model = Medium
        fields = ['project', 'received_date', 'photographer', 'license', 'copyright', 'blog_posts', 'file',
                  'descriptive_text']
        widgets = {'received_date': XDSoftYearMonthDayPickerInput,
                   'photographer': autocomplete.ModelSelect2(url='logged-autocomplete-physical-people')}


class MediaFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('received_date')

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['project'] = self.instance
        return kwargs


MediaInlineFormSet = inlineformset_factory(Project, Medium, form=MediumModelForm,
                                           formset=MediaFormSet,
                                           min_num=1, extra=0, can_delete=True)
