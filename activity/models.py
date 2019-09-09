from django.db import models
from django.utils import timezone
import uuid
# Create your models here.
class Activity(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)  # 会议名称，长度128，可重复
    type = models.CharField(max_length=64, null=True, blank=True, default='其他')  # 会议类型
    status_process = models.CharField(max_length=64, null=True, blank=True, default='not_start')  # 会议状态
    status_publish = models.CharField(max_length=64, null=True, blank=True, default='unpublished')  # 会议状态
    start_time = models.CharField(max_length=64, null=True, blank=True)  # 开始时间
    end_time = models.CharField(max_length=64, null=True, blank=True)  # 结束时间
    location = models.CharField(max_length=128, null=True, blank=True)  # 会议地点
    organizer = models.CharField(max_length=128, null=True, blank=True)  # 主办方
    username = models.CharField(max_length=128, null=True, blank=True)  # 创建者
    logo = models.CharField(max_length=256, null=True, blank=True)  # 会议logo
    introduction = models.CharField(max_length=256, default='这个人很懒，什么都没有留下。', null=True,
                                    blank=True)  # 会议介绍
    uuid = models.CharField(max_length=64, primary_key=True, auto_created=True, default=uuid.uuid1,
                            editable=False)  # uuid为主键
    c_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name


class UploadRecord(models.Model):
    #act_uuid = models.CharField(max_length=64, null=True, blank=True)
    file_name = models.CharField(max_length=128, null=True, blank=True)
    file_path = models.CharField(max_length=256, null=True, blank=True)
    activity = models.ForeignKey(max_length=64,db_column='act_uuid',to='Activity', to_field='uuid', null=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.file_name

class OldInfo(models.Model):
    logo = models.CharField(max_length=256, null=True, blank=True)  # 会议logo
    name = models.CharField(max_length=128, null=True, blank=True)  # 会议名称
    type = models.CharField(max_length=64, null=True, blank=True)  # 会议类型
    start_time = models.CharField(max_length=64, null=True, blank=True)  # 开始时间
    end_time = models.CharField(max_length=64, null=True, blank=True)  # 结束时间
    location = models.CharField(max_length=128, null=True, blank=True)  # 会议地点
    organizer = models.CharField(max_length=128, null=True, blank=True)  # 主办方
    introduction = models.CharField(max_length=256, null=True, blank=True)  # 会议介绍
    uuid = models.CharField(max_length=64, null=True, blank=True)  # uuid
    c_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)


    def __str__(self):
        return self.name

class AdminActivity(models.Model):
    #uuid = models.CharField(max_length=64, null=True, blank=True)  # uuid
    action = models.CharField(max_length=64, null=True, blank=True)  # 操作：发布 修改 删除
    activity = models.ForeignKey(max_length=64,db_column='uuid',to='Activity', to_field='uuid', null=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.action
