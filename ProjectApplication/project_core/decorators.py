from django.http import HttpResponse

from ProjectApplication import settings


def api_key_required(function):
    def wrap(request, *args, **kwargs):
        if 'ApiKey' not in request.request.headers:
            return HttpResponse(status=400,
                                content='"ApiKey" HTTP header is required')

        api_key_client = request.request.headers['ApiKey']
        if api_key_client != settings.API_SECRET_KEY:
            return HttpResponse(status=403,
                                content=f'Received ApiKey header ({api_key_client}) does not match settings.API_SECRET_KEY')

        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
