from django.db import models
from django.utils import timezone
import uuid
# Create your models here.
class Activity(models.Model):

    name = models.CharField(max_length=128, null=True, blank=True)  # 会议名称，长度128，可重复
    type = models.CharField(max_length=64, null=True, blank=True)  # 会议类型
    status = models.CharField(max_length=64, null=True, blank=True)  # 会议状态
    start_time = models.CharField(max_length=64,null=True, blank=True)  # 开始时间
    end_time = models.CharField(max_length=64,null=True, blank=True)  # 结束时间
    location = models.CharField(max_length=128, null=True, blank=True)  # 会议地点
    organizer = models.CharField(max_length=128, null=True, blank=True)  # 会议地点
    logo = models.CharField(max_length=256, null=True, blank=True)  # 会议logo
    introduction = models.CharField(max_length=256, default='这个人很懒，什么都没有留下。', null=True,
                                    blank=True)  # 会议介绍
    uuid = models.UUIDField(max_length=64, primary_key=True, auto_created=True, default=uuid.uuid1,
                            editable=False)  # uuid为主键

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-uuid"]
        verbose_name = "活动"
        verbose_name_plural = "活动"

class UploadRecord(models.Model):
    act_uuid = models.UUIDField(max_length=64, primary_key=True)  # uuid为主键
    file_name = models.CharField(max_length=128, null=True, blank=True)
    file_path = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.file_name
