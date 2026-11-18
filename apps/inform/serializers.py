from rest_framework import serializers
from apps.oaauth.models import OADepartment
from apps.oaauth.serializers import OAUserSerializer, OADepartmentSerializer
from apps.inform.models import Inform, InformRead, NoticeAttachment
from rest_framework.exceptions import PermissionDenied


# 附件序列化器
class InformAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.ReadOnlyField()  # 把模型里@property的file_url返回前端
    class Meta:
        model = NoticeAttachment
        fields = ["id", "name", "file_path", "file_url", "download_count", "upload_time"]


# 通知阅读序列化器
class InformReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformRead
        fields = '__all__'


# 通知阅读统计序列化器
class InformReadCountSerializer(serializers.Serializer):
    inform_id = serializers.IntegerField(error_messages={"required": '请传入inform的id!'})


# 通知序列化器
class InformSerializer(serializers.ModelSerializer):
    # 外联字段 只读
    author = OAUserSerializer(read_only=True)
    departments = OADepartmentSerializer(read_only=True, many=True)
    # 前端传入部门id列表，只写
    department_ids = serializers.ListField(write_only=True)
    reads = InformReadSerializer(read_only=True, many=True)
    attachments = InformAttachmentSerializer(read_only=True, many=True)

    # 新增时接收附件数组
    attachment_list = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Inform
        fields = '__all__'
        read_only_fields = ('public',)

    def create(self, validated_data):
        request = self.context['request']
        # 取出部门id列表
        department_ids = validated_data.pop('department_ids')
        department_ids = list(map(lambda value: int(value), department_ids))

        # 取出附件
        attachment_list = validated_data.pop("attachment_list", [])

        if 0 in department_ids:
            # 全部部门公开
            inform = Inform.objects.create(public=True, author=request.user, **validated_data)
        else:
            departments = OADepartment.objects.filter(id__in=department_ids)
            inform = Inform.objects.create(public=False, author=request.user, **validated_data)
            inform.departments.set(departments)

        # 创建附件
        for att_item in attachment_list:
            NoticeAttachment.objects.create(
                inform=inform,
                name=att_item["name"],
                file_path=att_item["path"]
            )
        return inform
