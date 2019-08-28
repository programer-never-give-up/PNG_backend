from django.db import models

# Create your models here.

class On_site(models.Model):
    uuid_act = models.UUIDField(max_length=64,editable=False,null=True, blank=True)
    uuid_user = models.UUIDField(max_length=64,editable=False,null=True, blank=True)

