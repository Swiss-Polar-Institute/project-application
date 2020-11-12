from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from project_core.models import Proposal, ProposalScientificCluster


class ScientificClusterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        # self.helper.disable_csrf = True  # checked in the higher form level

        self.helper.layout = Layout(
            Div(
                Div('proposal', hidden=True),
                Div('id', hidden=True),
                Div(Field('DELETE', hidden=True)),
                css_class='row', hidden=True
            ),
            Div(
                Div('title', css_class='col-12'),
                css_class='row'
            ),
        )

    def clean(self):
        cd = super().clean()
        return cd

    class Meta:
        model = ProposalScientificCluster
        fields = ['proposal', 'title']


class ScientificClustersFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

    def get_queryset(self):
        return super().get_queryset().order_by('id')


ScientificClustersInlineFormSet = inlineformset_factory(Proposal, ProposalScientificCluster, form=ScientificClusterForm,
                                                        formset=ScientificClustersFormSet,
                                                        min_num=1, extra=0, can_delete=True)
