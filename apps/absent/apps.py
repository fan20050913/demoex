from django.apps import AppConfig


class AbsentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.absent'
    verbose_name = '考勤管理'

default_app_config = "apps.absent.apps.AbsentConfig"
