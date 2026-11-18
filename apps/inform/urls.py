from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name='inform'

router = DefaultRouter(trailing_slash=False)
router.register('inform', views.InformViewSet, basename='inform')

urlpatterns = [
    path('inform/read', views.ReadInformView.as_view(), name='inform_read'),
    path("inform/attachment/download/<int:aid>", views.InformAttachmentDownloadView.as_view(), name="attachment-download"),
    path("inform/attachment/upload", views.InformAttachmentUploadView.as_view(), name="attachment-upload"),
    # 新增：最新通知接口
    path('latest/inform', views.LatestInformView.as_view()),
] + router.urls
