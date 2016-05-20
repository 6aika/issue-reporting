# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-18 07:25
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
            name='IssueMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='i/%Y/%Y%m/%Y%m%d')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='issues.Issue')),
            ],
        ),
    ]