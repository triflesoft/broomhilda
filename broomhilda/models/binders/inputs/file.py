from broomhilda.models.binders.inputs.base import NullableInputBase


class FileInput(NullableInputBase):# pylint: disable=R0903
    def __init__(self, **kwargs):
        super().__init__('inputs_file', 'file', **kwargs)

    def _parse_value(self, raw_data, default):
        result = None
        errors = []

        if raw_data is None:
            if not self.is_nullable:
                errors.append('No value specified.')

            result = default
        else:
            result = raw_data

        return result, errors

    def _validate_item_update(self, form_raw_data):
        default_dict = self.default_item_update() if callable(self.default_item_update) else self.default_item_update
        default_value = None if default_dict is None else default_dict.get('value', None)
        value_result, value_errors = self._parse_value(form_raw_data.get(self.name), default_value)

        return {'value': value_result}, {'value': value_errors}

    def _validate_list_filter(self, form_raw_data): # pylint: disable=R0201,W0613
        return {}, {}
