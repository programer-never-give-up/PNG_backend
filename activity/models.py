from django.db import models

# Create your models here.
class Activity(models.Model):

    name = models.CharField(max_length=128, null=True, blank=True)  # 会议名称，长度128，可重复
    type = models.CharField(max_length=64, null=True, blank=True)  # 会议类型
    status = models.CharField(max_length=64, null=True, blank=True)  # 会议状态
    start_time = models.DateTimeField(auto_now_add=True)  # 开始时间
    end_time = models.DateTimeField(auto_now_add=True)  # 结束时间
    location = models.CharField(max_length=128, null=True, blank=True)  # 会议地点
    organizer = models.CharField(max_length=128, null=True, blank=True)  # 会议地点
    logo = models.CharField(max_length=256, null=True, blank=True)  # 会议logo
    introduction = models.CharField(max_length=256, default='这个人很懒，什么都没有留下。', null=True, blank=True)  # 会议介绍
    uuid = models.CharField(max_length=128, unique=True, null=True, blank=True)  # 长度128，不可重复
