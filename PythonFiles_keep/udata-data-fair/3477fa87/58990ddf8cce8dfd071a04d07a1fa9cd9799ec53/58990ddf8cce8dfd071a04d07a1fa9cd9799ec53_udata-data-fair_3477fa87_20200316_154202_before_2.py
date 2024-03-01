# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from udata.core.dataset.preview import PreviewPlugin
from udata.core.dataset.models import Resource

class DataFairPreview(PreviewPlugin):
    def can_preview(self, resource):
        if not isinstance(resource, Resource):
            return
        dataset = resource.dataset
        if (not (dataset.extras.get('datafairDatasetId') and dataset.extras.get('datafairOrigin'))) and (not (resource.extras.get('datafairDatasetId') and resource.extras.get('datafairOrigin'))):
            return
        return resource.extras.get('datafairEmbed') or resource.extras.get('apidocUrl')

    def preview_url(self, resource):
        dataset = resource.dataset
        if resource.extras.get('datafairEmbed'):
            return '{origin}/embed/dataset/{datasetId}/{embed}'.format(
                origin=(resource.extras.get('datafairOrigin') or dataset.extras.get('datafairOrigin')),
                datasetId=(resource.extras.get('datafairDatasetId') or dataset.extras.get('datafairDatasetId')),
                embed=resource.extras.get('datafairEmbed')
            )
        elif resource.extras.get('apidocUrl'):
            return 'https://koumoul.com/openapi-viewer/?proxy=false&hide-toolbar=true&url={url}'.format(
                url=resource.extras.get('apidocUrl')
            )
