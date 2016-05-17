# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-17 13:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('issues', '0002_mod'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue_CitySDK',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_object_id', models.CharField(blank=True, max_length=100)),
                ('service_object_type', models.CharField(blank=True, max_length=100)),
                ('title', models.CharField(blank=True, max_length=120)),
                ('detailed_status', models.TextField(blank=True)),
                ('issue', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='citysdk', to='issues.Issue')),
            ],
            options={
                'verbose_name_plural': 'issue CitySDK extensions',
                'db_table': 'issue_citysdk_ext',
                'verbose_name': 'issue CitySDK extension',
            },
        ),
    ]
