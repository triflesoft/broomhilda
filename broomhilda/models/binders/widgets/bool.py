from broomhilda.models.binders.widgets.base import WidgetBase


class CheckboxWidget(WidgetBase):  # pylint: disable=R0903
    def __init__(self, **kwargs):
        super().__init__('widgets_bool', 'checkbox', **kwargs)

    def _parse_value(self, raw_data, default):  # pylint: disable=R0201
        result = None
        errors = []

        if raw_data is None:
            result = default
        else:
            if raw_data is True or raw_data is False:
                result = raw_data
            else:
                raw_data = str(raw_data).lower()

                if raw_data in ('t', 'true', 'on', 'yes', '1', 'checked'):
                    result = True
                elif raw_data in ('f', 'false', 'off', 'no', '0'):
                    result = False
                else:
                    result = None
                    errors.append(f'Invalid value ({raw_data}).')

        return result, errors

    def _validate_item_update(self, form_raw_data):
        default_dict = self.default_item_update() if callable(self.default_item_update) else self.default_item_update
        default_value = False if default_dict is None else default_dict.get('value', False)
        value_result, value_errors = self._parse_value(form_raw_data.get(self.name), default_value)

        return {'value': value_result}, {'value': value_errors}

    def _validate_list_filter(self, form_raw_data):
        default_dict = self.default_list_filter() if callable(self.default_list_filter) else self.default_list_filter
        default_none = False if default_dict is None else default_dict.get('none', False)
        default_true = False if default_dict is None else default_dict.get('true', False)
        default_false = False if default_dict is None else default_dict.get('false', False)

        none_result, none_errors = self._parse_value(form_raw_data.get(self.name + ':none'), default_none)
        true_result, true_errors = self._parse_value(form_raw_data.get(self.name + ':true'), default_true)
        false_result, false_errors = self._parse_value(form_raw_data.get(self.name + ':false'), default_false)

        return {'none': none_result, 'true': true_result, 'false': false_result}, {'none': none_errors, 'true': true_errors, 'false': false_errors}
