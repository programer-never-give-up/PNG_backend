from django.db import models
import  globals
# Create your models here.

class activity_sign_up(models.Model):
    uuid_act = models.CharField(max_length=64, null=True, blank=True)
    uuid_user = models.CharField(max_length=64, null=True, blank=True)
    qr_code=models.CharField(max_length=256, null=True, blank=True)

class user_collection(models.Model):
    uuid_act = models.CharField(max_length=64, null=True, blank=True)
    uuid_user = models.CharField(max_length=64, null=True, blank=True)

class recent_activity(models.Model):
    uuid_act = models.CharField(max_length=64, null=True, blank=True)

class recommended_activity(models.Model):
    uuid_act=models.CharField(max_length=64, null=True, blank=True)
    stay_length=models.IntegerField(max_length=30*globals.hours_per_day, null=True, blank=True)
    #停留时长以小时为单位，最多三十天

