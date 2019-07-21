from datetime import date
from datetime import datetime
from datetime import time

from broomhilda.models.binders.widgets.base import NullableWidgetBase


class DateWidget(NullableWidgetBase): # pylint: disable=R0903
    def __init__(
            self,
            min_value=date.min,
            max_value=date.max,
            date_formats=(
                '%Y-%m-%d',
                '%Y/%m/%d'),
            **kwargs):
        super().__init__('widgets_date', 'date', **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.avg_value = min_value + (max_value - min_value) / 2
        self.date_formats = date_formats

    def _parse_value(self, raw_data, default):
        result = None
        errors = []

        if raw_data is None:
            if not self.is_nullable:
                errors.append('No value specified.')

            result = default
        else:
            for date_format in self.date_formats:
                try:
                    result = datetime.strptime(raw_data, date_format).date()
                    break
                except ValueError:
                    pass

            if result is None:
                errors.append(f'Invalid value ({raw_data}).')

        if (result is None) and (not self.is_nullable):
            result = default

        return result, errors

    def _parse_filter(self, raw_data, default):
        result = None
        errors = []

        if raw_data is None:
            result = default
        else:
            for date_format in self.date_formats:
                try:
                    result = datetime.strptime(raw_data, date_format).date()
                    break
                except ValueError:
                    pass

            if result is None:
                errors.append(f'Invalid value ({raw_data}).')

        if (result is None) and (not self.is_nullable):
            result = default

        return result, errors

    def _validate_item_update(self, form_raw_data):
        default_dict = self.default_item_update() if callable(self.default_item_update) else self.default_item_update
        default_value = self.avg_value if default_dict is None else default_dict.get('value', self.avg_value)
        value_result, value_errors = self._parse_value(form_raw_data.get(self.name), default_value)

        return {'value': value_result}, {'value': value_errors}

    def _validate_list_filter(self, form_raw_data):
        default_dict = self.default_list_filter() if callable(self.default_list_filter) else self.default_list_filter
        default_lower = self.min_value if default_dict is None else default_dict.get('lower', self.min_value)
        default_upper = self.max_value if default_dict is None else default_dict.get('upper', self.max_value)

        lower_result, lower_errors = self._parse_filter(form_raw_data.get(self.name + ':lower'), default_lower)
        upper_result, upper_errors = self._parse_filter(form_raw_data.get(self.name + ':upper'), default_upper)

        return {'lower': lower_result, 'upper': upper_result}, {'lower': lower_errors, 'upper': upper_errors}


class DateTimeWidget(NullableWidgetBase): # pylint: disable=R0903
    def __init__(
            self,
            min_value=datetime.min,
            max_value=datetime.max,
            date_formats=(
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%Y.%m.%d'),
            time_formats=(
                '%H:%M:%S',
                '%H:%M'),
            **kwargs):
        super().__init__('widgets_date', 'datetime', **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.avg_value = min_value + (max_value - min_value) / 2
        self.date_formats = date_formats
        self.time_formats = time_formats

    def _parse_value(self, raw_data_date, raw_data_time, default):
        result_date = None
        result_time = None
        errors = []

        if (raw_data_date is None) or (raw_data_time is None):
            if not self.is_nullable:
                errors.append('No value specified.')

            result = default
        else:
            for date_format in self.date_formats:
                try:
                    result_date = datetime.strptime(raw_data_date, date_format).date()
                    break
                except ValueError:
                    pass

            if result_date is None:
                errors.append(f'Invalid value ({raw_data_date}).')

            for date_format in self.time_formats:
                try:
                    result_time = datetime.strptime(raw_data_time, date_format).time()
                    break
                except ValueError:
                    pass

            if result_time is None:
                errors.append(f'Invalid value ({raw_data_time}).')

        if not ((result_date is None) or (result_time is None)):
            result = datetime.combine(result_date, result_time)

        if (result is None) and (not self.is_nullable):
            result = default

        return result, errors

    def _parse_filter(self, raw_data_date, raw_data_time, default):
        result_date = None
        result_time = None
        errors = []

        if (raw_data_date is None) or (raw_data_time is None):
            result = default
        else:
            for date_format in self.date_formats:
                try:
                    result_date = datetime.strptime(raw_data_date, date_format).date()
                    break
                except ValueError:
                    pass

            if result_date is None:
                errors.append(f'Invalid value ({raw_data_date}).')

            for date_format in self.time_formats:
                try:
                    result_time = datetime.strptime(raw_data_time, date_format).time()
                    break
                except ValueError:
                    pass

            if result_time is None:
                errors.append(f'Invalid value ({raw_data_time}).')

        if not ((result_date is None) or (result_time is None)):
            result = datetime.combine(result_date, result_time)

        if (result is None) and (not self.is_nullable):
            result = default

        return result, errors

    def _validate_item_update(self, form_raw_data):
        default_dict = self.default_item_update() if callable(self.default_item_update) else self.default_item_update
        default_value = self.avg_value if default_dict is None else default_dict.get('value', self.avg_value)
        value_result, value_errors = self._parse_value(
            form_raw_data.get(self.name + ':date'),
            form_raw_data.get(self.name + ':time'),
            default_value)

        return {'value': value_result}, {'value': value_errors}

    def _validate_list_filter(self, form_raw_data):
        default_dict = self.default_list_filter() if callable(self.default_list_filter) else self.default_list_filter
        default_lower = self.min_value if default_dict is None else default_dict.get('lower', self.min_value)
        default_upper = self.max_value if default_dict is None else default_dict.get('upper', self.max_value)

        lower_result, lower_errors = self._parse_filter(
            form_raw_data.get(self.name + ':lower:date'),
            form_raw_data.get(self.name + ':lower:time'),
            default_lower)
        upper_result, upper_errors = self._parse_filter(
            form_raw_data.get(self.name + ':upper:date'),
            form_raw_data.get(self.name + ':upper:time'),
            default_upper)

        return {'lower': lower_result, 'upper': upper_result}, {'lower': lower_errors, 'upper': upper_errors}


class TimeWidget(NullableWidgetBase): # pylint: disable=R0903
    def __init__(
            self,
            min_value=time.min,
            max_value=time.max,
            time_formats=(
                '%H:%M:%S',
                '%H:%M'),
            **kwargs):
        super().__init__('widgets_date', 'time', **kwargs)
        self.min_value = min_value
        self.max_value = max_value

        avg_seconds = int(
            3600 * (self.min_value.hour + self.max_value.hour) +
            60 * (self.min_value.minute + self.max_value.minute) +
            (self.min_value.minute + self.max_value.minute) + 1) // 2

        self.avg_value = time(avg_seconds // 3600, (avg_seconds % 3600) // 60, avg_seconds % 60)
        self.time_formats = time_formats

    def _parse_value(self, raw_data, default):
        result = None
        errors = []

        if raw_data is None:
            if not self.is_nullable:
                errors.append('No value specified.')

            result = default
        else:
            for date_format in self.time_formats:
                try:
                    result = datetime.strptime(raw_data, date_format).time()
                    break
                except ValueError:
                    pass

            if result is None:
                errors.append(f'Invalid value ({raw_data}).')

        if (result is None) and (not self.is_nullable):
            result = default

        return result, errors

    def _parse_filter(self, raw_data, default):
        result = None
        errors = []

        if raw_data is None:
            result = default
        else:
            for date_format in self.time_formats:
                try:
                    result = datetime.strptime(raw_data, date_format).time()
                    break
                except ValueError:
                    pass

            if result is None:
                errors.append(f'Invalid value ({raw_data}).')

        if (result is None) and (not self.is_nullable):
            result = default

        return result, errors

    def _validate_item_update(self, form_raw_data):
        default_dict = self.default_item_update() if callable(self.default_item_update) else self.default_item_update
        default_value = self.avg_value if default_dict is None else default_dict.get('value', self.avg_value)
        value_result, value_errors = self._parse_value(form_raw_data.get(self.name), default_value)

        return {'value': value_result}, {'value': value_errors}

    def _validate_list_filter(self, form_raw_data):
        default_dict = self.default_list_filter() if callable(self.default_list_filter) else self.default_list_filter
        default_lower = self.min_value if default_dict is None else default_dict.get('lower', self.min_value)
        default_upper = self.max_value if default_dict is None else default_dict.get('upper', self.max_value)

        lower_result, lower_errors = self._parse_filter(form_raw_data.get(self.name + ':lower'), default_lower)
        upper_result, upper_errors = self._parse_filter(form_raw_data.get(self.name + ':upper'), default_upper)

        return {'lower': lower_result, 'upper': upper_result}, {'lower': lower_errors, 'upper': upper_errors}
