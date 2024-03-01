# -*- coding: utf-8 -*-
from django.db import migrations

app = 'model_logging'
model = 'LogEntry'


def move_data(apps, schema_editor):
    try:
        from pgcrypto.fields import TextPGPPublicKeyField
    except ImportError:
        raise ImportError('Please install django-pgcrypto-fields to perform migration')

    LogEntry = apps.get_model(app, model)
    for entry in LogEntry.objects.all():
        entry.data_temp = entry.data
        entry.save()

def move_data_back(apps, schema_editor):
    try:
        from pgcrypto.fields import TextPGPPublicKeyField
    except ImportError:
        raise ImportError('Please install django-pgcrypto-fields to perform migration')

    LogEntry = apps.get_model(app, model)
    for entry in LogEntry.objects.all():
        entry.data = entry.data_temp
        entry.save()

class Migration(migrations.Migration):

    dependencies = [
        ('model_logging', '0002_add_new_data_field'),
    ]

    operations = [
        migrations.RunPython(move_data reverse_code=move_data_back),
    ]
