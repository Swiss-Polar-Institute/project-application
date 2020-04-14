from django import forms


class ModelValidIfEmptyForm(forms.ModelForm):
    def _is_empty(self):
        # Returns True if no data has been entered (based on self.cleaned_data)
        # This is used in order to show a Financial Report but let the user to not enter anything
        # (so it plays easily with the jQuery modelset)
        # TODO: avoid this

        for field_name in self.fields:
            if field_name in ['project', 'id', 'DELETE', 'can_be_deleted']:
                continue
            if field_name in self.cleaned_data and self.cleaned_data[field_name] is not None:
                return False

        return True

    def save(self, *args, **kwargs):
        if self._is_empty():
            return None

        super().save(*args, **kwargs)

    def is_valid(self):
        valid = super().is_valid()

        return valid or self._is_empty()
