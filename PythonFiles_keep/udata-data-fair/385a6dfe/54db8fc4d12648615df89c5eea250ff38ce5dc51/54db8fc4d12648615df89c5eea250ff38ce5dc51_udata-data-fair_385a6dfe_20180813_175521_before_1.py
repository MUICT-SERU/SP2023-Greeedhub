# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from udata.core.dataset.preview import PreviewPlugin
from udata.core.dataset.models import Resource

class DataFairPreview(PreviewPlugin):
    def can_preview(self, resource):
        if not isinstance(resource, Resource):
            return
        dataset = resource.dataset
        if not (dataset.extras.get('datafairDatasetId') and dataset.extras.get('datafairOrigin')):
            return
        return True

    def preview_url(self, resource):
        dataset = resource.dataset
        return '{origin}/datasets/{datasetId}/tabular'.format(
            origin=dataset.extras.get('datafairOrigin'),
            datasetId=dataset.extras.get('datafairDatasetId')
        )
