from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'
STATIC_ROOT = str(BASE_DIR / 'staticfiles')  # converte Path para string, importante!

MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media')

# Em produção (DEBUG=False), use armazenamentos remotos para estáticos e mídia
if not DEBUG:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')

    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

    STATICFILES_STORAGE = 'storages.backends.s3.S3StaticStorage'
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"

    DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

else:
    # Em desenvolvimento, usar WhiteNoise localmente
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'