import logging

import requests
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from dal import autocomplete
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, CheckboxSelectMultiple
from django.urls import reverse

from ProjectApplication import settings
from grant_management.models import Medium, Tag
from project_core.models import Project, PhysicalPerson
from project_core.utils.utils import new_person_message
from project_core.widgets import XDSoftYearMonthDayPickerInput
from django.core.exceptions import ValidationError


logger = logging.getLogger('grant_management')


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

class many_to_many_field_Autocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tag.objects.all()

        #search option
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class TagMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TagCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MediumModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super().__init__(*args, **kwargs)

        XDSoftYearMonthDayPickerInput.set_format_to_field(self.fields['received_date'])

        self.fields['file'].widget.attrs.update({'multiple': True})

        self.fields['blog_posts'] = BlogPostMultipleChoiceField(
            queryset=project.blogpost_set.all().order_by('received_date'),
            widget=CheckboxSelectMultiple,
            required=False,
            help_text='Please select the relevant blog posts for this media file')

        self.fields['key_image'] = forms.BooleanField(
            required=False,
            help_text='Select as a key image to be displayed on website'
        )

        self.fields['primary_image'] = forms.BooleanField(
            required=False,
            help_text='Select as a primary image on website'
        )

        # self.fields['photographer'].help_text += new_person_message()

        self.fields['license'].queryset = self.fields['license'].queryset.order_by('name')

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
                Div(
                    Div('blog_posts'),
                    Div('tags'),
                    Div('key_image'),
                    Div('primary_image'),
                ),
                css_class='row'
            ),
        )
        if self.instance.pk:
            photographer_value = self.initial.get('photographer', '')
            if photographer_value and photographer_value.isdigit():
                try:
                    photographer_obj = PhysicalPerson.objects.get(id=int(photographer_value))
                    self.initial['photographer'] = photographer_obj.first_name + ' ' + photographer_obj.surname
                except PhysicalPerson.DoesNotExist:
                    self.initial['photographer'] = ''

    def clean(self):
        cd = super().clean()
        return cd

    class Meta:
        model = Medium
        fields = ['project', 'received_date', 'photographer', 'license', 'copyright', 'blog_posts', 'tags', 'file',
                  'descriptive_text', 'key_image', 'primary_image']
        widgets = {'received_date': XDSoftYearMonthDayPickerInput,
                   'tags': autocomplete.ModelSelect2Multiple(url='logged-autocomplete-tag')}


class MediaFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def save_new(self, form, commit=True):
        uploaded_files = form.files.getlist(form.add_prefix('file'))
        saved_objs = []

        # If no file uploaded at all (empty), skip
        if not uploaded_files:
            return None

        # If only one file and form was never saved before → treat normally
        if len(uploaded_files) == 1:
            obj = form.save(commit=False)
            obj.file = uploaded_files[0]
            obj.project = self.instance
            if commit:
                obj.save()
                form.save_m2m()
            return obj

        # If multiple files, copy the form for each
        for uploaded_file in uploaded_files:
            obj = form.save(commit=False)
            obj.pk = None  # force new object
            obj.file = uploaded_file
            obj.project = self.instance
            if commit:
                obj.save()
                form.save_m2m()
            saved_objs.append(obj)

        return saved_objs

    def save(self, commit=True):
        self.saved_instances = []
        self.deleted_objects = []

        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                self.deleted_objects.append(form.instance)
                continue

            if form.has_changed():
                if form.instance.pk:
                    obj = self.save_existing(form, form.instance, commit)
                    self.saved_instances.append(obj)
                    if commit and hasattr(form, 'save_m2m'):
                        try:
                            form.save_m2m()
                        except Exception as e:
                            logger.warning(f"Error calling save_m2m on form: {e}")
                else:
                    created = self.save_new(form, commit)
                    if isinstance(created, list):
                        self.saved_instances.extend(created)
                    elif created:
                        self.saved_instances.append(created)

        # ✅ Actually delete the marked objects
        for obj in self.deleted_objects:
            if commit:
                obj.delete()

        # ✅ SPI callback
        if commit:
            if settings.SPI_MEDIA_GALLERY_IMPORT_CALLBACK is not None:
                try:
                    headers = {'ApiKey': settings.API_SECRET_KEY}
                    requests.get(settings.SPI_MEDIA_GALLERY_IMPORT_CALLBACK, headers=headers)
                except requests.ConnectionError:
                    logger.warning('NOTIFY: Notifying SPI Media Gallery for new media failed - ConnectionError')

        return self.saved_instances

    def get_queryset(self):
        return super().get_queryset().order_by('received_date')

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['project'] = self.instance
        return kwargs


MediaInlineFormSet = inlineformset_factory(Project, Medium, form=MediumModelForm,
                                           formset=MediaFormSet,
                                           min_num=1, extra=0, can_delete=True)
