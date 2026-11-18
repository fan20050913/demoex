from rest_framework import serializers
from apps.absent.models import Absent, AbsentType, AbsentStatusChoices
from apps.oaauth.serializers import OAUserSerializer
from rest_framework import exceptions
from .utils import get_responder


class AbsentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsentType
        fields = '__all__'

class AbsentSerializer(serializers.ModelSerializer):
    absent_type = AbsentTypeSerializer(read_only=True)
    absent_type_id = serializers.IntegerField(write_only=True)
    requester = OAUserSerializer(read_only=True)
    responder = OAUserSerializer(read_only=True)

    class Meta:
        model = Absent
        fields = '__all__'

    # 验证absent_type_id是否在数据表中是否存在
    def validate_absent_type_id(self, value):
        if not AbsentType.objects.filter(pk=value).exists():
            raise exceptions.ValidationError("考勤类型不存在")
        return value

    # # 重写create方法
    # def create(self, validated_data):
    #     request = self.context['request']
    #     user = request.user
    #     # 获取审批者
    #     responder = get_responder(request)
    #     if responder is None:
    #         validated_data['status'] = AbsentStatusChoices.PASS
    #     else:
    #         validated_data['status'] = AbsentStatusChoices.AUDTING
    #     absent = Absent.objects.create(**validated_data, requester=user, responder=responder)
    #     return absent

    def create(self, validated_data):
        try:
            request = self.context['request']
            user = request.user
            # 获取审批者
            responder = get_responder(request)
            if responder is None:
                validated_data['status'] = AbsentStatusChoices.PASS
            else:
                validated_data['status'] = AbsentStatusChoices.AUDTING
            absent = Absent.objects.create(**validated_data, requester=user, responder=responder)
            return absent
        except Exception as e:
            raise exceptions.ValidationError(f"错误：{str(e)}")

    # 重写update方法
    def update(self, instance, validated_data):
        if instance.status != AbsentStatusChoices.AUDTING:
            raise exceptions.APIException(detail='不能修改已经确定的请假数据！')
        request = self.context['request']
        user = request.user
        if user.department.leader.uid != user.uid:
            raise exceptions.APIException(detail='您无权处理该考勤！')
        instance.status = validated_data['status']
        instance.response_content = validated_data['response_content']
        instance.save()
        return instance
