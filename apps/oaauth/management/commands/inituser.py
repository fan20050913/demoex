from django.core.management.base import BaseCommand
from apps.oaauth.models import OAUser, OADepartment


class Command(BaseCommand):
    def handle(self, *args, **options):
        boarder = OADepartment.objects.get(name="董事会")
        developer = OADepartment.objects.get(name="开发部")
        operater = OADepartment.objects.get(name="运营部")
        saler = OADepartment.objects.get(name="销售部")
        hr = OADepartment.objects.get(name="人事部")
        finance = OADepartment.objects.get(name="财务部")

        # 董事会的员工都是superuser,其余的都是user
        # 1.东东,董事会的leader
        dongdong = OAUser.objects.create_superuser(email="dongdong@qq.com", realname="东东", password="111111", department=boarder)
        # 2.多多,董事会
        duoduo = OAUser.objects.create_superuser(email="duoduo@qq.com", realname="多多", password="111111", department=boarder)
        # 3.张三,开发部的leader
        zhangsan = OAUser.objects.create_user(email="zhangsan@qq.com", realname="张三", password="111111", department=developer)
        # 4.李四,运营部的leader
        lisi = OAUser.objects.create_user(email="lisi@qq.com", realname="李四", password="111111", department=operater)
        # 5.王五,销售部的leader
        wangwu = OAUser.objects.create_user(email="wangwu@qq.com", realname="王五", password="111111", department=saler)
        # 6.赵六,人事部的leader
        zhaoliu = OAUser.objects.create_user(email="zhaoliu@qq.com", realname="赵六", password="111111", department=hr)
        # 7.孙七,财务部的leader
        sunqi = OAUser.objects.create_user(email="sunqi@qq.com", realname="孙七", password="111111", department=finance)
        # 给部门设置leader,manager
        # 东东分管开发部、运营部和销售部，多多分管人事和财务
        boarder.leader = dongdong
        boarder.manager = None

        developer.leader = zhangsan
        developer.manager = dongdong

        operater.leader = lisi
        operater.manager = dongdong

        saler.leader = wangwu
        saler.manager = dongdong

        hr.leader = zhaoliu
        hr.manager = duoduo

        finance.leader = sunqi
        finance.manager = duoduo

        boarder.save()
        developer.save()
        operater.save()
        saler.save()
        hr.save()
        finance.save()
        self.stdout.write("初始化用户完成")

