# Generated by Django 2.2.4 on 2019-08-29 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0005_activity_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadrecord',
            name='act_uuid',
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
    ]