# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-26 21:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0005_auto_20160225_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='synchronized',
            field=models.BooleanField(default=False),
        ),
    ]