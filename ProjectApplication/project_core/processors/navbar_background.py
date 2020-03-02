from django.conf import settings


def background(request):
    return {'navbarcolor': settings.NAVBAR_BACKGROUND_COLOR}
