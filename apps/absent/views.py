from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.absent.utils import get_responder
from apps.absent.models import AbsentStatusChoices, AbsentType, Absent
from apps.absent.serializers import AbsentSerializer, AbsentTypeSerializer
from apps.oaauth.serializers import OAUserSerializer


class AbsentViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Absent.objects.all()
    serializer_class = AbsentSerializer

    # 重写update方法
    def update(self, request, *args, **kwargs):
        # 默认修改时，所有字段都要传
        # 如果只传一部分，则设置kwargs['partial']=True
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    # 重写了ListModelMixin中的list方法
    def list(self, request, *args, **kwargs):
        # 重写list方法，实现发送get时，不是显示全部，而是显示自己的或者下属的
        # 查看下属请假列表：http://127.0.0.1:8000/absent?who=sub
        # 查看自己的请假列表：http://127.0.0.1:8000/absent?who=
        queryset = self.get_queryset()
        who = request.query_params.get('who')
        if who and who == 'sub':
            result = queryset.filter(responder=request.user)
        else:
            result = queryset.filter(requester=request.user)
        # pageinate_queryset方法，会做分页逻辑处理
        page = self.paginate_queryset(result)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # get_paginated_response除了返回序列化的数据外，还会返回有多少数据，上一步url...
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(result, many=True)
        return Response(data=serializer.data)


# 1.获取请假类型
class AbsentTypeView(APIView):
    def get(self, request):
        types = AbsentType.objects.all()
        serializer = AbsentTypeSerializer(types, many=True)
        return Response(data=serializer.data)

    def post(self, request):
        # 新增请假类型
        serializer = AbsentTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# 2.显示审批人
class ResponderView(APIView):
    def get(self, request):
        responder = get_responder(request)
        serializer = OAUserSerializer(responder)
        return Response(data=serializer.data)
