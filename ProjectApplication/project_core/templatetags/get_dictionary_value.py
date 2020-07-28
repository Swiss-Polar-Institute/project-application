from django.template.defaulttags import register


@register.filter
def get_dictionary_value(dictionary, key):
    return dictionary[key]
