"""ProjectApplication URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path,re_path
from django.conf import settings
from django.conf.urls.static import static
from django_otp.admin import OTPAdminSite
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


from ckeditor_uploader import views as ckeditor_views


if settings.ALLOWED_HOSTS[0] == "projects.swisspolar.ch":
    admin.site.__class__ = OTPAdminSite

urlpatterns = [
    path('', include('project_core.urls')),
    path('', include('evaluation.urls')),
    path('', include('grant_management.urls')),
    path('', include('reporting.urls')),
    path(settings.ADMIN_URL, admin.site.urls),
    re_path(r"^ckeditor/upload/", login_required(ckeditor_views.upload), name="ckeditor_upload"),
    re_path(r"^ckeditor/browse/", never_cache(login_required(ckeditor_views.browse)), name="ckeditor_browse")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
