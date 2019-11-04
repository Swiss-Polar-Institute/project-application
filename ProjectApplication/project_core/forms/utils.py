def get_model_information(model, field, information):
    return getattr(model._meta.get_field(field), information)


def get_field_information(model, field):
    kwargs = {}

    kwargs['help_text'] = get_model_information(model, field, 'help_text')
    kwargs['required'] = not get_model_information(model, field, 'blank')

    max_length = get_model_information(model, field, 'max_length')
    if max_length is not None:
        kwargs['max_length'] = max_length

    return kwargs