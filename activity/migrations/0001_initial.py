# Generated by Django 2.2.4 on 2019-08-26 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='未命名', max_length=128, null=True)),
                ('type', models.CharField(blank=True, max_length=64, null=True)),
                ('status', models.CharField(blank=True, max_length=64, null=True)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(blank=True, max_length=128, null=True)),
                ('organizer', models.CharField(blank=True, max_length=128, null=True)),
                ('logo', models.CharField(blank=True, max_length=256, null=True)),
                ('introduction', models.CharField(blank=True, max_length=256, null=True)),
            ],
        ),
    ]
