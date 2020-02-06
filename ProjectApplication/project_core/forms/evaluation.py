from django import forms


class EvaluationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        YES_NO_CHOICES = [(True, 'Yes'), (False, 'No')]
        self.fields['eligible'] = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect)
        self.fields['funding'] = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect)

        self.fields['comment'] = forms.CharField(label='Comment', max_length=1000,
                                                 widget=forms.Textarea(attrs={'rows': 4}))
