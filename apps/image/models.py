from django.db import models

# Create your models here.
from django.db import models

class Banner(models.Model):
    # 轮播图标题
    title = models.CharField(max_length=100, verbose_name="轮播标题")
    # 图片文件，上传到 media/banner 目录
    image = models.ImageField(upload_to="banner/", verbose_name="轮播图片")
    # 点击跳转链接，可以为空
    link = models.URLField(blank=True, null=True, verbose_name="跳转链接")
    # 是否启用，用来快速上下线轮播
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "轮播图"
        verbose_name_plural = "轮播图"

    def __str__(self):
        return self.title
