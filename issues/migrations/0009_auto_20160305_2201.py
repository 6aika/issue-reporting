# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-05 22:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('issues', '0008_auto_20160305_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formfiles',
            name='form_id',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]