from datetime import datetime
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.oaauth.authentications import generate_jwt
from apps.oaauth.serializers import LoginSerializer, OAUserSerializer, ResetPwdSerializer


class LoginView(APIView):
    def post(self, request):
        # 1、验证数据是否可用
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            token = generate_jwt(user)
            return Response({'token': token, 'user': OAUserSerializer(user).data})
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)



     # 关闭认证
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        # 1、验证数据是否可用
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            token = generate_jwt(user)
            return Response({'token': token, 'user': OAUserSerializer(user).data})
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)


class ResetPwdView(APIView):
    # 修改密码必须登录，使用全局的JWTAuthentication + IsAuthenticated，从request.user拿当前用户
    def post(self, request):
        serializer = ResetPwdSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "密码修改成功！"})
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
