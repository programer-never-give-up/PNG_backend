# Generated by Django 2.2.4 on 2019-09-01 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yw', '0003_recent_activity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity_sign_up',
            name='qr_code',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
