from django.db import models
from apps.oaauth.models import OAUser, OADepartment
from django.conf import settings

# 通知（inform）模型
class Inform(models.Model):
    name = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    # 如果前端上传的department_ids包含0，如[0]，就认为是所有部门可见
    public = models.BooleanField(default=False)
    author = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='inform', related_query_name='inform', verbose_name='发布者')
    # departments:序列化的时候用，前端上传部门id，可通过department_ids来获取
    departments = models.ManyToManyField(OADepartment, related_name='inform', related_query_name='inform')

    class Meta:
        ordering = ['-create_time']
        verbose_name = '通知管理'
        verbose_name_plural = '通知管理'

    def __str__(self):
        return self.name


# 通知阅读统计模型（informread）
class InformRead(models.Model):
    inform = models.ForeignKey(Inform, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')
    user = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')
    read_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        # inform和user组合的数据，必须是唯一的。
        unique_together = ('inform', 'user')


# 通知附件模型（noticeattachment）
class NoticeAttachment(models.Model):
    """附件独立表，用来统计下载次数"""
    inform = models.ForeignKey(Inform, related_name="attachments", on_delete=models.CASCADE, verbose_name="所属通知")
    name = models.CharField(max_length=200, verbose_name="附件原始名称")
    file_path = models.CharField(max_length=255, verbose_name="文件相对路径")
    download_count = models.PositiveIntegerField(default=0, verbose_name="下载次数")
    upload_time = models.DateTimeField(auto_now_add=True)

    @property
    def file_url(self):
        return f"{settings.MEDIA_URL}{self.file_path}"
