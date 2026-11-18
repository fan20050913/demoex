from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import Inform
from DjangoProject02.admin_site import oa_admin_site


class InformAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'author',
        'create_time',
        'operate',  # 新增操作列
    ]
    search_fields = ['name']
    list_filter = ['author']

    # 自定义操作按钮列
    def operate(self, obj):
        # 编辑链接：django admin原生修改地址
        edit_url = f"/admin/inform/inform/{obj.id}/change/"
        # 查看链接：你前端的通知详情页面
        view_url = f"http://localhost:5173/login#/inform/detail/{obj.id}"
        return format_html(
            '<a href="{}" target="_blank" style="color:red;margin-right:8px;">查看</a>'
            '<a href="{}" style="color:blue;">编辑</a>',
            view_url,
            edit_url
        )
    operate.short_description = "操作"


oa_admin_site.register(Inform, InformAdmin)
