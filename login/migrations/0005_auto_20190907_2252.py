# Generated by Django 2.2.4 on 2019-09-07 22:52

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0004_auto_20190906_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.CharField(auto_created=True, default=uuid.uuid1, editable=False, max_length=64, primary_key=True, serialize=False),
        ),
    ]