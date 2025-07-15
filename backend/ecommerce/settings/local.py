from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DJANGO_DB_NAME','ecommercedb'),
        'USER': os.getenv('DJANGO_DB_USER','postgres'),
        'PASSWORD': os.getenv('DJANGO_DB_PASS','123456'),
        'HOST': os.getenv('DJANGO_DB_HOST','localhost'),
        'PORT': os.getenv('DJANGO_DB_PORT','5432')
    }
}