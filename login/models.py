

# Create your models here.

from django.db import models
import uuid
import globals


class User(models.Model):

    username = models.CharField(max_length=128, unique=True,null=True, blank=True)#长度128，不可重复
    password = models.CharField(max_length=256,null=True, blank=True)
    email = models.EmailField(unique=True,null=True, blank=True)#django内置邮箱类型，唯一
    type=models.CharField(max_length=64,null=True, blank=True)#用户类型
    gender=models.CharField(max_length=64,null=True, blank=True)#性别
    address=models.CharField(max_length=256,null=True, blank=True)#个人地址
    company=models.CharField(max_length=256,null=True, blank=True)#单位
    profession=models.CharField(max_length=256,null=True, blank=True)#职业
    phone_number=models.CharField(max_length=256,null=True, blank=True)#电话号码
    introduction=models.CharField(max_length=256,null=True, blank=True,default='这个人很懒，什么都没写。')#个人介绍
    avatar=models.CharField(max_length=256,default='default.png',null=True, blank=True)#头像链接
    uuid = models.CharField(max_length=64,primary_key=True, auto_created=True, default=str(uuid.uuid1()), editable=False)  # uuid为主键

    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"

class Admin(models.Model):
    username = models.CharField(max_length=128, unique=True, null=True, blank=True)  # 长度128，不可重复
    password = models.CharField(max_length=256, null=True, blank=True)

