from broomhilda.models.binders.inputs.base import NullableInputBase


class TextInputBase(NullableInputBase):
    def __init__(self, jinja2_module_name, jinja2_macro_name, max_length, **kwargs):
        super().__init__(jinja2_module_name, jinja2_macro_name, **kwargs)
        self.max_length = max_length

    def _parse_value(self, raw_data, default):
        result = None
        errors = []

        if raw_data is None:
            if not self.is_nullable:
                errors.append('No value specified.')

            result = default
        else:
            result = str(raw_data)

            if len(result) > self.max_length:
                errors.append(f'Length must be less than {self.max_length}.')

        return result, errors

    def _parse_filter(self, raw_data, default):
        result = None
        errors = []

        if raw_data is None:
            result = default
        else:
            result = str(raw_data)

            if len(result) > self._max_filter_length:
                errors.append(f'Length must be less than {self._max_filter_length}.')

        return result, errors

    def _validate_item_update(self, form_raw_data):
        default_dict = self.default_item_update() if callable(self.default_item_update) else self.default_item_update
        default_value = '' if default_dict is None else default_dict.get('value', '')
        value_result, value_errors = self._parse_value(form_raw_data.get(self.name), default_value)

        return {'value': value_result}, {'value': value_errors}

    def _validate_list_filter(self, form_raw_data):
        default_dict = self.default_item_update() if callable(self.default_item_update) else self.default_item_update
        default_value = '' if default_dict is None else default_dict.get('value', '')
        value_result, value_errors = self._parse_filter(form_raw_data.get(self.name), default_value)

        return {'value': value_result}, {'value': value_errors}


class EMailInput(TextInputBase):
    def __init__(self, max_length=255, **kwargs):
        super().__init__('inputs_text', 'email', max_length, **kwargs)


class HiddenInput(TextInputBase):
    def __init__(self, max_length=255, **kwargs):
        super().__init__('inputs_text', 'hidden', max_length, **kwargs)


class PasswordInput(TextInputBase):
    def __init__(self, max_length=255, **kwargs):
        super().__init__('inputs_text', 'password', max_length, **kwargs)


class SearchInput(TextInputBase):
    def __init__(self, max_length=255, **kwargs):
        super().__init__('inputs_text', 'search', max_length, **kwargs)


class TextInput(TextInputBase):
    def __init__(self, max_length=255, **kwargs):
        super().__init__('inputs_text', 'text', max_length, **kwargs)


class UrlInput(TextInputBase):
    def __init__(self, **kwargs):
        super().__init__('inputs_text', 'url', 8192, **kwargs)
