# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('model_logging', '0003_data_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='LogEntry',
            name='data',
        ),
        migrations.RenameField(
            model_name='LogEntry',
            old_name='data_temp',
            new_name='data',
        ),
    ]
