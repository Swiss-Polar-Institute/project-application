from django import forms


class ValidIfEmptyModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        fields_allowed_empty = kwargs.pop('fields_allowed_empty', [])
        self._basic_fields = kwargs.pop('basic_fields', [])

        super().__init__(*args, **kwargs)

        for field_allowed_empty in fields_allowed_empty:
            self.fields[field_allowed_empty].required = False

    def _is_empty(self):
        """
        Returns True if no data has been entered (based on self.data and self.cleaned_data)
        This is used in order to show a Financial Report but let the user to not enter anything
        (so it plays easily with the jQuery modelset)

        TODO: avoid this (changing how the initial form is done)

        Note that this method needs to use self.data and self.cleaned_data:
        -self.data: required because it contains the fields that failed validation
        (in this case the form is not empty but the fields are not in self.cleaned_data)
        -self.cleaned_data: required because it contains fields which widgets are disabled. Those fields
        are not in self.data but are in self.cleaned_data

        Not using self.errors (it would be a way to detect fields that didn't pass the validation)
        in case that an empty field might actually trigger an error.
        """

        for field_name in self.fields:
            if field_name in self._basic_fields:
                continue

            if self.prefix is not None:
                field_name_in_data = f'{self.prefix}-{field_name}'
            else:
                field_name_in_data = field_name

            if self.data.get(field_name_in_data, '') != '' or self.cleaned_data.get(field_name) is not None:
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
