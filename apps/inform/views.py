from django.db.models import Q, Prefetch
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from django.http import FileResponse
from django.conf import settings
from urllib.parse import quote
from .models import Inform, InformRead, NoticeAttachment
from .serializers import InformSerializer, InformReadCountSerializer
from rest_framework.response import Response
import os
from rest_framework.parsers import MultiPartParser
import uuid
from django.core.cache import cache

# 通知接口（发布、查看列表、删除，查看通知详情）



class InformViewSet(viewsets.ModelViewSet):
    queryset = Inform.objects.all()
    serializer_class = InformSerializer

    def get_queryset(self):
        qs = self.queryset.select_related('author').prefetch_related(
            Prefetch("reads", queryset=InformRead.objects.filter(user_id=self.request.user.uid)),
            'departments',
            'attachments'
        ).distinct()
        # 列表才做可见范围过滤
        if self.action == "list":
            qs = qs.filter(
                Q(public=True) | Q(departments=self.request.user.department) | Q(author=self.request.user)
            )
        return qs

    def get_object(self):
        obj = super().get_object()
        # 权限判断
        can_view = obj.public or (self.request.user.department in obj.departments.all()) or (
                obj.author == self.request.user)
        if not can_view:
            raise PermissionDenied("无权查看该通知")
        return obj

    # 重写retrieve方法统计阅读量
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['read_count'] = InformRead.objects.filter(inform_id=instance.id).count()
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author.uid == request.user.uid:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


# 通知阅读接口
class ReadInformView(APIView):
    def post(self, request):
        serializer = InformReadCountSerializer(data=request.data)
        if serializer.is_valid():
            inform_id = serializer.validated_data.get("inform_id")
            # 此人已经读过通知
            if InformRead.objects.filter(inform_id=inform_id, user_id=request.user.uid).exists():
                return Response()
            else:
                try:
                    InformRead.objects.create(inform_id=inform_id, user_id=request.user.uid)
                except Exception as e:
                    print(e)
                    return Response(data={"detail": "阅读失败！"}, status=status.HTTP_400_BAD_REQUEST)
                return Response()
        else:
            return Response(data={"detail": list(serializer.errors.values())[0][0]},
                            status=status.HTTP_400_BAD_REQUEST)


# 附件上传接口
class InformAttachmentUploadView(APIView):
    parser_classes = [MultiPartParser]
    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(data={"msg": "缺少文件"}, status=400)
        ext = os.path.splitext(file_obj.name)[1]
        safe_name = f"{uuid.uuid4().hex}{ext}"
        sub_dir = "notice"
        save_dir = settings.MEDIA_ROOT / sub_dir
        save_dir.mkdir(exist_ok=True)
        save_full = save_dir / safe_name
        with open(save_full, "wb+") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        return Response({
            "name": file_obj.name,
            "path": f"{sub_dir}/{safe_name}"
        })


# 附件下载接口
class InformAttachmentDownloadView(APIView):
    def get(self, request, aid):
        try:
            att = NoticeAttachment.objects.select_related("inform").get(id=aid)
            inform = att.inform
            # 复用和通知一样的查看权限！
            can_view = inform.public or (request.user.department in inform.departments.all()) or (
                    inform.author == request.user)
            if not can_view:
                raise PermissionDenied("无权下载该附件")
            # 下载计数+1
            att.download_count += 1
            att.save()

            full_path = settings.MEDIA_ROOT / att.file_path
            f = open(full_path, "rb")
            resp = FileResponse(f)
            # 中文文件名兼容
            resp["Content-Disposition"] = f'attachment; filename="{quote(att.name)}"'
            return resp
        except NoticeAttachment.DoesNotExist:
            return Response(data={"msg": "附件不存在"}, status=status.HTTP_404_NOT_FOUND)

class LatestInformView(APIView):
    def get(self, request):
        current_user = request.user

        informs = (
            Inform.objects
            .prefetch_related(
                Prefetch("reads", queryset=InformRead.objects.filter(user=current_user)),
                'departments'
            )
            .filter(Q(public=True) | Q(departments=current_user.department))
            .distinct()
            [:5]
        )
        serializer = InformSerializer(informs, many=True)
        return Response(serializer.data)