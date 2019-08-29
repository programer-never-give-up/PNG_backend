from django.db import models

# Create your models here.

class On_site(models.Model):
    uuid_act = models.CharField(max_length=64,null=True, blank=True)
    uuid_user = models.CharField(max_length=64,null=True, blank=True)

