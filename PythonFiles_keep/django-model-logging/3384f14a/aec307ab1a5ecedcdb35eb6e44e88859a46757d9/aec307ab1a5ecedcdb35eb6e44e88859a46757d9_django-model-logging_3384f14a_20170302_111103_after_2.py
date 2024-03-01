# -*- coding: utf-8 -*-
from django.db import migrations

app = 'model_logging'
model = 'LogEntry'


def move_data(apps, schema_editor):
    LogEntry = apps.get_model(app, model)
    for entry in LogEntry.objects.all():
        entry.data_temp = entry.data
        entry.save()

class Migration(migrations.Migration):

    dependencies = [
        ('model_logging', '0002_add_new_data_field'),
    ]

    operations = [
        migrations.RunPython(move_data),
    ]
