from django.contrib import admin
from .models import OAUser, OADepartment
from DjangoProject02.admin_site import oa_admin_site


class OAUserAdmin(admin.ModelAdmin):
    list_display = ['get_index', 'realname', 'email', 'department']
    search_fields = ['realname', 'email']
    list_filter = ['department']

    def get_index(self, obj):
        return obj._index
    get_index.short_description = "序号"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        cl = response.context_data['cl']
        # 给当前页每一行对象挂上 _index，从1开始
        for i, obj in enumerate(cl.result_list, start=1):
            obj._index = i
        return response


class OADepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


oa_admin_site.register(OAUser, OAUserAdmin)
oa_admin_site.register(OADepartment, OADepartmentAdmin)
