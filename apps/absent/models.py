from django.db import models
from apps.oaauth.models import OAUser


#请假申请的状态设定
class AbsentStatusChoices(models.IntegerChoices):
    #审批中
    AUDTING=1
    #审批通过
    PASS=2
    #审批不通过
    REJECT=3


#请假类型
class AbsentType(models.Model):
    name = models.CharField(max_length=20)
    create_time=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "请假类型"
        verbose_name_plural = "请假类型"

    def __str__(self):
        return self.name




#请假申请
class Absent(models.Model):
    # 1.标题
    title = models.CharField(max_length=100)
    # 2.请假详细内容
    request_content = models.TextField()
    # 3.请假类型
    absent_type = models.ForeignKey(AbsentType, on_delete=models.CASCADE,related_name='absent',related_query_name='absent')
    # 注意，如果在一个模型中，有多个字段对同一个模型引用了外键，那么related_name必须用不同值
    # 4.发起人
    requester=models.ForeignKey(OAUser,on_delete=models.CASCADE,related_name='my_absent',related_query_name='my_absent')
    #5.审批人（可以为空，例如最高的leader请假不许审批）
    responder=models.ForeignKey(OAUser,on_delete=models.CASCADE,related_name='sub_absent',related_query_name='sub_absent',null=True)
    # 6.状态
    status=models.IntegerField(choices=AbsentStatusChoices,default=AbsentStatusChoices.AUDTING)
    #7.请假开始日期
    start_date=models.DateTimeField()
    #8.请假结束日期
    end_date = models.DateTimeField()
    # 9.请假发起时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 10.审批回复内容
    response_content = models.TextField(default='')

    class Meta:
        ordering = ('-create_time',)
        verbose_name = '请假管理'
        verbose_name_plural = '请假管理'

    def __str__(self):
        return self.title
