from django.apps import AppConfig

class OaauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # 重点！路径要写完整：apps.oaauth
    name = 'apps.oaauth'
    verbose_name = '权限认证'
