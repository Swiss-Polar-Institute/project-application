from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, NumberInput

from grant_management.models import ProjectSocialNetwork, SocialNetwork
from project_core.models import Project


class SocialNetworkModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['social_network'].queryset = SocialNetwork.objects.order_by('name')

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
                Div('social_network', css_class='col-6'),
                Div('url', css_class='col-6'),
                css_class='row'
            ),
        )

    def clean(self):
        cd = super().clean()

    class Meta:
        model = ProjectSocialNetwork
        fields = ['project', 'social_network', 'url']
        widgets = {
            'project': NumberInput,
        }
        labels = {
            'url': 'URL'
        }


class SocialNetworksFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('social_network')


SocialNetworksInlineFormSet = inlineformset_factory(Project, ProjectSocialNetwork, form=SocialNetworkModelForm,
                                                    formset=SocialNetworksFormSet,
                                                    min_num=1, extra=0, can_delete=True)
