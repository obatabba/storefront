"""
Django settings for storefront project in development.
"""

from .common import *


DEBUG = True

SECRET_KEY = 'django-insecure-hs6j037urx6iav+7#10%-vu4l4f5@@-1_zo)oft4g7$vf2$jmp'

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'storefront3',
		'USER': 'root',
		'PASSWORD': 'lolpop',
		'HOST':'localhost',
		'PORT':'3306',
        'OPTIONS': {
           "init_command": "SET GLOBAL max_connections = 1000",
	    }
    }
}
