import json

from rest_framework.serializers import (
    CharField,
    Field,
    HyperlinkedModelSerializer,
)

from . import models


class JSONField(Field):
    def to_representation(self, obj):
        return json.loads(obj)


class LogEntrySerializer(HyperlinkedModelSerializer):
    data = JSONField()
    creator = CharField(source='creator.name')
    operation_label = CharField(source='get_operation_display', read_only=True)

    class Meta:
        model = models.LogEntry
        fields = ('url', 'date_created', 'creator', 'operation', 'operation_label', 'data')
        read_only_fields = fields
        view_name = 'medication-history-detail'
