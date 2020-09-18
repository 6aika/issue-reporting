# Generated by Django 1.9.6 on 2016-06-14 12:02

from django.db import migrations, models
import django.db.models.deletion
import issues_geometry.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('issues', '0006_applications'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueGeometry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geometry', issues_geometry.models.ConfigurableGeometryField()),
                ('issue', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='geometry', to='issues.Issue')),
            ],
        ),
    ]
