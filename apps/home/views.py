from rest_framework.views import APIView
from apps.inform.models import Inform, InformRead
from apps.inform.serializers import InformSerializer
from django.db.models import Q
from django.db.models import Prefetch
from rest_framework.response import Response
from apps.absent.models import Absent
from apps.absent.serializers import AbsentSerializer
from apps.oaauth.models import OADepartment
from django.db.models import Count
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache


# 最新通知
class LatestInformView(APIView):
    """
    返回最新的5条通知
    """

    # @method_decorator(cache_page(60 * 15))
    # def get(self, request):
    #     current_user = request.user
    #     # 返回公共的，或者是我所在的部门能看到的通知
    #     informs = Inform.objects.prefetch_related(Prefetch("reads", queryset=InformRead.objects.filter(user_id=current_user.uid)), 'departments').filter(Q(public=True) | Q(departments=current_user.department))[:5]
    #     serializer = InformSerializer(informs, many=True)
    #     return Response(serializer.data)
    def get(self, request):
        current_user = request.user
        # 缓存key，带上用户id，用户隔离
        cache_key = f"inform_latest_{current_user.uid}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        informs = (
            Inform.objects
            .prefetch_related(
                Prefetch("reads", queryset=InformRead.objects.filter(user_id=current_user.uid)),
                'departments'
            )
            .filter(Q(public=True) | Q(departments=current_user.department))
            [:5]
        )
        serializer = InformSerializer(informs, many=True)
        data = serializer.data
        # 缓存15分钟
        # cache.set(cache_key, data, timeout=60 * 15)
        return Response(data)


# 最新请假
class LatestAbsentView(APIView):

    # @method_decorator(cache_page(60 * 15))
    # def get(self, request):
    #     # 董事会的人，可以看到所有人的考勤信息，非董事会的人，只能看到自己部门的考勤信息
    #     current_user = request.user
    #     queryset = Absent.objects
    #     if current_user.department.name != '董事会':
    #         queryset = queryset.filter(requester__department_id=current_user.department_id)
    #     queryset = queryset.all()[:10]
    #     serializer = AbsentSerializer(queryset, many=True)
    #     return Response(serializer.data)
    def get(self, request):
        current_user = request.user
        # 缓存key：带上用户id，天然隔离不同用户
        cache_key = f"absent_latest_{current_user.uid}"
        # 尝试读取Redis缓存
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return Response(cached_result)

        # 缓存不存在，查询数据库
        queryset = Absent.objects
        if current_user.department.name != '董事会':
            queryset = queryset.filter(requester__department_id=current_user.department_id)
        queryset = queryset.all()[:10]
        serializer = AbsentSerializer(queryset, many=True)
        data = serializer.data

        # 写入Redis，过期时间15分钟
        cache.set(cache_key, data, timeout=60 * 15)
        return Response(data)


# 部门员工统计
class DepartmentStaffCountView(APIView):

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        rows = OADepartment.objects.annotate(staff_count=Count("staffs")).values("name", "staff_count")
        # print(rows)
        print('=' * 10)
        return Response(rows)

