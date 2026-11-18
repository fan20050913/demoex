import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
from django.shortcuts import render
from rest_framework import serializers
from .models import Banner
from django.core.validators import FileExtensionValidator, get_available_image_extensions

# Create your views here.
from rest_framework import viewsets
from .models import Banner
from .serializers import BannerSerializer


class BannerViewSet(viewsets.ModelViewSet):
    # 轮播图管理接口
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    pagination_class = None

    # 列表接口默认只返回启用的轮播图
    def get_queryset(self):
        qs = super().get_queryset()
        # 如果是列表查询，过滤is_active=True，按创建时间倒序，取前3条
        if self.action == "list":
            qs = qs.filter(is_active=True).order_by("-create_time")[:3]
        return qs


class UploadImageView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'msg': '没有上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        save_path = os.path.join(settings.MEDIA_ROOT, file.name)
        with open(save_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        url = settings.MEDIA_URL + file.name
        return Response({'url': url})


class UploadImageSerializer(serializers.Serializer):
    # ImageField: 会校验上传的文件是否是图片
    image = serializers.ImageField(
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'gif'])],
        error_messages={'required': '请上传图片！', 'invalid_image': '请上传正确格式的图片'}
    )

    def validate_image(self, value):
        max_size = 1*1024*1024
        size = value.size
        if size > max_size:
            raise serializers.ValidationError('图片最大不能超过1MB！')
        return value

class UploadImageView(APIView):
    def post(self, request):
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('image')
            # abc.png => saddffff.png
            # os.path.splitext("abc.png")=('abc','png')
            filename = uuid() + os.path.splitext(file.name)[1]
            path = settings.MEDIA_ROOT / filename
            try:
                with open(path, 'wb') as fp:
                    for chunk in file.chunks():
                        fp.write(chunk)
            except Exception:
                return Response({
                    'error': 1,
                    'message': '图片保存失败！'
                })

            # abc.png => /media/abc.png
            file_url = settings.MEDIA_URL + filename
            return Response({
                'errno': 0,
                'data': {
                    'url': file_url,
                    'alt': '',
                    'href': file_url,
                }
            })
        else:
            return Response({
                'error': 1,
                'message': list(serializer.errors.values())[0][0]
            })

