"""
This module implements the functionality for request body deserialization.
API handler classes can inherit the functionality of any of these mixins.
"""
from django.core.exceptions import ValidationError
from django.db.models import Model


class ModelValidationMixin(object):
    """
    Provides functionality for converting a dict of data or list of dicts, to
    clean model instances
    """
    def validate(self, data, model_class, allowed_fields=[],
                 clean=True, exclude=None):
        """
        Args:
          - data (dict or list of dicts): Data to convert to ``model_class``
            instances
          - model_class (Django model class): Model class to which the ``data``
            wll be converted
          - allowed_fields (list): ``data`` fields which will be converted
            (for example, for security you might not want the ``id`` field to
             be specified, right?)
          - clean (bool): Specifies whether ``full_clean`` should be applied
          - exclude (list): ``model_class`` fields which should be
            excluded from the ``full_clean``

        Returns:
          - An instance of ``model`` or a list of instances

        Raises:
          - ValidationError: In case the ``full_clean`` method applied on any
            of the models, raises a ValidationError

        """
        models = self._modelize(data, model_class, allowed_fields)
        if clean:
            try:
                self._clean(models, exclude)
            except ValidationError:
                raise
        return models

    def _modelize(self, data, model_class, allowed_fields):
        if isinstance(data, dict):
            return self._modelize_dict(data, model_class, allowed_fields)
        return self._modelize_list(data, model_class, allowed_fields)

    def _modelize_dict(self, data, model_class, allowed_fields):
        data = {
            key: value for key, value in data.items() if key in allowed_fields
        }
        return model_class(**data)

    def _modelize_list(self, data, model_class, allowed_fields):
        return [
            self._modelize_dict(item, model_class, allowed_fields)
            for item in data
        ]

    def _clean(self, models, exclude):
        if isinstance(models, Model):
            try:
                self._clean_model(models, exclude)
            except ValidationError:
                raise
        else:
            try:
                self._clean_models(models, exclude)
            except ValidationError:
                raise

    def _clean_model(self, model, exclude):
        try:
            model.full_clean(exclude=exclude)
        except ValidationError:
            raise

    def _clean_models(self, models, exclude):
        for model in models:
            try:
                self._clean_model(model, exclude)
            except ValidationError:
                raise
