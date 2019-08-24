from django.db import models

# Create your models here.

from django.db import models




class User(models.Model):



    username = models.CharField(max_length=128, unique=True)#长度128，不可重复
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)#django内置邮箱类型，唯一
    #type=models.

    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"