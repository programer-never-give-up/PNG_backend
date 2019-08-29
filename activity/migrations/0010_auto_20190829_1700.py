# Generated by Django 2.2.4 on 2019-08-29 17:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0009_auto_20190829_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='type',
            field=models.CharField(blank=True, default='其他', max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='uuid',
            field=models.CharField(auto_created=True, default=uuid.uuid1, editable=False, max_length=64, primary_key=True, serialize=False),
        ),
    ]