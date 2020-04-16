from django import forms


class ModelValidIfEmptyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        fields_allowed_empty = kwargs.pop('fields_allowed_empty', [])
        self._basic_fields = kwargs.pop('basic_fields', [])

        super().__init__(*args, **kwargs)

        for field_allowed_empty in fields_allowed_empty:
            self.fields[field_allowed_empty].required = False

    def _is_empty(self):
        # Returns True if no data has been entered (based on self.cleaned_data)
        # This is used in order to show a Financial Report but let the user to not enter anything
        # (so it plays easily with the jQuery modelset)
        # TODO: avoid this

        for field_name in self.fields:
            if field_name in self._basic_fields:
                continue
            if field_name in self.cleaned_data and self.cleaned_data[field_name] is not None:
                return False

        return True

    def save(self, *args, **kwargs):
        """
        -If it's empty but it has an instance id: it needs to delete this. This is in the case that the user
        emptied an Invoice / FinancialReport / ...
        -If it's empty but it didn't have an instance id: do nothing, this is when a user didn't input anything
        in the form: it does nothing. The validation said that was "ok" even with the missing required fields
        but we cannot save it.
        -If it's not empty: save
        """
        if self._is_empty():
            if self.instance.id:
                self.instance.delete()

            return None

        return super().save(*args, **kwargs)

    def is_valid(self):
        valid = super().is_valid()

        return valid or self._is_empty()
