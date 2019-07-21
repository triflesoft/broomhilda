from broomhilda.models.binders.inputs.base import NullableInputBase


class NumberInput(NullableInputBase):
    def __init__(self, min_value=0, max_value=100, decimal_places=2, **kwargs):
        super().__init__('inputs_number', 'number', **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.decimal_places = decimal_places
        self.step = 1 / (10 ** decimal_places)

    def _parse_value(self, raw_data, default):
        from decimal import Decimal
        from decimal import InvalidOperation

        result = None
        errors = []

        if raw_data is None:
            if not self.is_nullable:
                errors.append('No value specified.')

            result = default
        else:
            if self.decimal_places == 0:
                try:
                    result = int(raw_data)
                except ValueError:
                    errors.append(f'Invalid value ({raw_data}).')
            else:
                try:
                    result = Decimal(raw_data)
                except InvalidOperation:
                    errors.append(f'Invalid value ({raw_data}).')

        return result, errors

    def _parse_filter(self, raw_data, default):
        from decimal import Decimal
        from decimal import InvalidOperation

        result = None
        errors = []

        if raw_data is None:
            result = default
        else:
            if self.decimal_places == 0:
                try:
                    result = int(raw_data)
                except ValueError:
                    errors.append(f'Invalid value ({raw_data}).')
            else:
                try:
                    result = Decimal(raw_data)
                except InvalidOperation:
                    errors.append(f'Invalid value ({raw_data}).')

        return result, errors

    def _validate_item_update(self, form_raw_data):
        default_dict = self.default_item_update() if callable(self.default_item_update) else self.default_item_update
        default_value = False if default_dict is None else default_dict.get('value', False)
        value_result, value_errors = self._parse_value(form_raw_data.get(self.name), default_value)

        return {'value': value_result}, {'value': value_errors}

    def _validate_list_filter(self, form_raw_data):
        default_dict = self.default_list_filter() if callable(self.default_list_filter) else self.default_list_filter
        default_lower = self.min_value if default_dict is None else default_dict.get('lower', self.min_value)
        default_upper = self.max_value if default_dict is None else default_dict.get('upper', self.max_value)

        lower_result, lower_errors = self._parse_filter(form_raw_data.get(self.name + ':lower'), default_lower)
        upper_result, upper_errors = self._parse_filter(form_raw_data.get(self.name + ':upper'), default_upper)

        return {'lower': lower_result, 'upper': upper_result}, {'lower': lower_errors, 'upper': upper_errors}
