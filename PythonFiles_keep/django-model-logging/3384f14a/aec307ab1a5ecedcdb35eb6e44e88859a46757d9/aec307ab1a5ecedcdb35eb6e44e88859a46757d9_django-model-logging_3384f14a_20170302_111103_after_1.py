# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('model_logging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='LogEntry',
            name='data_temp',
            field=models.TextField(default=''),
        ),
    ]
