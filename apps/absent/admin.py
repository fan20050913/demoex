from .models import Absent, AbsentType  # 导入你自己的模型
from DjangoProject02.admin_site import oa_admin_site

# 必须写注册代码！不写后台就看不到
oa_admin_site.register(Absent)
oa_admin_site.register(AbsentType)
