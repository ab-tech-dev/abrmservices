import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv  # Add this line to use environment variables from a .env file
import dj_database_url
load_dotenv()  # Load environment variables from a .env file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'user',
    'abrmservices',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ABRMS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'ABRMS.wsgi.application'

# DATABASES = {
#     'default': {},  # Default can be left empty if unused

#     # Users database
#     'users': dj_database_url.parse(
#         os.getenv('DATABASE_URL_USERS'),
#         conn_max_age=600,
#         ssl_require=True
#     ),

#     # ABRM Services database
#     'abrmservices': dj_database_url.parse(
#         os.getenv('DATABASE_URL_ABRMSERVICES'),
#         conn_max_age=600,
#         ssl_require=True
#     ),
# }

# # Database

# DATABASES = {
#     'default': dj_database_url.parse(
#         os.getenv('DATABASE_URL_MAIN'),  # Fetch the connection string from the environment
#         conn_max_age=600,               # Keep database connections open for 10 minutes
#         ssl_require=True                # Enforce SSL for secure connections
#     ),
# }

DATABASES = {
    'default': {},

    'users': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME_USERS', 'default_db_name_users'),
        'USER': os.getenv('DB_USER_USERS', 'default_db_user'),
        'PASSWORD': os.getenv('DB_PASSWORD_USERS', 'default_db_password'),
        'HOST': os.getenv('DB_HOST_USERS', 'localhost'),
    },

    'abrmservices': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME_ABRMSERVICES', 'default_db_name_abrmservices'),
        'USER': os.getenv('DB_USER_ABRMSERVICES', 'default_db_user'),
        'PASSWORD': os.getenv('DB_PASSWORD_ABRMSERVICES', 'default_db_password'),
        'HOST': os.getenv('DB_HOST_ABRMSERVICES', 'localhost'),
    },
}

DATABASE_ROUTERS = ['user.router.AuthRouter', 'abrmservices.router.ListingRouter']

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT =587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'default_email_user')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'default_email_password')
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# File upload settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB



# Custom user model
AUTH_USER_MODEL = 'user.UserAccount'

