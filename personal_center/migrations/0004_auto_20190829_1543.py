# Generated by Django 2.2.4 on 2019-08-29 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_center', '0003_auto_20190829_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='on_site',
            name='uuid_act',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='on_site',
            name='uuid_user',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
