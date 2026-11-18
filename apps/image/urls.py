from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import BannerViewSet

app_name = 'image'

router = DefaultRouter(trailing_slash=False)
router.register(prefix="banner", viewset=views.BannerViewSet, basename='banner')

urlpatterns = [
    path('upload', views.UploadImageView.as_view(), name='upload'),
] + router.urls
