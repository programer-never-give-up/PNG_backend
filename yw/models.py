from django.db import models

# Create your models here.

class activity_sign_up(models.Model):
    uuid_act = models.CharField(max_length=64, null=True, blank=True)
    uuid_user = models.CharField(max_length=64, null=True, blank=True)
    qr_code=models.CharField(max_length=128, null=True, blank=True)