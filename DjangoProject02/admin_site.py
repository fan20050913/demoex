from django.contrib.admin import AdminSite


class MyOAAdminSite(AdminSite):
    site_header = "OA系统"
    site_title = "OA系统后台"
    index_title = "OA系统管理"

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # 过滤掉auth分组
        return [app for app in app_list if app["app_label"] != "auth"]


# 实例化
oa_admin_site = MyOAAdminSite()
