"""
Django settings for ProjectApplication project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import mimetypes
import os
import pathlib

from django.contrib.messages import constants as messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'project_core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'project_core.middleware.login.LoginRequiredFormanagementMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'ProjectApplication.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ProjectApplication.wsgi.application'


def secrets_file(file_name, optional_path=None):
    """ First try optional_path, then $HOME/.file_name, then /run/secrets/file_name, else raises an exception"""

    if optional_path is not None:
        file_path_in_optional = os.path.join(optional_path, file_name)
        if os.path.exists(file_path_in_optional):
            return file_path_in_optional

    file_path_in_home_directory = os.path.join(str(pathlib.Path.home()), "." + file_name)
    if os.path.exists(file_path_in_home_directory):
        return file_path_in_home_directory

    file_path_in_run_secrets = os.path.join("/run/secrets", file_name)
    if os.path.exists(file_path_in_run_secrets):
        return file_path_in_run_secrets

    raise FileNotFoundError("Configuration for {} doesn't exist".format(file_name))


FORMAT_MODULE_PATH = [
    'spiformat.formats'
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': secrets_file('project_application_mysql.conf', '/etc/mysql'),
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'TEST': {
            'NAME': 'test_projects'
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# For deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# For the Debugging extension
# management_IPS = [
#     '127.0.0.1',
# ]

# Redirect to home URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = '/management/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Makes message tags compatible with Bootstrap4 alert messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

mimetypes.init()

LOGIN_CONTACT = 'Carles'

AWS_DEFAULT_ACL = 'private'

AWS_ACCESS_KEY_ID = os.environ['OBJECT_STORAGE_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['OBJECT_STORAGE_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['OBJECT_STORAGE_BUCKET_NAME']
AWS_S3_ENDPOINT_URL = os.environ['OBJECT_STORAGE_ENDPOINT_URL']
AWS_LOCATION = os.environ['OBJECT_STORAGE_PREFIX_LOCATION']

DEMO_MANAGEMENT_USER = os.environ['DEMO_MANAGEMENT_USER']
DEMO_MANAGEMENT_PASSWORD = os.environ['DEMO_MANAGEMENT_PASSWORD']

SECRET_KEY = os.environ.get('SECRET_KEY', 'shfl_mdb^frjpk8@5@fsl(qm0^u0+--m6_x28lgbil*m&#+rvq')

LOGGED_OUT_USERNAME = 'loggedout'
PROPOSAL_STATUS_DRAFT = 'Draft'
PROPOSAL_STATUS_SUBMITTED = 'Submitted'

if 'ALLOWED_HOST_1' in os.environ:
    ALLOWED_HOSTS.append(os.environ['ALLOWED_HOST_1'])
