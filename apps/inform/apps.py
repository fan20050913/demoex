from django.apps import AppConfig


class InformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inform'
    verbose_name = '通知管理'


default_app_config = "apps.inform.apps.InformConfig"
