from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password
from shortuuidfield import ShortUUIDField
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.utils import timezone


class UserStatusChoices(models.IntegerChoices):
    ACTIVED = 1
    UNACTIVE = 2
    LOCKED = 3


class OAUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user_object(self, realname, email, password, **extra_fields):
        if not realname:
            raise ValueError("必须添加真实姓名")
        email = self.normalize_email(email)
        user = self.model(realname=realname, email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, realname, email, password, **extra_fields):
        user = self._create_user_object(realname, email, password, **extra_fields)
        user.save(using=self._db)
        return user

    async def _acreate_user(self, realname, email, password, **extra_fields):
        user = self._create_user_object(realname, email, password, **extra_fields)
        await user.asave(using=self._db)
        return user

    def create_user(self, realname, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(realname, email, password, **extra_fields)

    create_user.alters_data = True

    async def acreate_user(self, realname, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await self._acreate_user(realname, email, password, **extra_fields)

    acreate_user.alters_data = True

    def create_superuser(self, realname, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatusChoices.ACTIVED)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("超级用户必须设置 is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级用户必须设置 is_superuser=True.")

        return self._create_user(realname, email, password, **extra_fields)

    create_superuser.alters_data = True

    async def acreate_superuser(
            self, realname, email=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return await self._acreate_user(realname, email, password, **extra_fields)

    acreate_superuser.alters_data = True


# 【重点】这个才是你的主用户表，删掉 abstract=True，所有字段缩进在这个类内部！
class OAUser(AbstractBaseUser, PermissionsMixin):
    uid = ShortUUIDField(primary_key=True)
    realname = models.CharField(max_length=150, unique=False)
    email = models.EmailField(unique=True, blank=False)
    telephone = models.CharField(max_length=11, blank=True)
    is_staff = models.BooleanField(default=True)
    status = models.IntegerField(choices=UserStatusChoices.choices, default=UserStatusChoices.UNACTIVE)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    department = models.ForeignKey("OADepartment", null=True, on_delete=models.SET_NULL,
                                   related_name="staffs", related_query_name="staffs")

    objects = OAUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["realname"]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.realname

    def get_short_name(self):
        return self.realname

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'


class OADepartment(models.Model):
    name = models.CharField(max_length=100)
    intro = models.CharField(max_length=200)
    leader = models.OneToOneField(OAUser, null=True, on_delete=models.SET_NULL,
                                  related_name="leader_department", related_query_name="leader_department")
    manager = models.ForeignKey(OAUser, null=True, on_delete=models.SET_NULL,
                                related_name="manager_departments", related_query_name="manager_departments")

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门管理'
