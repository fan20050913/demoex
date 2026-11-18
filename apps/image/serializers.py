from rest_framework import serializers
from .models import Banner


class BannerSerializer(serializers.ModelSerializer):
    # 返回图片完整访问地址
    image_url = serializers.SerializerMethodField()
    # 重点：手动声明is_active字段，设置default=True
    is_active = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = Banner
        fields = ["id", "title", "image", "image_url", "link", "is_active", "create_time"]
        read_only_fields = ["id", "create_time"]

    def get_image_url(self, obj):
        # 拼接完整url给前端
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
