"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import environ
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = [env('ALLOWED_HOSTS')]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'nagoyameshi.apps.NagoyameshiConfig',
    'bootstrapform',
    'import_export',
    'storages',
]

AUTH_USER_MODEL = 'nagoyameshi.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

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

WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'NAGOYAMESHI',
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
    # カスタムバリデーションクラス
    {
        "NAME": "nagoyameshi.utils.password_validator.PasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = '/static/'
#STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] 
#STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 画像関連の設定
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_local')

"""
デプロイ時設定
#AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
#AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
#AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
#AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
#AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400',}
#AWS_LOCATION = 'static'
#AWS_DEFAULT_ACL = None
#STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
STATIC_ROOT = '/var/www/static/'
#STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
"""

# ログイン認証
LOGIN_URL = 'top'
LOGIN_REDIRECT_URL = 'top'
LOGOUT_REDIECT_URL = 'top'

# メール認証 情報源: https://qiita.com/koseidaiki/items/85279375555a533c9318）
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # コンソールにメール内容を表示する
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # メールを送信する
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
# Nagoyameshi用のアプリパスワードを設定
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

# メール認証の有効期限
ACTIVATION_EXPIRED_DAYS = 1
