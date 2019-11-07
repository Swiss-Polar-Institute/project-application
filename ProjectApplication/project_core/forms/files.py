from django import forms

# TODO
class UploadFilesForm(forms.Form):
    file = forms.FileField()
