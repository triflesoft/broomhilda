from broomhilda.models.binders.inputs.base import NullableInputBase


class ChoiceInputBase(NullableInputBase): # pylint: disable=R0903
    def __init__(self, jinja2_module_name, jinja2_macro_name, **kwargs):
        super().__init__(jinja2_module_name, jinja2_macro_name, **kwargs)

    def _parse_value(self, raw_data, default):
        result = None
        errors = []

        if raw_data is None:
            if not self.is_nullable:
                errors.append('No value specified.')

            result = default
        else:
            if raw_data in self.choices:
                result = raw_data
            else:
                result = None
                errors.append(f'Invalid value ({raw_data}).')

        return result, errors

    def _parse_filter(self, raw_data, default):
        result = None
        errors = []

        if raw_data is None:
            result = default
        else:
            raw_data = str(raw_data)

            if raw_data in self.choices:
                result = raw_data
            else:
                errors.append(f'Invalid value ({raw_data}).')

        if (result is None) and (not self.is_nullable):
            result = default

        return result, errors

    def _validate_item_update(self, form_raw_data):
        default_dict = self.default_item_update() if callable(self.default_item_update) else self.default_item_update
        default_value = None if default_dict is None else default_dict.get('value')

        if default_value is None:
            for key in self.choices.keys():
                default_value = key
                break

        value_result, value_errors = self._parse_value(form_raw_data.get(self.name), default_value)

        return {'value': value_result}, {'value': value_errors}

    def _validate_list_filter(self, form_raw_data):
        default_dict = self.default_list_filter() if callable(self.default_list_filter) else self.default_list_filter
        result = {}
        errors = {}

        for choice_name in self.choices:
            if choice_name:
                default_choice = False if default_dict is None else default_dict.get('value', False)
                choice_result, choice_errors = self._parse_filter(form_raw_data.get(self.name + ':' + choice_name), default_choice)
                result[choice_name] = choice_result
                errors[choice_name] = choice_errors

        return result, errors


class RadioInput(ChoiceInputBase): # pylint: disable=R0903
    def __init__(self, **kwargs):
        super().__init__('inputs_choice', 'radio', **kwargs)


class SelectInput(ChoiceInputBase): # pylint: disable=R0903
    def __init__(self, size=1, **kwargs):
        super().__init__('inputs_choice', 'select', **kwargs)
        self.size = size
