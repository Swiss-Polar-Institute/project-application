from django.template.defaulttags import register


@register.filter
def get_dictionary_value(dictionary, key):
    if dictionary and key in dictionary:
        return dictionary[key]
    return None
