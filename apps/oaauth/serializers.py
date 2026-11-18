from rest_framework import serializers
from apps.oaauth.models import OAUser, UserStatusChoices, OADepartment


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=20, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = OAUser.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError("请输入正确的邮箱！")
            if not user.check_password(password):
                raise serializers.ValidationError("请输入正确的密码")
            # 判断状态
            if user.status == UserStatusChoices.UNACTIVE:
                raise serializers.ValidationError("该用户尚未激活")
            if user.status == UserStatusChoices.LOCKED:
                raise serializers.ValidationError("该已锁定，请联系管理员")
            # 为了节省执行SQL语句的次数，把user直接放到attrs中，方便在视图中使用
            attrs["user"] = user
        else:
            raise serializers.ValidationError("请传入邮箱和密码！")
        return attrs


class ResetPwdSerializer(serializers.Serializer):
    oldpwd = serializers.CharField(max_length=20, min_length=6)
    pwd1 = serializers.CharField(max_length=20, min_length=6)
    pwd2 = serializers.CharField(max_length=20, min_length=6)

    def validate_oldpwd(self, value):
        # 修改密码需要登录，request.user即为当前登录用户
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("请输入正确的原密码！")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['pwd1'])
        user.save()
        return user


class OADepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OADepartment
        fields='__all__'


class OAUserSerializer(serializers.ModelSerializer):
    department=OADepartmentSerializer()
    class Meta:
        model = OAUser
        exclude = ('password', 'groups', 'user_permissions')
