from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.urls import reverse

from evaluation.models import Criterion
from project_core.forms.utils import cancel_edit_button, cancel_button


class CriterionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        is_edit = self.instance and self.instance.pk

        if is_edit:
            cancel_html = cancel_edit_button(reverse('logged-evaluation_criterion-detail',
                                                     kwargs={'pk': self.instance.pk}))
        else:
            cancel_html = cancel_button(reverse('logged-evaluation_criteria-list'))

        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-6'),
                css_class='row'
            ),
            Div(
                Div('description', css_class='col-6'),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save Criterion'),
                cancel_html
            )
        )

    class Meta:
        model = Criterion
        fields = ['name', 'description']
