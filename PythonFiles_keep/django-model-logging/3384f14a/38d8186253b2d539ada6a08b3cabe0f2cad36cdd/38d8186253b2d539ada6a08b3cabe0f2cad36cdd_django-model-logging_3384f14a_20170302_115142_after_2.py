# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('model_logging', '0001_initial'), ('model_logging', '0002_add_new_data_field'), ('model_logging', '0003_data_migration'), ('model_logging', '0004_remove_old_field')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('operation', models.CharField(max_length=255, choices=[('added', 'Added'), ('removed', 'Removed'), ('modified', 'Modified')])),
                ('model_path', models.CharField(max_length=255)),
                ('data', models.TextField(default='')),
                ('creator', models.ForeignKey(related_name='log_entries_created', to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='log_entries', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('date_created',),
            },
        ),
    ]
