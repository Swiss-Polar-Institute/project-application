from django.forms import ModelForm, TextInput

from .models import Colour


class ColourForm(ModelForm):
    class Meta:
        model = Colour
        fields = '__all__'
        widgets = {
            'hex_code': TextInput(attrs={'type': 'color'}),
        }
