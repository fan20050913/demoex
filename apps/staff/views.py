from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.oaauth.models import OADepartment, UserStatusChoices
from apps.oaauth.serializers import OADepartmentSerializer
from apps.staff.serializers import AddStaffSerializer, ActiveStaffSerializer
from django.core.mail import send_mail
from django.conf import settings
from utils import aeser

OAUser = get_user_model()
aes = aeser.AESCipher(settings.SECRET_KEY)


# 显示部门接口
class DepartmentListView(ListAPIView):
    queryset = OADepartment.objects.all()
    serializer_class = OADepartmentSerializer
    # `ListAPIView`会全局读取DRF的分页配置,如果不想分页，可添加下行代码关闭分页
    pagination_class = None

    # 激活员工的过程：
    # 1. 用户访问激活的链接的时候，会返回一个含有表单的页面，视图中可以获取到token，为了在用户提交表单的时候，post函数中能知道这个token
    # 我们可以在返回页面之前，先把token存储在cookie中
    # 2. 校验用户上传的邮箱和密码是否正确，并且解密token中的邮箱，与用户提交的邮箱进行对比，如果都相同，那么就是激活成功


# 激活员工接口
class ActiveStaffView(APIView):
    # 关闭认证
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        # 获取token，并把token存储到cookie中，方便下次用户传过来
        # http://127.0.0.1:8000/staff/active?token=6AkzQXz+uIIlV/+I6gXMitowszWkiiDIj9J/XBfctIY=
        token = request.GET.get('token')
        try:
            email = aes.decrypt(token)
        except Exception as e:
            print("get解密异常：", e)
            email = ""
        response = render(request, 'active.html', context={"email": email})
        response.set_cookie('token', token, max_age=3600 * 24)
        return response

    def post(self, request):
        # 从cookie中获取token
        try:
            token = request.COOKIES.get('token')
            email = aes.decrypt(token)
            serializer = ActiveStaffSerializer(data=request.data)
            if serializer.is_valid():
                form_email = serializer.validated_data.get('email')
                user = serializer.validated_data.get('user')
                if email != form_email:
                    return JsonResponse({"code": 400, "message": "邮箱错误！"})
                user.status = UserStatusChoices.ACTIVED
                user.save()
                return JsonResponse({"code": 200, "message": ""})
            else:
                detail = list(serializer.errors.values())[0][0]
                return JsonResponse({"code": 400, "message": detail})
        except Exception as e:
            print(e)
            return JsonResponse({"code": 400, "message": "token错误！"})


# 员工接口
class StaffView(APIView):
    # 员工列表
    def get(self, request):
        # 解密出邮箱（注意，以下是我的邮箱收到的激活token,请测试时自行更换）
        token = 'TRJBaY6BnBH8b8DvtL+u4ZGM0wplgMVDMNlMMzUKXkGmJIuScekbJaIynKcMHZRX'
        result = aes.decrypt(token)
        return Response(data={'email': result})

    # 新增员工
    def post(self, request):
        # 如果继承的ViewSet，会自动将request赋给context
        # 如果继承的是APIView,则需要手动传值
        serializer = AddStaffSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            realname = serializer.validated_data['realname']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # 保存用户数据
            user = OAUser.objects.create_user(email=email, password=password, realname=realname)
            department = request.user.department
            user.department = department
            user.save()

            # 发送email
            self.send_active_email(email)

            return Response({
                "code": 200,
                "message": "员工添加成功！",
                "data": {
                    "uid": user.uid  # 可以把新建员工的uid返回去，方便前端使用
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response(data={'detail': list(serializer.errors.values())[0][0]}, status=status.HTTP_400_BAD_REQUEST)

    def send_active_email(self, email):
        token = aes.encrypt(email)
        # /staff/active?token=xxx（reverse：通过路由的名字获取路由url)
        active_path = reverse("staff:active_staff") + "?token=" + token
        # http://127.0.0.1:8000/staff/active?token=xxx
        active_url = self.request.build_absolute_uri(active_path)
        # 发送一个链接，让用户点击这个链接后，跳转到激活的页面，才能激活。
        # 为了区分用户，在发送链接邮件中，该链接中应该要包含这个用户的邮箱
        # 针对邮箱要进行加密：AES
        # http://127.0.0.1:8000/staff/active?token=TRJBaY6BnBH8b8DvtL+u4ZGM0wplgMVDMNlMMzUKXkGmJIuScekbJaIynKcMHZRX
        message = f"请点击以下链接激活账号：{active_url}"
        send_mail(f'用户账号激活', recipient_list=[email], message=message,
                  from_email=settings.DEFAULT_FROM_EMAIL)

