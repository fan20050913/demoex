from django.apps import AppConfig


class ImageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.image'
    verbose_name = '图片管理'


default_app_config = "apps.image.apps.ImageConfig"
