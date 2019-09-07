from django.db import models


# Create your models here.

class On_site(models.Model):
    #uuid_act = models.CharField(max_length=64,null=True, blank=True)
    #uuid_user = models.CharField(max_length=64,null=True, blank=True)
    activity = models.ForeignKey(max_length=64,db_column='uuid_act',to='activity.Activity', to_field='uuid', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(max_length=64,db_column='uuid_user',to='login.User', to_field='uuid', null=True, on_delete=models.CASCADE)
