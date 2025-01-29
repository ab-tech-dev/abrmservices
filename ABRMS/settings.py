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


# Ensure you securely generate and store these keys, possibly using environment variables
SECRET_KEY_P = os.getenv("SECRET_KEY", "your_generated_key")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "your_paystack_secret_key")


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
    'django.contrib.sites',
    'user',
    'abrmservices',
    'payments',
    'crispy_forms', 
]

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
]

# Optional: Define login URL
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'housing'
LOGOUT_REDIRECT_URL = 'housing'

# Google OAuth2 credentials
GOOGLE_OAUTH2_CLIENT_ID = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
GOOGLE_OAUTH2_REDIRECT_URI = 'https://aa31-197-211-58-3.ngrok-free.app/auth/google/callback/'

CSRF_TRUSTED_ORIGINS = [
    "https://aa31-197-211-58-3.ngrok-free.app",
]


CRISPY_TEMPLATE_PACK = 'bootstrap4'  # or 'bootstrap5', depending on your preference


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'user.middleware.ActiveUserMiddleware',
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

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME_USERS', 'default_db_name_users'),
        'USER': os.getenv('DB_USER_USERS', 'default_db_user'),
        'PASSWORD': os.getenv('DB_PASSWORD_USERS', 'default_db_password'),
        'HOST': os.getenv('DB_HOST_USERS', 'localhost'),
    },

}


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


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # keep this for default Django auth
)