import jwt
import time
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from jwt.exceptions import ExpiredSignatureError
from apps.oaauth.models import  OAUser

User = get_user_model()


def generate_jwt(user):
    timestamp = time.time() + 60*60*24*7
    # exp是一个特殊的参数，标识token过期的时间
    token = jwt.encode({"userid": user.uid, "exp": timestamp}, key=settings.SECRET_KEY, algorithm='HS256')
    return token

class JWTAuthentication(BaseAuthentication):
    """
    Authorization: jwt 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'JWT'
    model = None

    def authenticate(self, request):
        # auth = [b'jwt', b'401f7ac837da42b97f613d789819ff93537bee6a']
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = '没有提供JWTToken!'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = '无效的JWT! '
            raise exceptions.AuthenticationFailed(msg)
        try:
            jwt_token = auth[1].decode('utf-8')
            payload = jwt.decode(jwt_token, key=settings.SECRET_KEY, algorithms=['HS256'])
            userid = payload['userid']
            try:
                user = OAUser.objects.get(pk=userid)
                setattr(request, 'user', user)
                return (user, jwt_token)
            except Exception:
                msg = '用户信息错误! '
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = 'UnicodeError'
            raise exceptions.AuthenticationFailed(msg)
        except ExpiredSignatureError:
            msg = 'token已过期'
            raise exceptions.AuthenticationFailed(msg)
