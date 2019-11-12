from django.utils.datastructures import MultiValueDict


def dict_to_multivalue_dict(d):
    result = dict()

    for key, value in d.items():
        result[key] = [value]

    return MultiValueDict(result)